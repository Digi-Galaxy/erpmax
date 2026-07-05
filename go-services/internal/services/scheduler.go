package services

import (
	"database/sql"
	"fmt"
	"log"
	"sync"
	"time"

	"erpmax-go/internal/cache"
	"erpmax-go/internal/config"
)

type SchedulerService struct {
	db        *sql.DB
	cache     *cache.RedisCache
	tasks     map[string]*ScheduledTask
	mu        sync.RWMutex
	stopChan  chan struct{}
}

type ScheduledTask struct {
	ID          string                 `json:"id"`
	Name        string                 `json:"name"`
	Type        string                 `json:"type"` // report, cleanup, sync, notification
	Schedule    string                 `json:"schedule"` // cron-like: "*/5 * * * *" (every 5 min)
	Payload     map[string]interface{} `json:"payload"`
	Enabled     bool                   `json:"enabled"`
	LastRun     *time.Time             `json:"last_run,omitempty"`
	NextRun     time.Time              `json:"next_run"`
	RunCount    int                    `json:"run_count"`
	ErrorCount  int                    `json:"error_count"`
	LastError   string                 `json:"last_error,omitempty"`
}

type SchedulerConfig struct {
	Tasks []ScheduledTaskConfig `json:"tasks"`
}

type ScheduledTaskConfig struct {
	ID       string                 `json:"id"`
	Name     string                 `json:"name"`
	Type     string                 `json:"type"`
	Schedule string                 `json:"schedule"`
	Payload  map[string]interface{} `json:"payload"`
	Enabled  bool                   `json:"enabled"`
}

func NewSchedulerService(cfg *config.Config) *SchedulerService {
	db, err := sql.Open("mysql", fmt.Sprintf("%s:%s@tcp(%s:%d)/%s",
		cfg.DBUser, cfg.DBPassword, cfg.DBHost, cfg.DBPort, cfg.DBName))
	if err != nil {
		log.Fatalf("Failed to connect to database: %v", err)
	}

	redisCache := cache.NewRedisCache(cache.CacheConfig{
		Addr:     cfg.RedisAddr,
		Password: cfg.RedisPassword,
		DB:       cfg.RedisDB,
		TTL:      24 * time.Hour,
	})

	return &SchedulerService{
		db:       db,
		cache:    redisCache,
		tasks:    make(map[string]*ScheduledTask),
		stopChan: make(chan struct{}),
	}
}

// Start starts the scheduler
func (s *SchedulerService) Start() {
	log.Println("Starting scheduler service...")
	
	// Load default tasks
	s.loadDefaultTasks()
	
	// Start scheduler loop
	go s.run()
	
	log.Println("Scheduler service started")
}

// Stop stops the scheduler
func (s *SchedulerService) Stop() {
	close(s.stopChan)
	log.Println("Scheduler service stopped")
}

// AddTask adds a scheduled task
func (s *SchedulerService) AddTask(task ScheduledTask) {
	s.mu.Lock()
	defer s.mu.Unlock()
	
	s.tasks[task.ID] = &task
	log.Printf("Added scheduled task: %s", task.Name)
}

// RemoveTask removes a scheduled task
func (s *SchedulerService) RemoveTask(id string) {
	s.mu.Lock()
	defer s.mu.Unlock()
	
	delete(s.tasks, id)
	log.Printf("Removed scheduled task: %s", id)
}

// GetTask returns a scheduled task
func (s *SchedulerService) GetTask(id string) (*ScheduledTask, bool) {
	s.mu.RLock()
	defer s.mu.RUnlock()
	
	task, exists := s.tasks[id]
	return task, exists
}

// GetAllTasks returns all scheduled tasks
func (s *SchedulerService) GetAllTasks() []*ScheduledTask {
	s.mu.RLock()
	defer s.mu.RUnlock()
	
	var tasks []*ScheduledTask
	for _, task := range s.tasks {
		tasks = append(tasks, task)
	}
	return tasks
}

// EnableTask enables a scheduled task
func (s *SchedulerService) EnableTask(id string) {
	s.mu.Lock()
	defer s.mu.Unlock()
	
	if task, exists := s.tasks[id]; exists {
		task.Enabled = true
		log.Printf("Enabled scheduled task: %s", task.Name)
	}
}

// DisableTask disables a scheduled task
func (s *SchedulerService) DisableTask(id string) {
	s.mu.Lock()
	defer s.mu.Unlock()
	
	if task, exists := s.tasks[id]; exists {
		task.Enabled = false
		log.Printf("Disabled scheduled task: %s", task.Name)
	}
}

// RunTaskNow runs a task immediately
func (s *SchedulerService) RunTaskNow(id string) error {
	s.mu.RLock()
	task, exists := s.tasks[id]
	s.mu.RUnlock()
	
	if !exists {
		return fmt.Errorf("task not found: %s", id)
	}
	
	return s.executeTask(task)
}

func (s *SchedulerService) run() {
	ticker := time.NewTicker(1 * time.Minute)
	defer ticker.Stop()

	for {
		select {
		case <-s.stopChan:
			return
		case <-ticker.C:
			s.checkAndRunTasks()
		}
	}
}

func (s *SchedulerService) checkAndRunTasks() {
	s.mu.RLock()
	defer s.mu.RUnlock()

	now := time.Now()
	for _, task := range s.tasks {
		if task.Enabled && now.After(task.NextRun) {
			go s.executeTask(task)
			task.NextRun = s.calculateNextRun(task.Schedule)
		}
	}
}

func (s *SchedulerService) executeTask(task *ScheduledTask) error {
	log.Printf("Executing scheduled task: %s", task.Name)
	
	startTime := time.Now()
	now := time.Now()
	task.LastRun = &now

	var err error
	switch task.Type {
	case "report":
		err = s.executeReportTask(task)
	case "cleanup":
		err = s.executeCleanupTask(task)
	case "sync":
		err = s.executeSyncTask(task)
	case "notification":
		err = s.executeNotificationTask(task)
	case "cache_refresh":
		err = s.executeCacheRefreshTask(task)
	case "data_aggregation":
		err = s.executeDataAggregationTask(task)
	default:
		err = fmt.Errorf("unknown task type: %s", task.Type)
	}

	task.RunCount++
	if err != nil {
		task.ErrorCount++
		task.LastError = err.Error()
		log.Printf("Task %s failed: %v", task.Name, err)
	} else {
		log.Printf("Task %s completed in %v", task.Name, time.Since(startTime))
	}

	return err
}

func (s *SchedulerService) executeReportTask(task *ScheduledTask) error {
	reportType, _ := task.Payload["report_type"].(string)
	
	query := s.getReportQuery(reportType)
	_, err := s.db.Exec(query)
	return err
}

func (s *SchedulerService) executeCleanupTask(task *ScheduledTask) error {
	// Cleanup old logs
	days := 30
	if d, ok := task.Payload["days"].(float64); ok {
		days = int(d)
	}
	
	query := fmt.Sprintf(`
		DELETE FROM `+"`tabActivity Log`"+`
		WHERE timestamp < DATE_SUB(NOW(), INTERVAL %d DAY)
	`, days)
	
	_, err := s.db.Exec(query)
	return err
}

func (s *SchedulerService) executeSyncTask(task *ScheduledTask) error {
	// Sync data
	return nil
}

func (s *SchedulerService) executeNotificationTask(task *ScheduledTask) error {
	// Send notifications
	return nil
}

func (s *SchedulerService) executeCacheRefreshTask(task *ScheduledTask) error {
	if s.cache != nil {
		s.cache.Clear()
	}
	return nil
}

func (s *SchedulerService) executeDataAggregationTask(task *ScheduledTask) error {
	// Aggregate data
	return nil
}

func (s *SchedulerService) loadDefaultTasks() {
	defaultTasks := []ScheduledTask{
		{
			ID:       "cache_cleanup",
			Name:     "Cache Cleanup",
			Type:     "cache_refresh",
			Schedule: "*/30 * * * *", // Every 30 minutes
			Enabled:  true,
		},
		{
			ID:       "activity_log_cleanup",
			Name:     "Activity Log Cleanup",
			Type:     "cleanup",
			Schedule: "0 2 * * *", // Daily at 2 AM
			Payload:  map[string]interface{}{"days": 90},
			Enabled:  true,
		},
		{
			ID:       "report_refresh",
			Name:     "Report Cache Refresh",
			Type:     "report",
			Schedule: "0 */6 * * *", // Every 6 hours
			Enabled:  true,
		},
	}

	for _, task := range defaultTasks {
		task.NextRun = s.calculateNextRun(task.Schedule)
		s.tasks[task.ID] = &task
	}
}

func (s *SchedulerService) calculateNextRun(schedule string) time.Time {
	// Simplified - would parse cron expression in production
	return time.Now().Add(1 * time.Hour)
}

func (s *SchedulerService) getReportQuery(reportType string) string {
	switch reportType {
	case "trial_balance":
		return "SELECT 1" // Placeholder
	default:
		return "SELECT 1"
	}
}
