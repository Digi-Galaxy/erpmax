package services

import (
	"database/sql"
	"fmt"
	"io"
	"log"
	"net/http"
	"os"
	"path/filepath"
	"time"

	"erpmax-go/internal/cache"
	"erpmax-go/internal/config"
)

type FileService struct {
	db        *sql.DB
	cache     *cache.RedisCache
	uploadDir string
}

type FileRequest struct {
	FileURL  string `json:"file_url"`
	Doctype  string `json:"doctype"`
	DocName  string `json:"doc_name"`
}

type FileResponse struct {
	URL         string    `json:"url"`
	Name        string    `json:"name"`
	ContentType string    `json:"content_type"`
	Size        int64     `json:"size"`
	Content     []byte    `json:"-"`
	Cached      bool      `json:"cached"`
	LoadTime    float64   `json:"load_time_ms"`
}

type FileInfo struct {
	Name        string    `json:"name"`
	URL         string    `json:"url"`
	ContentType string    `json:"content_type"`
	Size        int64     `json:"size"`
	Modified    time.Time `json:"modified"`
}

func NewFileService(cfg *config.Config) *FileService {
	db, err := sql.Open("mysql", fmt.Sprintf("%s:%s@tcp(%s:%d)/%s",
		cfg.DBUser, cfg.DBPassword, cfg.DBHost, cfg.DBPort, cfg.DBName))
	if err != nil {
		log.Fatalf("Failed to connect to database: %v", err)
	}

	redisCache := cache.NewRedisCache(cache.CacheConfig{
		Addr:     cfg.RedisAddr,
		Password: cfg.RedisPassword,
		DB:       cfg.RedisDB,
		TTL:      30 * time.Minute,
	})

	uploadDir := cfg.UploadDir
	if uploadDir == "" {
		uploadDir = "/tmp/erpmax/files"
	}

	os.MkdirAll(uploadDir, 0755)

	return &FileService{
		db:        db,
		cache:     redisCache,
		uploadDir: uploadDir,
	}
}

// GetFile returns file content
func (s *FileService) GetFile(req FileRequest) (*FileResponse, error) {
	start := time.Now()

	// Build cache key
	cacheKey := fmt.Sprintf("file:%s", req.FileURL)

	// Try cache for metadata
	var cached FileResponse
	if s.cache != nil && s.cache.Get(cacheKey, &cached) {
		cached.Cached = true
		cached.LoadTime = float64(time.Since(start).Microseconds()) / 1000

		// Read file content
		content, err := os.ReadFile(filepath.Join(s.uploadDir, req.FileURL))
		if err == nil {
			cached.Content = content
		}

		return &cached, nil
	}

	// Get file info from database
	fileInfo := s.getFileInfo(req.FileURL)
	if fileInfo == nil {
		return nil, fmt.Errorf("file not found: %s", req.FileURL)
	}

	// Read file content
	content, err := os.ReadFile(filepath.Join(s.uploadDir, req.FileURL))
	if err != nil {
		return nil, err
	}

	response := &FileResponse{
		URL:         fileInfo.URL,
		Name:        fileInfo.Name,
		ContentType: fileInfo.ContentType,
		Size:        fileInfo.Size,
		Content:     content,
		Cached:      false,
		LoadTime:    float64(time.Since(start).Microseconds()) / 1000,
	}

	// Cache metadata
	if s.cache != nil {
		s.cache.Set(cacheKey, &FileResponse{
			URL:         response.URL,
			Name:        response.Name,
			ContentType: response.ContentType,
			Size:        response.Size,
		}, 30*time.Minute)
	}

	return response, nil
}

// GetFilesByDoc returns all files for a document
func (s *FileService) GetFilesByDoc(doctype, docName string) ([]FileInfo, error) {
	query := `
		SELECT 
			file_name,
			file_url,
			CASE 
			 WHEN file_name LIKE '%.jpg' OR file_name LIKE '%.jpeg' THEN 'image/jpeg'
			 WHEN file_name LIKE '%.png' THEN 'image/png'
			 WHEN file_name LIKE '%.pdf' THEN 'application/pdf'
			 WHEN file_name LIKE '%.doc%' THEN 'application/msword'
			 WHEN file_name LIKE '%.xls%' THEN 'application/vnd.ms-excel'
			 ELSE 'application/octet-stream'
			END as content_type,
			COALESCE(file_size, 0) as size,
			modified
		FROM tabFile
		WHERE attached_to_doctype = ? AND attached_to_name = ?
		ORDER BY modified DESC
	`

	rows, err := s.db.Query(query, doctype, docName)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var files []FileInfo
	for rows.Next() {
		var file FileInfo
		if err := rows.Scan(&file.Name, &file.URL, &file.ContentType, &file.Size, &file.Modified); err == nil {
			files = append(files, file)
		}
	}

	return files, nil
}

// UploadFile uploads a file
func (s *FileService) UploadFile(file io.Reader, filename string, doctype string, docName string) (*FileInfo, error) {
	// Generate unique filename
	uniqueName := fmt.Sprintf("%s_%d_%s", doctype, time.Now().UnixNano(), filename)
	filePath := filepath.Join(s.uploadDir, uniqueName)

	// Create file
	out, err := os.Create(filePath)
	if err != nil {
		return nil, err
	}
	defer out.Close()

	// Copy content
	written, err := io.Copy(out, file)
	if err != nil {
		return nil, err
	}

	// Save to database
	query := `
		INSERT INTO tabFile (file_name, file_url, attached_to_doctype, attached_to_name, file_size, owner)
		VALUES (?, ?, ?, ?, ?, ?)
	`

	_, err = s.db.Exec(query, filename, uniqueName, doctype, docName, written, "Administrator")
	if err != nil {
		os.Remove(filePath)
		return nil, err
	}

	return &FileInfo{
		Name: filename,
		URL:  uniqueName,
		Size: written,
	}, nil
}

// DeleteFile deletes a file
func (s *FileService) DeleteFile(fileURL string) error {
	// Delete from database
	query := "DELETE FROM tabFile WHERE file_url = ?"
	_, err := s.db.Exec(query, fileURL)
	if err != nil {
		return err
	}

	// Delete from filesystem
	filePath := filepath.Join(s.uploadDir, fileURL)
	os.Remove(filePath)

	// Invalidate cache
	if s.cache != nil {
		s.cache.Delete(fmt.Sprintf("file:%s", fileURL))
	}

	return nil
}

func (s *FileService) getFileInfo(fileURL string) *FileInfo {
	query := `
		SELECT 
			file_name,
			file_url,
			CASE 
			 WHEN file_name LIKE '%.jpg' OR file_name LIKE '%.jpeg' THEN 'image/jpeg'
			 WHEN file_name LIKE '%.png' THEN 'image/png'
			 WHEN file_name LIKE '%.pdf' THEN 'application/pdf'
			 ELSE 'application/octet-stream'
			END as content_type,
			COALESCE(file_size, 0) as size,
			modified
		FROM tabFile
		WHERE file_url = ?
	`

	var file FileInfo
	err := s.db.QueryRow(query, fileURL).Scan(&file.Name, &file.URL, &file.ContentType, &file.Size, &file.Modified)
	if err != nil {
		return nil
	}

	return &file
}

// ServeFile serves file via HTTP
func (s *FileService) ServeFile(w http.ResponseWriter, r *http.Request, fileURL string) {
	filePath := filepath.Join(s.uploadDir, fileURL)

	// Check if file exists
	if _, err := os.Stat(filePath); os.IsNotExist(err) {
		http.Error(w, "File not found", http.StatusNotFound)
		return
	}

	// Set headers
	w.Header().Set("Content-Disposition", fmt.Sprintf("inline; filename=\"%s\"", filepath.Base(fileURL)))

	// Serve file
	http.ServeFile(w, r, filePath)
}
