package services

import (
	"database/sql"
	"encoding/json"
	"fmt"
	"log"
	"sync"
	"time"

	"erpmax-go/internal/config"
)

type JobService struct {
	db        *sql.DB
	jobs      map[string]*Job
	mu        sync.RWMutex
	jobQueue  chan *Job
	resultMap map[string]*JobResult
}

type Job struct {
	ID          string                 `json:"id"`
	Type        string                 `json:"type"` // report, bulk_operation, sync, notification
	Status      string                 `json:"status"` // pending, running, completed, failed
	Priority    int                    `json:"priority"` // 1-10, higher = more priority
	Payload     map[string]interface{} `json:"payload"`
	Result      *JobResult            `json:"result,omitempty"`
	Error       string                 `json:"error,omitempty"`
	CreatedAt   time.Time             `json:"created_at"`
	StartedAt   *time.Time            `json:"started_at,omitempty"`
	CompletedAt *time.Time            `json:"completed_at,omitempty"`
	RetryCount  int                    `json:"retry_count"`
	MaxRetries  int                    `json:"max_retries"`
}

type JobResult struct {
	Success bool        `json:"success"`
	Data    interface{} `json:"data"`
	Error   string      `json:"error,omitempty"`
}

type JobRequest struct {
	Type       string                 `json:"type"`
	Priority   int                    `json:"priority"`
	Payload    map[string]interface{} `json:"payload"`
	MaxRetries int                    `json:"max_retries"`
}

func NewJobService(cfg *config.Config) *JobService {
	db, err := sql.Open("mysql", fmt.Sprintf("%s:%s@tcp(%s:%d)/%s",
		cfg.DBUser, cfg.DBPassword, cfg.DBHost, cfg.DBPort, cfg.DBName))
	if err != nil {
		log.Fatalf("Failed to connect to database: %v", err)
	}

	return &JobService{
		db:        db,
		jobs:      make(map[string]*Job),
		jobQueue:  make(chan *Job, 1000),
		resultMap: make(map[string]*JobResult),
	}
}

// CreateJob creates a new background job
func (s *JobService) CreateJob(req JobRequest) *Job {
	job := &Job{
		ID:         generateJobID(),
		Type:       req.Type,
		Status:     "pending",
		Priority:   req.Priority,
		Payload:    req.Payload,
		CreatedAt:  time.Now(),
		RetryCount: 0,
		MaxRetries: req.MaxRetries,
	}

	if job.MaxRetries == 0 {
		job.MaxRetries = 3
	}

	s.mu.Lock()
	s.jobs[job.ID] = job
	s.mu.Unlock()

	// Add to queue
	s.jobQueue <- job

	log.Printf("Job created: %s (type: %s, priority: %d)", job.ID, job.Type, job.Priority)
	return job
}

// GetJob returns job status
func (s *JobService) GetJob(id string) (*Job, bool) {
	s.mu.RLock()
	defer s.mu.RUnlock()
	job, exists := s.jobs[id]
	return job, exists
}

// ProcessJob processes a single job
func (s *JobService) ProcessJob(job *Job) {
	startTime := time.Now()
	job.StartedAt = &startTime
	job.Status = "running"

	var result *JobResult
	var err error

	switch job.Type {
	case "report":
		result, err = s.processReportJob(job)
	case "bulk_delete":
		result, err = s.processBulkDeleteJob(job)
	case "bulk_update":
		result, err = s.processBulkUpdateJob(job)
	case "sync":
		result, err = s.processSyncJob(job)
	case "notification":
		result, err = s.processNotificationJob(job)
	case "aggregation":
		result, err = s.processAggregationJob(job)
	default:
		err = fmt.Errorf("unknown job type: %s", job.Type)
	}

	completedTime := time.Now()
	job.CompletedAt = &completedTime

	if err != nil {
		job.Status = "failed"
		job.Error = err.Error()
		job.RetryCount++

		// Retry if under max retries
		if job.RetryCount < job.MaxRetries {
			job.Status = "pending"
			job.StartedAt = nil
			job.CompletedAt = nil
			s.jobQueue <- job
			log.Printf("Job %s failed, retrying (%d/%d): %v", job.ID, job.RetryCount, job.MaxRetries, err)
			return
		}
	} else {
		job.Status = "completed"
		job.Result = result
	}

	s.mu.Lock()
	s.jobs[job.ID] = job
	s.mu.Unlock()

	log.Printf("Job %s completed with status: %s", job.ID, job.Status)
}

// processReportJob handles report generation
func (s *JobService) processReportJob(job *Job) (*JobResult, error) {
	reportType, _ := job.Payload["report_type"].(string)
	filtersJSON, _ := json.Marshal(job.Payload["filters"])

	// Execute report query
	query := s.buildReportQuery(reportType, job.Payload)
	rows, err := s.db.Query(query)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	// Process results
	var data []map[string]interface{}
	columns, _ := rows.Columns()

	for rows.Next() {
		values := make([]interface{}, len(columns))
		valuePtrs := make([]interface{}, len(columns))
		for i := range values {
			valuePtrs[i] = &values[i]
		}

		if err := rows.Scan(valuePtrs...); err != nil {
			continue
		}

		row := make(map[string]interface{})
		for i, col := range columns {
			row[col] = values[i]
		}
		data = append(data, row)
	}

	return &JobResult{
		Success: true,
		Data: map[string]interface{}{
			"report_type": reportType,
			"filters":     string(filtersJSON),
			"rows":        data,
			"count":       len(data),
		},
	}, nil
}

// processBulkDeleteJob handles bulk deletion
func (s *JobService) processBulkDeleteJob(job *Job) (*JobResult, error) {
	doctype, _ := job.Payload["doctype"].(string)
	filters, _ := job.Payload["filters"].(map[string]interface{})

	tableName := doctypeToTable(doctype)
	query := fmt.Sprintf("DELETE FROM %s WHERE 1=1", tableName)
	args := []interface{}{}

	for key, value := range filters {
		query += fmt.Sprintf(" AND %s = ?", key)
		args = append(args, value)
	}

	result, err := s.db.Exec(query, args...)
	if err != nil {
		return nil, err
	}

	affected, _ := result.RowsAffected()
	return &JobResult{
		Success: true,
		Data: map[string]interface{}{
			"deleted": affected,
		},
	}, nil
}

// processBulkUpdateJob handles bulk updates
func (s *JobService) processBulkUpdateJob(job *Job) (*JobResult, error) {
	doctype, _ := job.Payload["doctype"].(string)
	filters, _ := job.Payload["filters"].(map[string]interface{})
	values, _ := job.Payload["values"].(map[string]interface{})

	tableName := doctypeToTable(doctype)
	setClause := ""
	args := []interface{}{}

	for key, value := range values {
		if setClause != "" {
			setClause += ", "
		}
		setClause += fmt.Sprintf("%s = ?", key)
		args = append(args, value)
	}

	for key, value := range filters {
		args = append(args, value)
	}

	query := fmt.Sprintf("UPDATE %s SET %s WHERE 1=1", tableName, setClause)
	for key := range filters {
		query += fmt.Sprintf(" AND %s = ?", key)
	}

	result, err := s.db.Exec(query, args...)
	if err != nil {
		return nil, err
	}

	affected, _ := result.RowsAffected()
	return &JobResult{
		Success: true,
		Data: map[string]interface{}{
			"updated": affected,
		},
	}, nil
}

// processSyncJob handles data synchronization
func (s *JobService) processSyncJob(job *Job) (*JobResult, error) {
	// Sync logic here
	return &JobResult{
		Success: true,
		Data:    map[string]interface{}{"synced": true},
	}, nil
}

// processNotificationJob handles notifications
func (s *JobService) processNotificationJob(job *Job) (*JobResult, error) {
	// Notification logic here
	return &JobResult{
		Success: true,
		Data:    map[string]interface{}{"sent": true},
	}, nil
}

// processAggregationJob handles data aggregation
func (s *JobService) processAggregationJob(job *Job) (*JobResult, error) {
	// Aggregation logic here
	return &JobResult{
		Success: true,
		Data:    map[string]interface{}{"aggregated": true},
	}, nil
}

func (s *JobService) buildReportQuery(reportType string, payload map[string]interface{}) string {
	// Build query based on report type
	switch reportType {
	case "trial_balance":
		return "SELECT account, SUM(debit) as debit, SUM(credit) as credit FROM tabGLEntry WHERE is_cancelled = 0 GROUP BY account"
	case "sales_summary":
		return "SELECT customer, SUM(grand_total) as total FROM tabSalesInvoice WHERE docstatus = 1 GROUP BY customer"
	default:
		return "SELECT * FROM tabGLEntry LIMIT 100"
	}
}

// GetQueueSize returns current queue size
func (s *JobService) GetQueueSize() int {
	return len(s.jobQueue)
}

// GetPendingJobs returns all pending jobs
func (s *JobService) GetPendingJobs() []*Job {
	s.mu.RLock()
	defer s.mu.RUnlock()

	var pending []*Job
	for _, job := range s.jobs {
		if job.Status == "pending" {
			pending = append(pending, job)
		}
	}
	return pending
}

func generateJobID() string {
	return fmt.Sprintf("job_%d", time.Now().UnixNano())
}
