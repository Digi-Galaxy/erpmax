package api

import (
	"encoding/json"
	"net/http"

	"erpmax-go/internal/services"
)

type Router struct {
	mux              *http.ServeMux
	bulkService      *services.BulkService
	reportService    *services.ReportService
	cacheService     *services.CacheService
	jobService       *services.JobService
	listViewService  *services.ListViewService
	printService     *services.PrintService
	dashboardService *services.DashboardService
	searchService    *services.SearchService
	fileService      *services.FileService
	wsService        *services.WebSocketService
}

func NewRouter(bulk *services.BulkService, report *services.ReportService, cache *services.CacheService, job *services.JobService, listView *services.ListViewService, print *services.PrintService, dashboard *services.DashboardService, search *services.SearchService, file *services.FileService, ws *services.WebSocketService) *http.ServeMux {
	router := &Router{
		mux:              http.NewServeMux(),
		bulkService:      bulk,
		reportService:    report,
		cacheService:     cache,
		jobService:       job,
		listViewService:  listView,
		printService:     print,
		dashboardService: dashboard,
		searchService:    search,
		fileService:      file,
		wsService:        ws,
	}

	router.setupRoutes()
	return router.mux
}

func (r *Router) setupRoutes() {
	// Health check
	r.mux.HandleFunc("/health", r.handleHealth)

	// Bulk operations
	r.mux.HandleFunc("/api/bulk/delete", r.handleBulkDelete)
	r.mux.HandleFunc("/api/bulk/update", r.handleBulkUpdate)
	r.mux.HandleFunc("/api/bulk/export", r.handleBulkExport)

	// Reports
	r.mux.HandleFunc("/api/reports/generate", r.handleGenerateReport)
	r.mux.HandleFunc("/api/reports/trial-balance", r.handleTrialBalance)
	r.mux.HandleFunc("/api/reports/general-ledger", r.handleGeneralLedger)
	r.mux.HandleFunc("/api/reports/balance-sheet", r.handleBalanceSheet)
	r.mux.HandleFunc("/api/reports/profit-and-loss", r.handleProfitAndLoss)
	r.mux.HandleFunc("/api/reports/sales-register", r.handleSalesRegister)
	r.mux.HandleFunc("/api/reports/purchase-register", r.handlePurchaseRegister)
	r.mux.HandleFunc("/api/reports/customer-summary", r.handleCustomerSummary)
	r.mux.HandleFunc("/api/reports/supplier-summary", r.handleSupplierSummary)
	r.mux.HandleFunc("/api/reports/aged-receivables", r.handleAgedReceivables)
	r.mux.HandleFunc("/api/reports/aged-payables", r.handleAgedPayables)
	r.mux.HandleFunc("/api/reports/tax-summary", r.handleTaxSummary)
	r.mux.HandleFunc("/api/reports/bank-summary", r.handleBankSummary)

	// Jobs
	r.mux.HandleFunc("/api/jobs/create", r.handleCreateJob)
	r.mux.HandleFunc("/api/jobs/status", r.handleGetJobStatus)
	r.mux.HandleFunc("/api/jobs/queue", r.handleGetQueueStatus)

	// Cache
	r.mux.HandleFunc("/api/cache/stats", r.handleCacheStats)
	r.mux.HandleFunc("/api/cache/clear", r.handleClearCache)
	r.mux.HandleFunc("/api/cache/invalidate", r.handleInvalidateCache)

	// List View
	r.mux.HandleFunc("/api/listview", r.handleListView)
	r.mux.HandleFunc("/api/listview/refresh", r.handleRefreshListView)

	// Print
	r.mux.HandleFunc("/api/print", r.handlePrint)
	r.mux.HandleFunc("/api/print/bulk", r.handleBulkPrint)

	// Dashboard
	r.mux.HandleFunc("/api/dashboard", r.handleDashboard)
	r.mux.HandleFunc("/api/dashboard/refresh", r.handleRefreshDashboard)

	// Search
	r.mux.HandleFunc("/api/search", r.handleSearch)
	r.mux.HandleFunc("/api/autocomplete", r.handleAutocomplete)

	// Files
	r.mux.HandleFunc("/api/files", r.handleGetFile)
	r.mux.HandleFunc("/api/files/upload", r.handleUploadFile)
	r.mux.HandleFunc("/api/files/delete", r.handleDeleteFile)
	r.mux.HandleFunc("/api/files/doc", r.handleGetDocFiles)

	// WebSocket
	r.mux.HandleFunc("/ws", r.handleWebSocket)
}

func (r *Router) handleHealth(w http.ResponseWriter, req *http.Request) {
	respondJSON(w, http.StatusOK, map[string]interface{}{
		"status":  "healthy",
		"service": "erpmax-go-services",
	})
}

func (r *Router) handleBulkDelete(w http.ResponseWriter, req *http.Request) {
	if req.Method != http.MethodPost {
		respondError(w, http.StatusMethodNotAllowed, "Method not allowed")
		return
	}

	var request services.BulkDeleteRequest
	if err := json.NewDecoder(req.Body).Decode(&request); err != nil {
		respondError(w, http.StatusBadRequest, "Invalid request body")
		return
	}

	result, err := r.bulkService.BulkDelete(request)
	if err != nil {
		respondError(w, http.StatusInternalServerError, err.Error())
		return
	}

	respondJSON(w, http.StatusOK, result)
}

func (r *Router) handleBulkUpdate(w http.ResponseWriter, req *http.Request) {
	if req.Method != http.MethodPost {
		respondError(w, http.StatusMethodNotAllowed, "Method not allowed")
		return
	}

	var request services.BulkUpdateRequest
	if err := json.NewDecoder(req.Body).Decode(&request); err != nil {
		respondError(w, http.StatusBadRequest, "Invalid request body")
		return
	}

	result, err := r.bulkService.BulkUpdate(request)
	if err != nil {
		respondError(w, http.StatusInternalServerError, err.Error())
		return
	}

	respondJSON(w, http.StatusOK, result)
}

func (r *Router) handleBulkExport(w http.ResponseWriter, req *http.Request) {
	if req.Method != http.MethodPost {
		respondError(w, http.StatusMethodNotAllowed, "Method not allowed")
		return
	}

	var request services.BulkExportRequest
	if err := json.NewDecoder(req.Body).Decode(&request); err != nil {
		respondError(w, http.StatusBadRequest, "Invalid request body")
		return
	}

	data, contentType, err := r.bulkService.BulkExport(request)
	if err != nil {
		respondError(w, http.StatusInternalServerError, err.Error())
		return
	}

	w.Header().Set("Content-Type", contentType)
	w.Write(data)
}

func (r *Router) handleGenerateReport(w http.ResponseWriter, req *http.Request) {
	if req.Method != http.MethodPost {
		respondError(w, http.StatusMethodNotAllowed, "Method not allowed")
		return
	}

	var request struct {
		ReportType string                 `json:"report_type"`
		Filters    map[string]interface{} `json:"filters"`
	}
	if err := json.NewDecoder(req.Body).Decode(&request); err != nil {
		respondError(w, http.StatusBadRequest, "Invalid request body")
		return
	}

	result, err := r.reportService.GenerateReport(request.ReportType, request.Filters)
	if err != nil {
		respondError(w, http.StatusInternalServerError, err.Error())
		return
	}

	respondJSON(w, http.StatusOK, result)
}

func (r *Router) handleTrialBalance(w http.ResponseWriter, req *http.Request) {
	r.handleReport("trial_balance", w, req)
}

func (r *Router) handleGeneralLedger(w http.ResponseWriter, req *http.Request) {
	r.handleReport("general_ledger", w, req)
}

func (r *Router) handleBalanceSheet(w http.ResponseWriter, req *http.Request) {
	r.handleReport("balance_sheet", w, req)
}

func (r *Router) handleProfitAndLoss(w http.ResponseWriter, req *http.Request) {
	r.handleReport("profit_and_loss", w, req)
}

func (r *Router) handleSalesRegister(w http.ResponseWriter, req *http.Request) {
	r.handleReport("sales_register", w, req)
}

func (r *Router) handlePurchaseRegister(w http.ResponseWriter, req *http.Request) {
	r.handleReport("purchase_register", w, req)
}

func (r *Router) handleCustomerSummary(w http.ResponseWriter, req *http.Request) {
	r.handleReport("customer_summary", w, req)
}

func (r *Router) handleSupplierSummary(w http.ResponseWriter, req *http.Request) {
	r.handleReport("supplier_summary", w, req)
}

func (r *Router) handleAgedReceivables(w http.ResponseWriter, req *http.Request) {
	r.handleReport("aged_receivables", w, req)
}

func (r *Router) handleAgedPayables(w http.ResponseWriter, req *http.Request) {
	r.handleReport("aged_payables", w, req)
}

func (r *Router) handleTaxSummary(w http.ResponseWriter, req *http.Request) {
	r.handleReport("tax_summary", w, req)
}

func (r *Router) handleBankSummary(w http.ResponseWriter, req *http.Request) {
	r.handleReport("bank_summary", w, req)
}

func (r *Router) handleReport(reportType string, w http.ResponseWriter, req *http.Request) {
	filters := make(map[string]interface{})
	if req.Method == http.MethodPost {
		json.NewDecoder(req.Body).Decode(&filters)
	} else if req.Method == http.MethodGet {
		for key, values := range req.URL.Query() {
			if len(values) > 0 {
				filters[key] = values[0]
			}
		}
	}

	result, err := r.reportService.GenerateReport(reportType, filters)
	if err != nil {
		respondError(w, http.StatusInternalServerError, err.Error())
		return
	}

	respondJSON(w, http.StatusOK, result)
}

func (r *Router) handleCreateJob(w http.ResponseWriter, req *http.Request) {
	if req.Method != http.MethodPost {
		respondError(w, http.StatusMethodNotAllowed, "Method not allowed")
		return
	}

	var request services.JobRequest
	if err := json.NewDecoder(req.Body).Decode(&request); err != nil {
		respondError(w, http.StatusBadRequest, "Invalid request body")
		return
	}

	job := r.jobService.CreateJob(request)
	respondJSON(w, http.StatusCreated, job)
}

func (r *Router) handleGetJobStatus(w http.ResponseWriter, req *http.Request) {
	jobID := req.URL.Query().Get("id")
	if jobID == "" {
		respondError(w, http.StatusBadRequest, "Job ID required")
		return
	}

	job, exists := r.jobService.GetJob(jobID)
	if !exists {
		respondError(w, http.StatusNotFound, "Job not found")
		return
	}

	respondJSON(w, http.StatusOK, job)
}

func (r *Router) handleGetQueueStatus(w http.ResponseWriter, req *http.Request) {
	respondJSON(w, http.StatusOK, map[string]interface{}{
		"queue_size":  r.jobService.GetQueueSize(),
		"pending_jobs": r.jobService.GetPendingJobs(),
	})
}

func (r *Router) handleCacheStats(w http.ResponseWriter, req *http.Request) {
	stats := r.cacheService.GetStats()
	respondJSON(w, http.StatusOK, stats)
}

func (r *Router) handleClearCache(w http.ResponseWriter, req *http.Request) {
	r.cacheService.Clear()
	respondJSON(w, http.StatusOK, map[string]interface{}{
		"message": "Cache cleared",
	})
}

func (r *Router) handleInvalidateCache(w http.ResponseWriter, req *http.Request) {
	var request struct {
		Doctype string `json:"doctype"`
	}
	if err := json.NewDecoder(req.Body).Decode(&request); err != nil {
		respondError(w, http.StatusBadRequest, "Invalid request body")
		return
	}

	r.cacheService.InvalidateDoctype(request.Doctype)
	respondJSON(w, http.StatusOK, map[string]interface{}{
		"message": "Cache invalidated for " + request.Doctype,
	})
}

// List View handlers
func (r *Router) handleListView(w http.ResponseWriter, req *http.Request) {
	if req.Method != http.MethodPost {
		respondError(w, http.StatusMethodNotAllowed, "Method not allowed")
		return
	}

	var request services.ListViewRequest
	if err := json.NewDecoder(req.Body).Decode(&request); err != nil {
		respondError(w, http.StatusBadRequest, "Invalid request body")
		return
	}

	result, err := r.listViewService.GetListView(request)
	if err != nil {
		respondError(w, http.StatusInternalServerError, err.Error())
		return
	}

	respondJSON(w, http.StatusOK, result)
}

func (r *Router) handleRefreshListView(w http.ResponseWriter, req *http.Request) {
	if req.Method != http.MethodPost {
		respondError(w, http.StatusMethodNotAllowed, "Method not allowed")
		return
	}

	var request struct {
		Doctype string `json:"doctype"`
	}
	if err := json.NewDecoder(req.Body).Decode(&request); err != nil {
		respondError(w, http.StatusBadRequest, "Invalid request body")
		return
	}

	r.listViewService.InvalidateCache(request.Doctype)
	respondJSON(w, http.StatusOK, map[string]interface{}{"message": "Cache refreshed"})
}

// Print handlers
func (r *Router) handlePrint(w http.ResponseWriter, req *http.Request) {
	if req.Method != http.MethodPost {
		respondError(w, http.StatusMethodNotAllowed, "Method not allowed")
		return
	}

	var request services.PrintRequest
	if err := json.NewDecoder(req.Body).Decode(&request); err != nil {
		respondError(w, http.StatusBadRequest, "Invalid request body")
		return
	}

	result, err := r.printService.GetPrintData(request)
	if err != nil {
		respondError(w, http.StatusInternalServerError, err.Error())
		return
	}

	respondJSON(w, http.StatusOK, result)
}

func (r *Router) handleBulkPrint(w http.ResponseWriter, req *http.Request) {
	if req.Method != http.MethodPost {
		respondError(w, http.StatusMethodNotAllowed, "Method not allowed")
		return
	}

	var request struct {
		Doctype     string   `json:"doctype"`
		Names       []string `json:"names"`
		PrintFormat string   `json:"print_format"`
	}
	if err := json.NewDecoder(req.Body).Decode(&request); err != nil {
		respondError(w, http.StatusBadRequest, "Invalid request body")
		return
	}

	result, err := r.printService.GetBulkPrintData(request.Doctype, request.Names, request.PrintFormat)
	if err != nil {
		respondError(w, http.StatusInternalServerError, err.Error())
		return
	}

	respondJSON(w, http.StatusOK, result)
}

// Dashboard handlers
func (r *Router) handleDashboard(w http.ResponseWriter, req *http.Request) {
	if req.Method != http.MethodPost {
		respondError(w, http.StatusMethodNotAllowed, "Method not allowed")
		return
	}

	var request services.DashboardRequest
	if err := json.NewDecoder(req.Body).Decode(&request); err != nil {
		respondError(w, http.StatusBadRequest, "Invalid request body")
		return
	}

	result, err := r.dashboardService.GetDashboard(request)
	if err != nil {
		respondError(w, http.StatusInternalServerError, err.Error())
		return
	}

	respondJSON(w, http.StatusOK, result)
}

func (r *Router) handleRefreshDashboard(w http.ResponseWriter, req *http.Request) {
	respondJSON(w, http.StatusOK, map[string]interface{}{"message": "Dashboard refreshed"})
}

// Search handlers
func (r *Router) handleSearch(w http.ResponseWriter, req *http.Request) {
	var request services.SearchRequest
	if err := json.NewDecoder(req.Body).Decode(&request); err != nil {
		// Try GET params
		query := req.URL.Query().Get("q")
		if query == "" {
			respondError(w, http.StatusBadRequest, "Query required")
			return
		}
		request.Query = query
	}

	result, err := r.searchService.Search(request)
	if err != nil {
		respondError(w, http.StatusInternalServerError, err.Error())
		return
	}

	respondJSON(w, http.StatusOK, result)
}

func (r *Router) handleAutocomplete(w http.ResponseWriter, req *http.Request) {
	query := req.URL.Query().Get("q")
	doctype := req.URL.Query().Get("doctype")
	limit := 10

	if query == "" {
		respondError(w, http.StatusBadRequest, "Query required")
		return
	}

	results := r.searchService.Autocomplete(query, doctype, limit)
	respondJSON(w, http.StatusOK, results)
}

// File handlers
func (r *Router) handleGetFile(w http.ResponseWriter, req *http.Request) {
	fileURL := req.URL.Query().Get("url")
	if fileURL == "" {
		respondError(w, http.StatusBadRequest, "File URL required")
		return
	}

	result, err := r.fileService.GetFile(services.FileRequest{FileURL: fileURL})
	if err != nil {
		respondError(w, http.StatusInternalServerError, err.Error())
		return
	}

	w.Header().Set("Content-Type", result.ContentType)
	w.Write(result.Content)
}

func (r *Router) handleUploadFile(w http.ResponseWriter, req *http.Request) {
	if req.Method != http.MethodPost {
		respondError(w, http.StatusMethodNotAllowed, "Method not allowed")
		return
	}

	// Handle file upload
	file, header, err := req.FormFile("file")
	if err != nil {
		respondError(w, http.StatusBadRequest, "No file provided")
		return
	}
	defer file.Close()

	doctype := req.FormValue("doctype")
	docName := req.FormValue("doc_name")

	result, err := r.fileService.UploadFile(file, header.Filename, doctype, docName)
	if err != nil {
		respondError(w, http.StatusInternalServerError, err.Error())
		return
	}

	respondJSON(w, http.StatusOK, result)
}

func (r *Router) handleDeleteFile(w http.ResponseWriter, req *http.Request) {
	if req.Method != http.MethodPost {
		respondError(w, http.StatusMethodNotAllowed, "Method not allowed")
		return
	}

	var request struct {
		FileURL string `json:"file_url"`
	}
	if err := json.NewDecoder(req.Body).Decode(&request); err != nil {
		respondError(w, http.StatusBadRequest, "Invalid request body")
		return
	}

	err := r.fileService.DeleteFile(request.FileURL)
	if err != nil {
		respondError(w, http.StatusInternalServerError, err.Error())
		return
	}

	respondJSON(w, http.StatusOK, map[string]interface{}{"message": "File deleted"})
}

func (r *Router) handleGetDocFiles(w http.ResponseWriter, req *http.Request) {
	doctype := req.URL.Query().Get("doctype")
	docName := req.URL.Query().Get("name")

	if doctype == "" || docName == "" {
		respondError(w, http.StatusBadRequest, "Doctype and name required")
		return
	}

	files, err := r.fileService.GetFilesByDoc(doctype, docName)
	if err != nil {
		respondError(w, http.StatusInternalServerError, err.Error())
		return
	}

	respondJSON(w, http.StatusOK, files)
}

// WebSocket handler
func (r *Router) handleWebSocket(w http.ResponseWriter, req *http.Request) {
	r.wsService.HandleWebSocket(w, req)
}

func respondJSON(w http.ResponseWriter, status int, data interface{}) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(status)
	json.NewEncoder(w).Encode(data)
}

func respondError(w http.ResponseWriter, status int, message string) {
	respondJSON(w, status, map[string]interface{}{
		"error": message,
	})
}
