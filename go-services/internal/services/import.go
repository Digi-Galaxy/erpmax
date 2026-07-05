package services

import (
	"database/sql"
	"encoding/csv"
	"encoding/json"
	"fmt"
	"io"
	"log"
	"os"
	"path/filepath"
	"strings"
	"time"

	"erpmax-go/internal/cache"
	"erpmax-go/internal/config"
)

type ImportService struct {
	db        *sql.DB
	cache     *cache.RedisCache
	importDir string
}

type ImportRequest struct {
	Doctype   string   `json:"doctype"`
	FileURL   string   `json:"file_url"`
	Fields    []string `json:"fields"`
	Update    bool     `json:"update"` // Update existing records
	Overwrite bool     `json:"overwrite"`
}

type ImportResponse struct {
	JobID     string `json:"job_id"`
	Status    string `json:"status"`
	Total     int    `json:"total"`
	Imported  int    `json:"imported"`
	Updated   int    `json:"updated"`
	Skipped   int    `json:"skipped"`
	Failed    int    `json:"failed"`
	Errors    []ImportError `json:"errors,omitempty"`
	CreatedAt time.Time `json:"created_at"`
}

type ImportError struct {
	Row     int    `json:"row"`
	Error   string `json:"error"`
	Data    map[string]interface{} `json:"data,omitempty"`
}

type ImportJob struct {
	ID        string     `json:"id"`
	Doctype   string     `json:"doctype"`
	Status    string     `json:"status"`
	Total     int        `json:"total"`
	Imported  int        `json:"imported"`
	Updated   int        `json:"updated"`
	Skipped   int        `json:"skipped"`
	Failed    int        `json:"failed"`
	Errors    []ImportError `json:"errors,omitempty"`
	CreatedAt time.Time  `json:"created_at"`
	UpdatedAt time.Time  `json:"updated_at"`
}

func NewImportService(cfg *config.Config) *ImportService {
	db, err := sql.Open("mysql", fmt.Sprintf("%s:%s@tcp(%s:%d)/%s",
		cfg.DBUser, cfg.DBPassword, cfg.DBHost, cfg.DBPort, cfg.DBName))
	if err != nil {
		log.Fatalf("Failed to connect to database: %v", err)
	}

	db.SetMaxOpenConns(50)

	redisCache := cache.NewRedisCache(cache.CacheConfig{
		Addr:     cfg.RedisAddr,
		Password: cfg.RedisPassword,
		DB:       cfg.RedisDB,
		TTL:      1 * time.Hour,
	})

	importDir := "/tmp/erpmax/imports"
	os.MkdirAll(importDir, 0755)

	return &ImportService{
		db:        db,
		cache:     redisCache,
		importDir: importDir,
	}
}

// ImportData imports data from file
func (s *ImportService) ImportData(req ImportRequest) (*ImportResponse, error) {
	// Generate job ID
	jobID := fmt.Sprintf("import_%d", time.Now().UnixNano())

	// Read file
	fileData, err := os.ReadFile(req.FileURL)
	if err != nil {
		return nil, err
	}

	// Parse data
	var records []map[string]interface{}
	ext := filepath.Ext(req.FileURL)

	switch ext {
	case ".csv":
		records, err = s.parseCSV(fileData, req.Fields)
	case ".json":
		records, err = s.parseJSON(fileData)
	default:
		return nil, fmt.Errorf("unsupported file format: %s", ext)
	}

	if err != nil {
		return nil, err
	}

	// Create import job
	job := &ImportJob{
		ID:        jobID,
		Doctype:   req.Doctype,
		Status:    "processing",
		Total:     len(records),
		CreatedAt: time.Now(),
		UpdatedAt: time.Now(),
	}

	// Process import
	go s.processImport(job, req, records)

	return &ImportResponse{
		JobID:     jobID,
		Status:    "processing",
		Total:     len(records),
		CreatedAt: time.Now(),
	}, nil
}

// GetImportStatus returns import job status
func (s *ImportService) GetImportStatus(jobID string) (*ImportJob, error) {
	if s.cache != nil {
		var job ImportJob
		if s.cache.Get("import:"+jobID, &job) {
			return &job, nil
		}
	}
	return nil, fmt.Errorf("import job not found")
}

func (s *ImportService) processImport(job *ImportJob, req ImportRequest, records []map[string]interface{}) {
	tableName := "tab" + req.Doctype

	for i, record := range records {
		// Check if record exists
		name := fmt.Sprintf("%v", record["name"])
		
		if name != "" {
			exists := s.recordExists(tableName, name)
			
			if exists && !req.Update {
				job.Skipped++
				continue
			}
			
			if exists && req.Update {
				// Update record
				err := s.updateRecord(tableName, name, record)
				if err != nil {
					job.Errors = append(job.Errors, ImportError{
						Row:   i + 1,
						Error: err.Error(),
						Data:  record,
					})
					job.Failed++
				} else {
					job.Updated++
				}
			} else {
				// Insert record
				err := s.insertRecord(tableName, record)
				if err != nil {
					job.Errors = append(job.Errors, ImportError{
						Row:   i + 1,
						Error: err.Error(),
						Data:  record,
					})
					job.Failed++
				} else {
					job.Imported++
				}
			}
		} else {
			// Insert new record
			err := s.insertRecord(tableName, record)
			if err != nil {
				job.Errors = append(job.Errors, ImportError{
					Row:   i + 1,
					Error: err.Error(),
					Data:  record,
				})
				job.Failed++
			} else {
				job.Imported++
			}
		}

		// Update progress
		job.UpdatedAt = time.Now()
		s.cache.Set("import:"+job.ID, job, 1*time.Hour)
	}

	// Complete
	job.Status = "completed"
	job.UpdatedAt = time.Now()
	s.cache.Set("import:"+job.ID, job, 1*time.Hour)
}

func (s *ImportService) parseCSV(data []byte, fields []string) ([]map[string]interface{}, error) {
	reader := csv.NewReader(strings.NewReader(string(data)))
	
	// Read header
	header, err := reader.Read()
	if err != nil {
		return nil, err
	}

	// Use provided fields or header
	if len(fields) > 0 {
		header = fields
	}

	var records []map[string]interface{}
	for {
		record, err := reader.Read()
		if err == io.EOF {
			break
		}
		if err != nil {
			continue
		}

		row := make(map[string]interface{})
		for i, field := range header {
			if i < len(record) {
				row[field] = record[i]
			}
		}
		records = append(records, row)
	}

	return records, nil
}

func (s *ImportService) parseJSON(data []byte) ([]map[string]interface{}, error) {
	var records []map[string]interface{}
	if err := json.Unmarshal(data, &records); err != nil {
		return nil, err
	}
	return records, nil
}

func (s *ImportService) recordExists(tableName, name string) bool {
	var count int
	s.db.QueryRow(fmt.Sprintf("SELECT COUNT(*) FROM %s WHERE name = ?", tableName), name).Scan(&count)
	return count > 0
}

func (s *ImportService) insertRecord(tableName string, data map[string]interface{}) error {
	if len(data) == 0 {
		return fmt.Errorf("no data to insert")
	}

	fields := ""
	placeholders := ""
	args := []interface{}{}

	for key, value := range data {
		if fields != "" {
			fields += ", "
			placeholders += ", "
		}
		fields += key
		placeholders += "?"
		args = append(args, value)
	}

	query := fmt.Sprintf("INSERT INTO %s (%s) VALUES (%s)", tableName, fields, placeholders)
	_, err := s.db.Exec(query, args...)
	return err
}

func (s *ImportService) updateRecord(tableName, name string, data map[string]interface{}) error {
	if len(data) == 0 {
		return fmt.Errorf("no data to update")
	}

	setClause := ""
	args := []interface{}{}

	for key, value := range data {
		if key == "name" {
			continue
		}
		if setClause != "" {
			setClause += ", "
		}
		setClause += fmt.Sprintf("%s = ?", key)
		args = append(args, value)
	}

	args = append(args, name)
	query := fmt.Sprintf("UPDATE %s SET %s WHERE name = ?", tableName, setClause)
	_, err := s.db.Exec(query, args...)
	return err
}

// ValidateImport validates import data
func (s *ImportService) ValidateImport(doctype string, data []map[string]interface{}) ([]ImportError, error) {
	var errors []ImportError

	// Get required fields
	requiredFields := s.getRequiredFields(doctype)

	for i, record := range data {
		for _, field := range requiredFields {
			val, exists := record[field]
			if !exists || val == "" {
				errors = append(errors, ImportError{
					Row:   i + 1,
					Error: fmt.Sprintf("Required field '%s' is missing", field),
					Data:  record,
				})
			}
		}
	}

	return errors, nil
}

func (s *ImportService) getRequiredFields(doctype string) []string {
	query := `
		SELECT fieldname 
		FROM tabDocTypeField
		WHERE parent = ? AND reqd = 1
	`

	rows, err := s.db.Query(query, doctype)
	if err != nil {
		return nil
	}
	defer rows.Close()

	var fields []string
	for rows.Next() {
		var field string
		if err := rows.Scan(&field); err == nil {
			fields = append(fields, field)
		}
	}

	return fields
}
