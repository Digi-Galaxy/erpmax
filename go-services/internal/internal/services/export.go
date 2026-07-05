package services

import (
	"database/sql"
	"encoding/csv"
	"encoding/json"
	"fmt"
	"log"
	"os"
	"path/filepath"
	"time"

	"erpmax-go/internal/cache"
	"erpmax-go/internal/config"
)

type ExportService struct {
	db        *sql.DB
	cache     *cache.RedisCache
	exportDir string
}

type ExportRequest struct {
	Doctype   string                 `json:"doctype"`
	Filters   map[string]interface{} `json:"filters"`
	Fields    []string               `json:"fields"`
	Format    string                 `json:"format"` // csv, json, xlsx
	Name      string                 `json:"name"`
}

type ExportResponse struct {
	JobID     string `json:"job_id"`
	Status    string `json:"status"`
	FileName  string `json:"file_name"`
	FilePath  string `json:"file_path"`
	FileSize  int64  `json:"file_size"`
	CreatedAt time.Time `json:"created_at"`
}

type ExportJob struct {
	ID        string                 `json:"id"`
	Doctype   string                 `json:"doctype"`
	Filters   map[string]interface{} `json:"filters"`
	Fields    []string               `json:"fields"`
	Format    string                 `json:"format"`
	Status    string                 `json:"status"`
	Total     int                    `json:"total"`
	Processed int                    `json:"processed"`
	FilePath  string                 `json:"file_path"`
	FileSize  int64                  `json:"file_size"`
	Error     string                 `json:"error,omitempty"`
	CreatedAt time.Time             `json:"created_at"`
	UpdatedAt time.Time             `json:"updated_at"`
}

func NewExportService(cfg *config.Config) *ExportService {
	db, err := sql.Open("mysql", fmt.Sprintf("%s:%s@tcp(%s:%d)/%s",
		cfg.DBUser, cfg.DBPassword, cfg.DBHost, cfg.DBPort, cfg.DBName))
	if err != nil {
		log.Fatalf("Failed to connect to database: %v", err)
	}

	redisCache := cache.NewRedisCache(cache.CacheConfig{
		Addr:     cfg.RedisAddr,
		Password: cfg.RedisPassword,
		DB:       cfg.RedisDB,
		TTL:      1 * time.Hour,
	})

	exportDir := "/tmp/erpmax/exports"
	os.MkdirAll(exportDir, 0755)

	return &ExportService{
		db:        db,
		cache:     redisCache,
		exportDir: exportDir,
	}
}

// ExportData exports data in specified format
func (s *ExportService) ExportData(req ExportRequest) (*ExportResponse, error) {
	// Generate job ID
	jobID := fmt.Sprintf("export_%d", time.Now().UnixNano())

	// Count total records
	total, err := s.countRecords(req.Doctype, req.Filters)
	if err != nil {
		return nil, err
	}

	// Generate filename
	fileName := fmt.Sprintf("%s_%s.%s", req.Doctype, time.Now().Format("20060102_150405"), req.Format)
	filePath := filepath.Join(s.exportDir, fileName)

	// Create export job
	job := &ExportJob{
		ID:        jobID,
		Doctype:   req.Doctype,
		Filters:   req.Filters,
		Fields:    req.Fields,
		Format:    req.Format,
		Status:    "processing",
		Total:     total,
		FilePath:  filePath,
		CreatedAt: time.Now(),
		UpdatedAt: time.Now(),
	}

	// Process export
	go s.processExport(job, req)

	return &ExportResponse{
		JobID:     jobID,
		Status:    "processing",
		FileName:  fileName,
		FilePath:  filePath,
		CreatedAt: time.Now(),
	}, nil
}

// GetExportStatus returns export job status
func (s *ExportService) GetExportStatus(jobID string) (*ExportJob, error) {
	if s.cache != nil {
		var job ExportJob
		if s.cache.Get("export:"+jobID, &job) {
			return &job, nil
		}
	}
	return nil, fmt.Errorf("export job not found")
}

// GetExportFile returns export file
func (s *ExportService) GetExportFile(filePath string) ([]byte, string, error) {
	data, err := os.ReadFile(filePath)
	if err != nil {
		return nil, "", err
	}

	// Determine content type
	ext := filepath.Ext(filePath)
	contentType := "application/octet-stream"
	switch ext {
	case ".csv":
		contentType = "text/csv"
	case ".json":
		contentType = "application/json"
	case ".xlsx":
		contentType = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
	}

	return data, contentType, nil
}

// CleanupOldExports removes old export files
func (s *ExportService) CleanupOldExports() {
	threshold := time.Now().Add(-24 * time.Hour)

	filepath.Walk(s.exportDir, func(path string, info os.FileInfo, err error) error {
		if err != nil {
			return nil
		}
		if !info.IsDir() && info.ModTime().Before(threshold) {
			os.Remove(path)
		}
		return nil
	})
}

func (s *ExportService) processExport(job *ExportJob, req ExportRequest) {
	// Update status
	job.Status = "processing"
	job.UpdatedAt = time.Now()
	s.cache.Set("export:"+job.ID, job, 1*time.Hour)

	// Get data
	data, err := s.getExportData(req)
	if err != nil {
		job.Status = "failed"
		job.Error = err.Error()
		job.UpdatedAt = time.Now()
		s.cache.Set("export:"+job.ID, job, 1*time.Hour)
		return
	}

	// Write to file
	var fileSize int64
	switch req.Format {
	case "csv":
		fileSize, err = s.writeCSV(job.FilePath, req.Fields, data)
	case "json":
		fileSize, err = s.writeJSON(job.FilePath, data)
	}

	if err != nil {
		job.Status = "failed"
		job.Error = err.Error()
		job.UpdatedAt = time.Now()
		s.cache.Set("export:"+job.ID, job, 1*time.Hour)
		return
	}

	// Update job
	job.Status = "completed"
	job.Processed = len(data)
	job.FileSize = fileSize
	job.UpdatedAt = time.Now()
	s.cache.Set("export:"+job.ID, job, 1*time.Hour)
}

func (s *ExportService) getExportData(req ExportRequest) ([]map[string]interface{}, error) {
	tableName := "tab" + req.Doctype
	fields := "*"
	if len(req.Fields) > 0 {
		fields = ""
		for i, f := range req.Fields {
			if i > 0 {
				fields += ", "
			}
			fields += f
		}
	}

	query := fmt.Sprintf("SELECT %s FROM %s WHERE 1=1", fields, tableName)
	args := []interface{}{}

	for key, value := range req.Filters {
		query += fmt.Sprintf(" AND %s = ?", key)
		args = append(args, value)
	}

	query += " LIMIT 10000"

	rows, err := s.db.Query(query, args...)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	columns, _ := rows.Columns()
	var result []map[string]interface{}

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
			val := values[i]
			if b, ok := val.([]byte); ok {
				row[col] = string(b)
			} else {
				row[col] = val
			}
		}
		result = append(result, row)
	}

	return result, nil
}

func (s *ExportService) writeCSV(filePath string, fields []string, data []map[string]interface{}) (int64, error) {
	file, err := os.Create(filePath)
	if err != nil {
		return 0, err
	}
	defer file.Close()

	writer := csv.NewWriter(file)
	defer writer.Flush()

	// Write header
	if err := writer.Write(fields); err != nil {
		return 0, err
	}

	// Write data
	for _, row := range data {
		var record []string
		for _, field := range fields {
			val := fmt.Sprintf("%v", row[field])
			record = append(record, val)
		}
		if err := writer.Write(record); err != nil {
			return 0, err
		}
	}

	info, _ := file.Stat()
	return info.Size(), nil
}

func (s *ExportService) writeJSON(filePath string, data []map[string]interface{}) (int64, error) {
	file, err := os.Create(filePath)
	if err != nil {
		return 0, err
	}
	defer file.Close()

	encoder := json.NewEncoder(file)
	encoder.SetIndent("", "  ")
	if err := encoder.Encode(data); err != nil {
		return 0, err
	}

	info, _ := file.Stat()
	return info.Size(), nil
}

func (s *ExportService) countRecords(doctype string, filters map[string]interface{}) (int, error) {
	tableName := "tab" + doctype
	query := fmt.Sprintf("SELECT COUNT(*) FROM %s WHERE 1=1", tableName)
	args := []interface{}{}

	for key, value := range filters {
		query += fmt.Sprintf(" AND %s = ?", key)
		args = append(args, value)
	}

	var count int
	err := s.db.QueryRow(query, args...).Scan(&count)
	return count, err
}
