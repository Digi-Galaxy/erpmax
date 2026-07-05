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

type CacheService struct {
	db        *sql.DB
	cache     map[string]*CacheEntry
	mu        sync.RWMutex
	ttl       time.Duration
	hitCount  int64
	missCount int64
}

type CacheEntry struct {
	Key       string      `json:"key"`
	Value     interface{} `json:"value"`
	ExpiresAt time.Time   `json:"expires_at"`
	CreatedAt time.Time   `json:"created_at"`
}

type CacheStats struct {
	HitCount   int64   `json:"hit_count"`
	MissCount  int64   `json:"miss_count"`
	HitRate    float64 `json:"hit_rate"`
	EntryCount int     `json:"entry_count"`
	MemoryUsed string  `json:"memory_used"`
}

func NewCacheService(cfg *config.Config) *CacheService {
	db, err := sql.Open("mysql", fmt.Sprintf("%s:%s@tcp(%s:%d)/%s",
		cfg.DBUser, cfg.DBPassword, cfg.DBHost, cfg.DBPort, cfg.DBName))
	if err != nil {
		log.Fatalf("Failed to connect to database: %v", err)
	}

	service := &CacheService{
		db:    db,
		cache: make(map[string]*CacheEntry),
		ttl:   time.Duration(cfg.CacheTTL) * time.Second,
	}

	// Start cleanup goroutine
	go service.cleanupLoop()

	return service
}

// Get retrieves value from cache
func (s *CacheService) Get(key string) (interface{}, bool) {
	s.mu.RLock()
	entry, exists := s.cache[key]
	s.mu.RUnlock()

	if !exists {
		s.missCount++
		return nil, false
	}

	if time.Now().After(entry.ExpiresAt) {
		s.mu.Lock()
		delete(s.cache, key)
		s.mu.Unlock()
		s.missCount++
		return nil, false
	}

	s.hitCount++
	return entry.Value, true
}

// Set adds value to cache
func (s *CacheService) Set(key string, value interface{}, ttl ...time.Duration) {
	s.mu.Lock()
	defer s.mu.Unlock()

	duration := s.ttl
	if len(ttl) > 0 {
		duration = ttl[0]
	}

	s.cache[key] = &CacheEntry{
		Key:       key,
		Value:     value,
		ExpiresAt: time.Now().Add(duration),
		CreatedAt: time.Now(),
	}
}

// Delete removes value from cache
func (s *CacheService) Delete(key string) {
	s.mu.Lock()
	delete(s.cache, key)
	s.mu.Unlock()
}

// Clear removes all cache entries
func (s *CacheService) Clear() {
	s.mu.Lock()
	s.cache = make(map[string]*CacheEntry)
	s.mu.Unlock()
}

// GetOrSet retrieves from cache or executes function and caches result
func (s *CacheService) GetOrSet(key string, fn func() (interface{}, error), ttl ...time.Duration) (interface{}, error) {
	if value, exists := s.Get(key); exists {
		return value, nil
	}

	value, err := fn()
	if err != nil {
		return nil, err
	}

	s.Set(key, value, ttl...)
	return value, nil
}

// GetStats returns cache statistics
func (s *CacheService) GetStats() CacheStats {
	s.mu.RLock()
	defer s.mu.RUnlock()

	totalRequests := s.hitCount + s.missCount
	var hitRate float64
	if totalRequests > 0 {
		hitRate = float64(s.hitCount) / float64(totalRequests) * 100
	}

	return CacheStats{
		HitCount:   s.hitCount,
		MissCount:  s.missCount,
		HitRate:    hitRate,
		EntryCount: len(s.cache),
		MemoryUsed: s.estimateMemory(),
	}
}

// PreloadReport caches commonly used report data
func (s *CacheService) PreloadReport(reportType string, filters map[string]interface{}) error {
	cacheKey := s.buildCacheKey(reportType, filters)

	// Check if already cached
	if _, exists := s.Get(cacheKey); exists {
		return nil
	}

	// Load data from database
	data, err := s.loadReportData(reportType, filters)
	if err != nil {
		return err
	}

	// Cache with longer TTL for reports
	s.Set(cacheKey, data, 30*time.Minute)
	return nil
}

// InvalidateReport removes cached report data
func (s *CacheService) InvalidateReport(reportType string) {
	s.mu.Lock()
	defer s.mu.Unlock()

	for key := range s.cache {
		if len(key) > len(reportType) && key[:len(reportType)] == reportType {
			delete(s.cache, key)
		}
	}
}

// InvalidateDoctype removes all cache entries for a doctype
func (s *CacheService) InvalidateDoctype(doctype string) {
	s.mu.Lock()
	defer s.mu.Unlock()

	for key := range s.cache {
		if contains(key, doctype) {
			delete(s.cache, key)
		}
	}
}

func (s *CacheService) cleanupLoop() {
	ticker := time.NewTicker(1 * time.Minute)
	defer ticker.Stop()

	for range ticker.C {
		s.cleanup()
	}
}

func (s *CacheService) cleanup() {
	s.mu.Lock()
	defer s.mu.Unlock()

	now := time.Now()
	for key, entry := range s.cache {
		if now.After(entry.ExpiresAt) {
			delete(s.cache, key)
		}
	}
}

func (s *CacheService) buildCacheKey(reportType string, filters map[string]interface{}) string {
	filtersJSON, _ := json.Marshal(filters)
	return fmt.Sprintf("%s:%s", reportType, string(filtersJSON))
}

func (s *CacheService) loadReportData(reportType string, filters map[string]interface{}) (interface{}, error) {
	// Load data from database based on report type
	query := s.buildQuery(reportType, filters)
	rows, err := s.db.Query(query)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

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

	return data, nil
}

func (s *CacheService) buildQuery(reportType string, filters map[string]interface{}) string {
	switch reportType {
	case "trial_balance":
		return "SELECT account, SUM(debit) as debit, SUM(credit) as credit FROM tabGLEntry WHERE is_cancelled = 0 GROUP BY account"
	case "sales_summary":
		return "SELECT customer, SUM(grand_total) as total FROM tabSalesInvoice WHERE docstatus = 1 GROUP BY customer"
	default:
		return "SELECT * FROM tabGLEntry LIMIT 100"
	}
}

func (s *CacheService) estimateMemory() string {
	// Rough estimate of memory usage
	entrySize := 200 // bytes per entry estimate
	totalBytes := len(s.cache) * entrySize
	
	if totalBytes > 1024*1024 {
		return fmt.Sprintf("%.2f MB", float64(totalBytes)/(1024*1024))
	}
	return fmt.Sprintf("%.2f KB", float64(totalBytes)/1024)
}

func contains(s, substr string) bool {
	return len(s) >= len(substr) && (s == substr || len(s) > 0 && containsSubstr(s, substr))
}

func containsSubstr(s, substr string) bool {
	for i := 0; i <= len(s)-len(substr); i++ {
		if s[i:i+len(substr)] == substr {
			return true
		}
	}
	return false
}
