package services

import (
	"database/sql"
	"fmt"
	"log"
	"strings"
	"time"

	"erpmax-go/internal/cache"
	"erpmax-go/internal/config"
)

type ListViewService struct {
	db    *sql.DB
	cache *cache.RedisCache
}

type ListViewRequest struct {
	Doctype    string                 `json:"doctype"`
	Fields     []string               `json:"fields"`
	Filters    map[string]interface{} `json:"filters"`
	OrderBy    string                 `json:"order_by"`
	PageLength int                    `json:"page_length"`
	Start      int                    `json:"start"`
	GroupBy    string                 `json:"group_by"`
}

type ListViewResponse struct {
	Data       []map[string]interface{} `json:"data"`
	Total      int                      `json:"total"`
	Fields     []FieldMeta              `json:"fields"`
	HasMore    bool                     `json:"has_more"`
	Cached     bool                     `json:"cached"`
	LoadTime   float64                  `json:"load_time_ms"`
}

type FieldMeta struct {
	Fieldname string `json:"fieldname"`
	Label     string `json:"label"`
	Fieldtype string `json:"fieldtype"`
	Width     int    `json:"width"`
	InList    bool   `json:"in_list_view"`
	Options   string `json:"options"`
	Required  bool   `json:"required"`
	ReadOnly  bool   `json:"read_only"`
	Hidden    bool   `json:"hidden"`
}

func NewListViewService(cfg *config.Config) *ListViewService {
	db, err := sql.Open("mysql", fmt.Sprintf("%s:%s@tcp(%s:%d)/%s",
		cfg.DBUser, cfg.DBPassword, cfg.DBHost, cfg.DBPort, cfg.DBName))
	if err != nil {
		log.Fatalf("Failed to connect to database: %v", err)
	}

	db.SetMaxOpenConns(50)
	db.SetMaxIdleConns(25)

	redisCache := cache.NewRedisCache(cache.CacheConfig{
		Addr:     cfg.RedisAddr,
		Password: cfg.RedisPassword,
		DB:       cfg.RedisDB,
		TTL:      time.Duration(cfg.CacheTTL) * time.Second,
	})

	return &ListViewService{
		db:    db,
		cache: redisCache,
	}
}

// GetListView returns paginated list data
func (s *ListViewService) GetListView(req ListViewRequest) (*ListViewResponse, error) {
	start := time.Now()

	// Build cache key
	cacheKey := s.buildCacheKey(req)

	// Try cache first
	var cached Response
	if s.cache != nil && s.cache.Get(cacheKey, &cached) {
		cached.Cached = true
		cached.LoadTime = float64(time.Since(start).Microseconds()) / 1000
		return &cached, nil
	}

	// Get field metadata
	fields := s.getFieldMetadata(req.Doctype)
	if len(req.Fields) == 0 {
		req.Fields = s.getDefaultFields(fields)
	}

	// Build query
	query, countQuery := s.buildQuery(req)

	// Get total count
	total := s.getCount(countQuery)

	// Get data
	data := s.executeQuery(query)

	// Build response
	response := &ListViewResponse{
		Data:       data,
		Total:      total,
		Fields:     fields,
		HasMore:    total > req.Start+req.PageLength,
		Cached:     false,
		LoadTime:   float64(time.Since(start).Microseconds()) / 1000,
	}

	// Cache for 5 minutes
	if s.cache != nil {
		s.cache.Set(cacheKey, response, 5*time.Minute)
	}

	return response, nil
}

// InvalidateCache invalidates cache for a doctype
func (s *ListViewService) InvalidateCache(doctype string) {
	if s.cache != nil {
		s.cache.DeletePattern(fmt.Sprintf("listview:%s:*", doctype))
	}
}

// RefreshCache refreshes cache for a doctype
func (s *ListViewService) RefreshCache(doctype string, filters map[string]interface{}) {
	s.InvalidateCache(doctype)
}

func (s *ListViewService) getFieldMetadata(doctype string) []FieldMeta {
	query := `
		SELECT 
			fieldname,
			label,
			fieldtype,
			COALESCE(length, 0) as width,
			CASE WHEN in_list_view = 1 THEN 1 ELSE 0 END as in_list
		FROM tabDocTypeField
		WHERE parent = ? AND fieldtype NOT IN ('Section Break', 'Column Break', 'Tab Break')
		ORDER BY idx
	`

	rows, err := s.db.Query(query, doctype)
	if err != nil {
		return nil
	}
	defer rows.Close()

	var fields []FieldMeta
	for rows.Next() {
		var field FieldMeta
		var inList int
		if err := rows.Scan(&field.Fieldname, &field.Label, &field.Fieldtype, &field.Width, &inList); err != nil {
			continue
		}
		field.InList = inList == 1
		if field.Width == 0 {
			field.Width = s.getDefaultWidth(field.Fieldtype)
		}
		fields = append(fields, field)
	}

	return fields
}

func (s *ListViewService) getDefaultFields(fields []FieldMeta) []string {
	var result []string
	for _, f := range fields {
		if f.InList || f.Fieldtype == "Link" || f.Fieldtype == "Data" || f.Fieldtype == "Currency" {
			result = append(result, f.Fieldname)
		}
	}
	if len(result) == 0 && len(fields) > 0 {
		for i := 0; i < 5 && i < len(fields); i++ {
			result = append(result, fields[i].FieldName)
		}
	}
	return result
}

func (s *ListViewService) buildQuery(req ListViewRequest) (string, string) {
	tableName := "tab" + req.Doctype
	fields := strings.Join(req.Fields, ", ")

	// Build WHERE clause
	whereClause := "1=1"
	args := []interface{}{}

	for key, value := range req.Filters {
		switch v := value.(type) {
		case []interface{}:
			if len(v) == 2 {
				// Handle operators like ["between", [start, end]]
				if operator, ok := v[0].(string); ok {
					switch operator {
					case "between":
						if rangeVals, ok := v[1].([]interface{}); ok && len(rangeVals) == 2 {
							whereClause += fmt.Sprintf(" AND %s BETWEEN ? AND ?", key)
							args = append(args, rangeVals[0], rangeVals[1])
						}
					case "like":
						whereClause += fmt.Sprintf(" AND %s LIKE ?", key)
						args = append(args, v[1])
					case "in":
						placeholders := ""
						if inVals, ok := v[1].([]interface{}); ok {
							for i, val := range inVals {
								if i > 0 {
									placeholders += ","
								}
								placeholders += "?"
								args = append(args, val)
							}
						}
						whereClause += fmt.Sprintf(" AND %s IN (%s)", key, placeholders)
					default:
						whereClause += fmt.Sprintf(" AND %s = ?", key)
						args = append(args, v)
					}
				}
			}
		default:
			whereClause += fmt.Sprintf(" AND %s = ?", key)
			args = append(args, value)
		}
	}

	// Build ORDER BY
	orderBy := req.OrderBy
	if orderBy == "" {
		orderBy = "modified DESC"
	}

	// Build queries
	query := fmt.Sprintf("SELECT %s FROM %s WHERE %s ORDER BY %s LIMIT ? OFFSET ?",
		fields, tableName, whereClause, orderBy)

	countQuery := fmt.Sprintf("SELECT COUNT(*) FROM %s WHERE %s", tableName, whereClause)

	return query, countQuery
}

func (s *ListViewService) getCount(query string) int {
	var count int
	s.db.QueryRow(query).Scan(&count)
	return count
}

func (s *ListViewService) executeQuery(query string, args ...interface{}) []map[string]interface{} {
	rows, err := s.db.Query(query, args...)
	if err != nil {
		return nil
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

	return result
}

func (s *ListViewService) buildCacheKey(req ListViewRequest) string {
	return fmt.Sprintf("listview:%s:%s:%d:%d", req.Doctype, fmt.Sprint(req.Filters), req.PageLength, req.Start)
}

func (s *ListViewService) getDefaultWidth(fieldtype string) int {
	switch fieldtype {
	case "Data", "Link", "Select":
		return 200
	case "Currency", "Int", "Float":
		return 120
	case "Date", "Datetime":
		return 100
	case "Check":
		return 80
	case "Text", "Small Text":
		return 300
	default:
		return 150
	}
}
