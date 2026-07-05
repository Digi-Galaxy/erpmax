package services

import (
	"database/sql"
	"fmt"
	"log"
	"time"

	"erpmax-go/internal/cache"
	"erpmax-go/internal/config"
)

type FormService struct {
	db    *sql.DB
	cache *cache.RedisCache
}

type FormRequest struct {
	Doctype string `json:"doctype"`
	Name    string `json:"name"`
}

type FormResponse struct {
	DocType     string                 `json:"doctype"`
	Name        string                 `json:"name"`
	Meta        FormMeta               `json:"meta"`
	Data        map[string]interface{} `json:"data"`
	Attachments []Attachment           `json:"attachments"`
	Comments    []Comment              `json:"comments"`
	Timeline    []TimelineEntry        `json:"timeline"`
	Cached      bool                   `json:"cached"`
	LoadTime    float64                `json:"load_time_ms"`
}

type FormMeta struct {
	Fields      []FieldMeta `json:"fields"`
	Permissions Permissions `json:"permissions"`
	Title       string      `json:"title"`
	Submittable bool        `json:"submittable"`
	IsTree      bool        `json:"is_tree"`
}

type Permissions struct {
	CanCreate bool `json:"can_create"`
	CanRead   bool `json:"can_read"`
	CanWrite  bool `json:"can_write"`
	CanSubmit bool `json:"can_submit"`
	CanCancel bool `json:"can_cancel"`
	CanDelete bool `json:"can_delete"`
}

type Attachment struct {
	Name    string `json:"name"`
	URL     string `json:"url"`
	Size    int64  `json:"size"`
	Type    string `json:"type"`
}

type Comment struct {
	Name      string    `json:"name"`
	Content   string    `json:"content"`
	Author    string    `json:"author"`
	Timestamp time.Time `json:"timestamp"`
	Type      string    `json:"type"`
}

type TimelineEntry struct {
	Name      string    `json:"name"`
	Action    string    `json:"action"`
	User      string    `json:"user"`
	Timestamp time.Time `json:"timestamp"`
}

func NewFormService(cfg *config.Config) *FormService {
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

	return &FormService{
		db:    db,
		cache: redisCache,
	}
}

// GetFormData returns form data for editing
func (s *FormService) GetFormData(req FormRequest) (*FormResponse, error) {
	start := time.Now()

	// Build cache key
	cacheKey := fmt.Sprintf("form:%s:%s", req.Doctype, req.Name)

	// Try cache
	var cached FormResponse
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

	// Get form metadata
	meta := s.getFormMeta(req.Doctype)

	// Get attachments
	attachments := s.getAttachments(req.Doctype, req.Name)

	// Get comments
	comments := s.getComments(req.Doctype, req.Name)

	// Get timeline
	timeline := s.getTimeline(req.Doctype, req.Name)

	response := &FormResponse{
		DocType:     req.Doctype,
		Name:        req.Name,
		Meta:        meta,
		Data:        docData,
		Attachments: attachments,
		Comments:    comments,
		Timeline:    timeline,
		Cached:      false,
		LoadTime:    float64(time.Since(start).Microseconds()) / 1000,
	}

	// Cache for 10 minutes
	if s.cache != nil {
		s.cache.Set(cacheKey, response, 10*time.Minute)
	}

	return response, nil
}

// InvalidateCache invalidates form cache
func (s *FormService) InvalidateCache(doctype, name string) {
	if s.cache != nil {
		s.cache.Delete(fmt.Sprintf("form:%s:%s", doctype, name))
	}
}

func (s *FormService) getDocumentData(doctype, name string) (map[string]interface{}, error) {
	tableName := "tab" + doctype
	query := fmt.Sprintf("SELECT * FROM %s WHERE name = ?", tableName)

	rows, err := s.db.Query(query, name)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	if !rows.Next() {
		return nil, fmt.Errorf("record not found")
	}

	columns, _ := rows.Columns()

	values := make([]interface{}, len(columns))
	valuePtrs := make([]interface{}, len(columns))
	for i := range values {
		valuePtrs[i] = &values[i]
	}

	if err := rows.Scan(valuePtrs...); err != nil {
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

func (s *FormService) getFormMeta(doctype string) FormMeta {
	// Get fields
	fields := s.getFields(doctype)

	// Get permissions
	permissions := s.getPermissions(doctype)

	// Get doctype info
	var title string
	var submittable, isTree bool
	s.db.QueryRow(`
		SELECT COALESCE(title_field, ''), is_submittable, is_tree
		FROM tabDocType WHERE name = ?
	`, doctype).Scan(&title, &submittable, &isTree)

	return FormMeta{
		Fields:      fields,
		Permissions: permissions,
		Title:       title,
		Submittable: submittable,
		IsTree:      isTree,
	}
}

func (s *FormService) getFields(doctype string) []FieldMeta {
	query := `
		SELECT fieldname, label, fieldtype, COALESCE(length, 0), 
		       COALESCE(options, ''), reqd, read_only, hidden
		FROM tabDocTypeField
		WHERE parent = ? 
		ORDER BY idx
	`

	rows, err := s.db.Query(query, doctype)
	if err != nil {
		return nil
	}
	defer rows.Close()

	var fields []FieldMeta
	for rows.Next() {
		var f FieldMeta
		var options string
		var reqd, readOnly, hidden int
		if err := rows.Scan(&f.Fieldname, &f.Label, &f.Fieldtype, &f.Width, &options, &reqd, &readOnly, &hidden); err == nil {
			f.Options = options
			f.Required = reqd == 1
			f.ReadOnly = readOnly == 1
			f.Hidden = hidden == 1
			fields = append(fields, f)
		}
	}

	return fields
}

func (s *FormService) getPermissions(doctype string) Permissions {
	// Simplified - would check user roles in production
	return Permissions{
		CanCreate: true,
		CanRead:   true,
		CanWrite:  true,
		CanSubmit: true,
		CanCancel: true,
		CanDelete: true,
	}
}

func (s *FormService) getAttachments(doctype, docName string) []Attachment {
	query := `
		SELECT name, file_url, COALESCE(file_size, 0), file_name
		FROM tabFile
		WHERE attached_to_doctype = ? AND attached_to_name = ?
		ORDER BY modified DESC
	`

	rows, err := s.db.Query(query, doctype, docName)
	if err != nil {
		return nil
	}
	defer rows.Close()

	var attachments []Attachment
	for rows.Next() {
		var a Attachment
		if err := rows.Scan(&a.Name, &a.URL, &a.Size, &a.Type); err == nil {
			attachments = append(attachments, a)
		}
	}

	return attachments
}

func (s *FormService) getComments(doctype, docName string) []Comment {
	query := `
		SELECT name, content, owner, modified, comment_type
		FROM tabComment
		WHERE reference_doctype = ? AND reference_name = ?
		ORDER BY modified DESC
		LIMIT 20
	`

	rows, err := s.db.Query(query, doctype, docName)
	if err != nil {
		return nil
	}
	defer rows.Close()

	var comments []Comment
	for rows.Next() {
		var c Comment
		if err := rows.Scan(&c.Name, &c.Content, &c.Author, &c.Timestamp, &c.Type); err == nil {
			comments = append(comments, c)
		}
	}

	return comments
}

func (s *FormService) getTimeline(doctype, docName string) []TimelineEntry {
	query := `
		SELECT name, action, user, timestamp
		FROM tabActivity Log
		WHERE doc_type = ? AND doc_name = ?
		ORDER BY timestamp DESC
		LIMIT 20
	`

	rows, err := s.db.Query(query, doctype, docName)
	if err != nil {
		return nil
	}
	defer rows.Close()

	var timeline []TimelineEntry
	for rows.Next() {
		var t TimelineEntry
		if err := rows.Scan(&t.Name, &t.Action, &t.User, &t.Timestamp); err == nil {
			timeline = append(timeline, t)
		}
	}

	return timeline
}

func (s *FormService) getChildTables(doctype string) []string {
	query := `
		SELECT name FROM tabDocType
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

func (s *FormService) getChildData(childDoctype, parentName string) []map[string]interface{} {
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
