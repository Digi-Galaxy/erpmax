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

type SearchService struct {
	db    *sql.DB
	cache *cache.RedisCache
}

type SearchRequest struct {
	Query    string   `json:"query"`
	Doctypes []string `json:"doctypes"`
	Limit    int      `json:"limit"`
	Filters  map[string]interface{} `json:"filters"`
}

type SearchResponse struct {
	Results  []SearchResult `json:"results"`
	Total    int            `json:"total"`
	Cached   bool           `json:"cached"`
	LoadTime float64        `json:"load_time_ms"`
}

type SearchResult struct {
	Doctype   string `json:"doctype"`
	Name      string `json:"name"`
	Title     string `json:"title"`
	Subtitle  string `json:"subtitle"`
	Icon      string `json:"icon"`
	URL       string `json:"url"`
}

func NewSearchService(cfg *config.Config) *SearchService {
	db, err := sql.Open("mysql", fmt.Sprintf("%s:%s@tcp(%s:%d)/%s",
		cfg.DBUser, cfg.DBPassword, cfg.DBHost, cfg.DBPort, cfg.DBName))
	if err != nil {
		log.Fatalf("Failed to connect to database: %v", err)
	}

	db.SetMaxOpenConns(30)

	redisCache := cache.NewRedisCache(cache.CacheConfig{
		Addr:     cfg.RedisAddr,
		Password: cfg.RedisPassword,
		DB:       cfg.RedisDB,
		TTL:      10 * time.Minute,
	})

	return &SearchService{
		db:    db,
		cache: redisCache,
	}
}

// Search performs global search
func (s *SearchService) Search(req SearchRequest) (*SearchResponse, error) {
	start := time.Now()

	// Build cache key
	cacheKey := fmt.Sprintf("search:%s:%s", req.Query, strings.Join(req.Doctypes, ","))

	// Try cache
	var cached SearchResponse
	if s.cache != nil && s.cache.Get(cacheKey, &cached) {
		cached.Cached = true
		cached.LoadTime = float64(time.Since(start).Microseconds()) / 1000
		return &cached, nil
	}

	if req.Limit == 0 {
		req.Limit = 20
	}

	var results []SearchResult

	// Search each doctype
	for _, doctype := range req.Doctypes {
		doctypeResults := s.searchDoctype(doctype, req.Query, req.Limit)
		results = append(results, doctypeResults...)
	}

	// If no doctypes specified, search common ones
	if len(req.Doctypes) == 0 {
		defaultDoctypes := []string{
			"Customer", "Supplier", "Item", "Sales Invoice",
			"Purchase Invoice", "Payment Entry", "Journal Entry",
		}
		for _, doctype := range defaultDoctypes {
			doctypeResults := s.searchDoctype(doctype, req.Query, req.Limit)
			results = append(results, doctypeResults...)
		}
	}

	response := &SearchResponse{
		Results:  results,
		Total:    len(results),
		Cached:   false,
		LoadTime: float64(time.Since(start).Microseconds()) / 1000,
	}

	// Cache for 10 minutes
	if s.cache != nil {
		s.cache.Set(cacheKey, response, 10*time.Minute)
	}

	return response, nil
}

// Autocomplete returns quick suggestions
func (s *SearchService) Autocomplete(query string, doctype string, limit int) []SearchResult {
	if limit == 0 {
		limit = 10
	}

	return s.searchDoctype(doctype, query, limit)
}

func (s *SearchService) searchDoctype(doctype, query string, limit int) []SearchResult {
	tableName := "tab" + doctype

	// Get title field
	titleField := s.getTitleField(doctype)
	if titleField == "" {
		titleField = "name"
	}

	// Get subtitle field
	subtitleField := s.getSubtitleField(doctype)

	// Build query
	searchQuery := fmt.Sprintf(`
		SELECT name, %s
		FROM %s
		WHERE name LIKE ? OR %s LIKE ?
		LIMIT ?
	`, titleField, tableName, titleField)

	rows, err := s.db.Query(searchQuery, "%"+query+"%", "%"+query+"%", limit)
	if err != nil {
		return nil
	}
	defer rows.Close()

	var results []SearchResult
	for rows.Next() {
		var name, title string
		if err := rows.Scan(&name, &title); err != nil {
			continue
		}

		subtitle := ""
		if subtitleField != "" {
			s.db.QueryRow(fmt.Sprintf("SELECT %s FROM %s WHERE name = ?", subtitleField, tableName), name).Scan(&subtitle)
		}

		results = append(results, SearchResult{
			Doctype:  doctype,
			Name:     name,
			Title:    title,
			Subtitle: subtitle,
			Icon:     s.getDoctypeIcon(doctype),
			URL:      fmt.Sprintf("/app/%s/%s", strings.ToLower(doctype), name),
		})
	}

	return results
}

func (s *SearchService) getTitleField(doctype string) string {
	// Common title fields
	titleFields := map[string]string{
		"Customer":       "customer_name",
		"Supplier":       "supplier_name",
		"Item":           "item_name",
		"Sales Invoice":  "customer_name",
		"Purchase Invoice": "supplier_name",
		"Payment Entry":  "party",
		"Journal Entry":  "voucher_type",
	}

	if field, ok := titleFields[doctype]; ok {
		return field
	}

	// Try to get from metadata
	var fieldName string
	s.db.QueryRow(`
		SELECT fieldname 
		FROM tabDocTypeField 
		WHERE parent = ? AND fieldname LIKE '%name%' 
		LIMIT 1
	`, doctype).Scan(&fieldName)

	return fieldName
}

func (s *SearchService) getSubtitleField(doctype string) string {
	subtitleFields := map[string]string{
		"Customer":       "customer_group",
		"Supplier":       "supplier_group",
		"Item":           "item_group",
		"Sales Invoice":  "grand_total",
		"Purchase Invoice": "grand_total",
	}

	if field, ok := subtitleFields[doctype]; ok {
		return field
	}

	return ""
}

func (s *SearchService) getDoctypeIcon(doctype string) string {
	icons := map[string]string{
		"Customer":       "fa-user",
		"Supplier":       "fa-truck",
		"Item":           "fa-cube",
		"Sales Invoice":  "fa-file-text",
		"Purchase Invoice": "fa-file-text",
		"Payment Entry":  "fa-money",
		"Journal Entry":  "fa-book",
	}

	if icon, ok := icons[doctype]; ok {
		return icon
	}

	return "fa-file"
}
