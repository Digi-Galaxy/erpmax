package services

import (
	"database/sql"
	"fmt"
	"log"
	"time"

	"erpmax-go/internal/cache"
	"erpmax-go/internal/config"
)

type PrintService struct {
	db    *sql.DB
	cache *cache.RedisCache
}

type PrintRequest struct {
	Doctype      string `json:"doctype"`
	Name         string `json:"name"`
	PrintFormat  string `json:"print_format"`
	NoLetterhead bool   `json:"no_letterhead"`
}

type PrintResponse struct {
	HTML       string                 `json:"html"`
	CSS        string                 `json:"css"`
	DocData    map[string]interface{} `json:"doc_data"`
	Letterhead map[string]interface{} `json:"letterhead,omitempty"`
	Cached     bool                   `json:"cached"`
	LoadTime   float64                `json:"load_time_ms"`
}

func NewPrintService(cfg *config.Config) *PrintService {
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

	return &PrintService{
		db:    db,
		cache: redisCache,
	}
}

// GetPrintData returns document data for printing
func (s *PrintService) GetPrintData(req PrintRequest) (*PrintResponse, error) {
	start := time.Now()

	// Build cache key
	cacheKey := fmt.Sprintf("print:%s:%s:%s", req.Doctype, req.Name, req.PrintFormat)

	// Try cache
	var cached PrintResponse
	if s.cache != nil && s.cache.Get(cacheKey, &cached) {
		cached.Cached = true
		cached.LoadTime = float64(time.Since(start).Microseconds()) / 1000
		return &cached, nil
	}

	// Get document data
	docData, err := s.getDocumentData(req.Doctype, req.Name)
	if err != nil {
		return nil, err
	}

	// Get print format
	printFormat, css := s.getPrintFormat(req.Doctype, req.PrintFormat)

	// Get letterhead if needed
	var letterhead map[string]interface{}
	if !req.NoLetterhead {
		letterhead = s.getLetterhead(docData)
	}

	// Build HTML
	html := s.buildPrintHTML(docData, printFormat, letterhead)

	response := &PrintResponse{
		HTML:       html,
		CSS:        css,
		DocData:    docData,
		Letterhead: letterhead,
		Cached:     false,
		LoadTime:   float64(time.Since(start).Microseconds()) / 1000,
	}

	// Cache for 10 minutes
	if s.cache != nil {
		s.cache.Set(cacheKey, response, 10*time.Minute)
	}

	return response, nil
}

// GetBulkPrintData returns data for multiple documents
func (s *PrintService) GetBulkPrintData(doctype string, names []string, printFormat string) ([]PrintResponse, error) {
	var results []PrintResponse

	for _, name := range names {
		data, err := s.GetPrintData(PrintRequest{
			Doctype:     doctype,
			Name:        name,
			PrintFormat: printFormat,
		})
		if err != nil {
			continue
		}
		results = append(results, *data)
	}

	return results, nil
}

// InvalidateCache invalidates print cache
func (s *PrintService) InvalidateCache(doctype, name string) {
	if s.cache != nil {
		s.cache.DeletePattern(fmt.Sprintf("print:%s:%s:*", doctype, name))
	}
}

func (s *PrintService) getDocumentData(doctype, name string) (map[string]interface{}, error) {
	tableName := "tab" + doctype

	// Get all fields
	query := fmt.Sprintf("SELECT * FROM %s WHERE name = ?", tableName)
	row := s.db.QueryRow(query, name)

	columns, _ := row.Columns()
	values := make([]interface{}, len(columns))
	valuePtrs := make([]interface{}, len(columns))
	for i := range values {
		valuePtrs[i] = &values[i]
	}

	if err := row.Scan(valuePtrs...); err != nil {
		return nil, err
	}

	data := make(map[string]interface{})
	for i, col := range columns {
		val := values[i]
		if b, ok := val.([]byte); ok {
			data[col] = string(b)
		} else {
			data[col] = val
		}
	}

	// Get child tables
	childTables := s.getChildTables(doctype)
	for _, child := range childTables {
		childData := s.getChildData(child, name)
		data[child] = childData
	}

	return data, nil
}

func (s *PrintService) getChildTables(doctype string) []string {
	query := `
		SELECT name 
		FROM tabDocType 
		WHERE istable = 1 AND module = (
			SELECT module FROM tabDocType WHERE name = ?
		)
	`

	rows, err := s.db.Query(query, doctype)
	if err != nil {
		return nil
	}
	defer rows.Close()

	var tables []string
	for rows.Next() {
		var name string
		if err := rows.Scan(&name); err == nil {
			tables = append(tables, name)
		}
	}

	return tables
}

func (s *PrintService) getChildData(childDoctype, parentName string) []map[string]interface{} {
	tableName := "tab" + childDoctype
	query := fmt.Sprintf("SELECT * FROM %s WHERE parent = ? ORDER BY idx", tableName)

	rows, err := s.db.Query(query, parentName)
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

func (s *PrintService) getPrintFormat(doctype, printFormat string) (string, string) {
	if printFormat == "" {
		printFormat = "Standard"
	}

	query := `
		SELECT html, css 
		FROM tabPrintFormat 
		WHERE name = ? AND doc_type = ?
	`

	var html, css string
	s.db.QueryRow(query, printFormat, doctype).Scan(&html, &css)

	if html == "" {
		html = s.getDefaultPrintFormat(doctype)
	}

	return html, css
}

func (s *PrintService) getDefaultPrintFormat(doctype string) string {
	return fmt.Sprintf(`
		<div class="print-format">
			<h1>%s</h1>
			<div class="section">
				{{#each doc}}
				<div class="field">
					<label>{{@key}}:</label>
					<span>{{this}}</span>
				</div>
				{{/each}}
			</div>
		</div>
	`, doctype)
}

func (s *PrintService) getLetterhead(docData map[string]interface{}) map[string]interface{} {
	company, _ := docData["company"].(string)
	if company == "" {
		return nil
	}

	query := `
		SELECT name, image, footer 
		FROM tabLetter Head 
		WHERE company = ? AND is_default = 1
	`

	letterhead := make(map[string]interface{})
	s.db.QueryRow(query, company).Scan(
		&letterhead["name"],
		&letterhead["image"],
		&letterhead["footer"],
	)

	return letterhead
}

func (s *PrintService) buildPrintHTML(docData map[string]interface{}, printFormat string, letterhead map[string]interface{}) string {
	// Build HTML with data
	html := "<!DOCTYPE html><html><head>"
	html += "<meta charset='utf-8'>"
	html += "<style>/* Print styles */</style>"
	html += "</head><body>"

	// Add letterhead
	if letterhead != nil {
		if image, ok := letterhead["image"].(string); ok && image != "" {
			html += fmt.Sprintf("<div class='letterhead'><img src='%s'></div>", image)
		}
	}

	// Add content
	html += printFormat

	// Add footer
	if letterhead != nil {
		if footer, ok := letterhead["footer"].(string); ok && footer != "" {
			html += fmt.Sprintf("<div class='footer'>%s</div>", footer)
		}
	}

	html += "</body></html>"
	return html
}
