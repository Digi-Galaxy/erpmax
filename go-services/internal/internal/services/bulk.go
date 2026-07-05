package services

import (
	"database/sql"
	"encoding/json"
	"fmt"
	"log"
	"time"

	"erpmax-go/internal/config"
)

type BulkService struct {
	db        *sql.DB
	batchSize int
}

type BulkOperation struct {
	ID        string    `json:"id"`
	Doctype   string    `json:"doctype"`
	Action    string    `json:"action"` // delete, update, export
	Status    string    `json:"status"` // pending, running, completed, failed
	Total     int       `json:"total"`
	Processed int       `json:"processed"`
	Failed    int       `json:"failed"`
	StartedAt time.Time `json:"started_at"`
	EndedAt   time.Time `json:"ended_at"`
	Error     string    `json:"error,omitempty"`
}

type BulkDeleteRequest struct {
	Doctype   string            `json:"doctype"`
	Filters   map[string]interface{} `json:"filters"`
	DryRun    bool              `json:"dry_run"`
}

type BulkUpdateRequest struct {
	Doctype   string            `json:"doctype"`
	Filters   map[string]interface{} `json:"filters"`
	Values    map[string]interface{} `json:"values"`
	DryRun    bool              `json:"dry_run"`
}

type BulkExportRequest struct {
	Doctype   string            `json:"doctype"`
	Filters   map[string]interface{} `json:"filters"`
	Fields    []string          `json:"fields"`
	Format    string            `json:"format"` // csv, json, xlsx
}

func NewBulkService(cfg *config.Config) *BulkService {
	db, err := sql.Open("mysql", fmt.Sprintf("%s:%s@tcp(%s:%d)/%s",
		cfg.DBUser, cfg.DBPassword, cfg.DBHost, cfg.DBPort, cfg.DBName))
	if err != nil {
		log.Fatalf("Failed to connect to database: %v", err)
	}

	db.SetMaxOpenConns(25)
	db.SetMaxIdleConns(5)
	db.SetConnMaxLifetime(5 * time.Minute)

	return &BulkService{
		db:        db,
		batchSize: cfg.BatchSize,
	}
}

// BulkDelete deletes records in batches
func (s *BulkService) BulkDelete(req BulkDeleteRequest) (*BulkOperation, error) {
	op := &BulkOperation{
		ID:        generateID(),
		Doctype:   req.Doctype,
		Action:    "delete",
		Status:    "running",
		StartedAt: time.Now(),
	}

	// Count total records
	total, err := s.countRecords(req.Doctype, req.Filters)
	if err != nil {
		op.Status = "failed"
		op.Error = err.Error()
		return op, err
	}
	op.Total = total

	if req.DryRun {
		op.Status = "completed"
		op.EndedAt = time.Now()
		return op, nil
	}

	// Delete in batches
	tableName := doctypeToTable(req.Doctype)
	query := fmt.Sprintf("DELETE FROM %s WHERE 1=1", tableName)
	args := []interface{}{}

	// Add filters
	for key, value := range req.Filters {
		query += fmt.Sprintf(" AND %s = ?", key)
		args = append(args, value)
	}

	for op.Processed < total {
		batchQuery := query + fmt.Sprintf(" LIMIT %d", s.batchSize)
		result, err := s.db.Exec(batchQuery, args...)
		if err != nil {
			op.Status = "failed"
			op.Error = err.Error()
			return op, err
		}

		affected, _ := result.RowsAffected()
		op.Processed += int(affected)

		if affected == 0 {
			break
		}
	}

	op.Status = "completed"
	op.EndedAt = time.Now()
	return op, nil
}

// BulkUpdate updates records in batches
func (s *BulkService) BulkUpdate(req BulkUpdateRequest) (*BulkOperation, error) {
	op := &BulkOperation{
		ID:        generateID(),
		Doctype:   req.Doctype,
		Action:    "update",
		Status:    "running",
		StartedAt: time.Now(),
	}

	// Count total records
	total, err := s.countRecords(req.Doctype, req.Filters)
	if err != nil {
		op.Status = "failed"
		op.Error = err.Error()
		return op, err
	}
	op.Total = total

	if req.DryRun {
		op.Status = "completed"
		op.EndedAt = time.Now()
		return op, nil
	}

	// Build update query
	tableName := doctypeToTable(req.Doctype)
	setClause := ""
	args := []interface{}{}

	for key, value := range req.Values {
		if setClause != "" {
			setClause += ", "
		}
		setClause += fmt.Sprintf("%s = ?", key)
		args = append(args, value)
	}

	// Add filter args
	for _, value := range req.Filters {
		args = append(args, value)
	}

	query := fmt.Sprintf("UPDATE %s SET %s WHERE 1=1", tableName, setClause)
	for key := range req.Filters {
		query += fmt.Sprintf(" AND %s = ?", key)
	}

	// Update in batches
	for op.Processed < total {
		batchQuery := query + fmt.Sprintf(" LIMIT %d", s.batchSize)
		result, err := s.db.Exec(batchQuery, args...)
		if err != nil {
			op.Status = "failed"
			op.Error = err.Error()
			return op, err
		}

		affected, _ := result.RowsAffected()
		op.Processed += int(affected)

		if affected == 0 {
			break
		}
	}

	op.Status = "completed"
	op.EndedAt = time.Now()
	return op, nil
}

// BulkExport exports records
func (s *BulkService) BulkExport(req BulkExportRequest) ([]byte, string, error) {
	tableName := doctypeToTable(req.Doctype)
	fields := "*"
	if len(req.Fields) > 0 {
		fields = joinFields(req.Fields)
	}

	query := fmt.Sprintf("SELECT %s FROM %s WHERE 1=1", fields, tableName)
	args := []interface{}{}

	for key, value := range req.Filters {
		query += fmt.Sprintf(" AND %s = ?", key)
		args = append(args, value)
	}

	rows, err := s.db.Query(query, args...)
	if err != nil {
		return nil, "", err
	}
	defer rows.Close()

	// Get column names
	columns, _ := rows.Columns()

	// Build result
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

	// Convert to requested format
	switch req.Format {
	case "json":
		data, err := json.Marshal(result)
		return data, "application/json", err
	case "csv":
		data := convertToCSV(columns, result)
		return []byte(data), "text/csv", nil
	default:
		data, err := json.Marshal(result)
		return data, "application/json", err
	}
}

func (s *BulkService) countRecords(doctype string, filters map[string]interface{}) (int, error) {
	tableName := doctypeToTable(doctype)
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

func doctypeToTable(doctype string) string {
	// Convert DocType name to table name
	// e.g., "Sales Invoice" -> "tabSales Invoice"
	return "tab" + doctype
}

func joinFields(fields []string) string {
	result := ""
	for i, field := range fields {
		if i > 0 {
			result += ", "
		}
		result += field
	}
	return result
}

func convertToCSV(columns []string, data []map[string]interface{}) string {
	result := ""
	for i, col := range columns {
		if i > 0 {
			result += ","
		}
		result += fmt.Sprintf(`"%s"`, col)
	}
	result += "\n"

	for _, row := range data {
		for i, col := range columns {
			if i > 0 {
				result += ","
			}
			val := row[col]
			result += fmt.Sprintf(`"%v"`, val)
		}
		result += "\n"
	}

	return result
}

func generateID() string {
	return fmt.Sprintf("op_%d", time.Now().UnixNano())
}
