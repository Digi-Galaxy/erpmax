package main

import (
	"context"
	"fmt"
	"log"
	"net/http"
	"os"
	"os/signal"
	"syscall"
	"time"

	_ "github.com/go-sql-driver/mysql"
	
	"erpmax-go/internal/api"
	"erpmax-go/internal/config"
	"erpmax-go/internal/services"
	"erpmax-go/internal/worker"
)

func main() {
	// Load configuration
	cfg := config.Load()

	// Initialize services
	bulkService := services.NewBulkService(cfg)
	reportService := services.NewReportService(cfg)
	cacheService := services.NewCacheService(cfg)
	jobService := services.NewJobService(cfg)
	listViewService := services.NewListViewService(cfg)
	printService := services.NewPrintService(cfg)
	dashboardService := services.NewDashboardService(cfg)
	searchService := services.NewSearchService(cfg)
	fileService := services.NewFileService(cfg)
	wsService := services.NewWebSocketService()

	// Start WebSocket service
	wsService.Start()

	// Initialize worker pool
	workerPool := worker.NewPool(cfg.WorkerCount, jobService)
	workerPool.Start()

	// Initialize API router
	router := api.NewRouter(bulkService, reportService, cacheService, jobService, listViewService, printService, dashboardService, searchService, fileService, wsService)

	// Create HTTP server
	server := &http.Server{
		Addr:         fmt.Sprintf(":%d", cfg.Port),
		Handler:      router,
		ReadTimeout:  30 * time.Second,
		WriteTimeout: 30 * time.Second,
		IdleTimeout:  120 * time.Second,
	}

	// Start server in goroutine
	go func() {
		log.Printf("ERPMax Go Services starting on port %d", cfg.Port)
		if err := server.ListenAndServe(); err != nil && err != http.ErrServerClosed {
			log.Fatalf("Server failed: %v", err)
		}
	}()

	// Graceful shutdown
	quit := make(chan os.Signal, 1)
	signal.Notify(quit, syscall.SIGINT, syscall.SIGTERM)
	<-quit

	log.Println("Shutting down server...")

	// Stop worker pool
	workerPool.Stop()

	// Shutdown server with timeout
	ctx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
	defer cancel()

	if err := server.Shutdown(ctx); err != nil {
		log.Fatalf("Server forced to shutdown: %v", err)
	}

	log.Println("Server exited gracefully")
}
