package services

import (
	"database/sql"
	"fmt"
	"log"
	"time"

	"erpmax-go/internal/cache"
	"erpmax-go/internal/config"
)

type DashboardService struct {
	db    *sql.DB
	cache *cache.RedisCache
}

type DashboardRequest struct {
	Dashboard string                 `json:"dashboard"`
	Filters   map[string]interface{} `json:"filters"`
	Company   string                 `json:"company"`
}

type DashboardResponse struct {
	Widgets   []DashboardWidget      `json:"widgets"`
	KPIs      []KPIData              `json:"kpis"`
	Charts    []ChartData            `json:"charts"`
	Activity  []ActivityItem         `json:"activity"`
	Cached    bool                   `json:"cached"`
	LoadTime  float64                `json:"load_time_ms"`
}

type DashboardWidget struct {
	ID       string      `json:"id"`
	Type     string      `json:"type"`
	Title    string      `json:"title"`
	Value    interface{} `json:"value"`
	Change   float64     `json:"change"`
	Icon     string      `json:"icon"`
	Color    string      `json:"color"`
}

type KPIData struct {
	Name      string  `json:"name"`
	Value     float64 `json:"value"`
	Target    float64 `json:"target"`
	Unit      string  `json:"unit"`
	Trend     string  `json:"trend"`
}

type ChartData struct {
	ID         string                 `json:"id"`
	Type       string                 `json:"type"`
	Title      string                 `json:"title"`
	Categories []string               `json:"categories"`
	Series     []ChartSeries          `json:"series"`
}

type ChartSeries struct {
	Name  string    `json:"name"`
	Data  []float64 `json:"data"`
}

type ActivityItem struct {
	User      string    `json:"user"`
	Action    string    `json:"action"`
	DocType   string    `json:"doc_type"`
	DocName   string    `json:"doc_name"`
	Timestamp time.Time `json:"timestamp"`
}

func NewDashboardService(cfg *config.Config) *DashboardService {
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
		TTL:      5 * time.Minute,
	})

	return &DashboardService{
		db:    db,
		cache: redisCache,
	}
}

// GetDashboard returns dashboard data
func (s *DashboardService) GetDashboard(req DashboardRequest) (*DashboardResponse, error) {
	start := time.Now()

	// Build cache key
	cacheKey := fmt.Sprintf("dashboard:%s:%s", req.Dashboard, req.Company)

	// Try cache
	var cached DashboardResponse
	if s.cache != nil && s.cache.Get(cacheKey, &cached) {
		cached.Cached = true
		cached.LoadTime = float64(time.Since(start).Microseconds()) / 1000
		return &cached, nil
	}

	// Get widgets
	widgets := s.getWidgets(req)

	// Get KPIs
	kpis := s.getKPIs(req)

	// Get charts
	charts := s.getCharts(req)

	// Get recent activity
	activity := s.getActivity(req)

	response := &DashboardResponse{
		Widgets:  widgets,
		KPIs:     kpis,
		Charts:   charts,
		Activity: activity,
		Cached:   false,
		LoadTime: float64(time.Since(start).Microseconds()) / 1000,
	}

	// Cache for 5 minutes
	if s.cache != nil {
		s.cache.Set(cacheKey, response, 5*time.Minute)
	}

	return response, nil
}

func (s *DashboardService) getWidgets(req DashboardRequest) []DashboardWidget {
	widgets := []DashboardWidget{}

	// Total Sales
	totalSales := s.getAggregateValue("tabSalesInvoice", "grand_total", "docstatus = 1")
	widgets = append(widgets, DashboardWidget{
		ID:    "total_sales",
		Type:  "kpi",
		Title: "Total Sales",
		Value: totalSales,
		Icon:  "fa-line-chart",
		Color: "#5e64ff",
	})

	// Total Purchases
	totalPurchases := s.getAggregateValue("tabPurchaseInvoice", "grand_total", "docstatus = 1")
	widgets = append(widgets, DashboardWidget{
		ID:    "total_purchases",
		Type:  "kpi",
		Title: "Total Purchases",
		Value: totalPurchases,
		Icon:  "fa-shopping-cart",
		Color: "#ff5858",
	})

	// Outstanding
	outstanding := s.getAggregateValue("tabSalesInvoice", "outstanding_amount", "docstatus = 1 AND outstanding_amount > 0")
	widgets = append(widgets, DashboardWidget{
		ID:    "outstanding",
		Type:  "kpi",
		Title: "Outstanding",
		Value: outstanding,
		Icon:  "fa-exclamation-triangle",
		Color: "#ffc107",
	})

	// Net Profit
	netProfit := totalSales - totalPurchases
	widgets = append(widgets, DashboardWidget{
		ID:    "net_profit",
		Type:  "kpi",
		Title: "Net Profit",
		Value: netProfit,
		Icon:  "fa-balance-scale",
		Color: "#28a745",
	})

	return widgets
}

func (s *DashboardService) getKPIs(req DashboardRequest) []KPIData {
	kpis := []KPIData{}

	// Customer Count
	customerCount := s.getCount("tabCustomer", "disabled = 0")
	kpis = append(kpis, KPIData{
		Name:   "Customers",
		Value:  float64(customerCount),
		Target: 1000,
		Unit:   "count",
		Trend:  "up",
	})

	// Supplier Count
	supplierCount := s.getCount("tabSupplier", "disabled = 0")
	kpis = append(kpis, KPIData{
		Name:   "Suppliers",
		Value:  float64(supplierCount),
		Target: 500,
		Unit:   "count",
		Trend:  "up",
	})

	// Item Count
	itemCount := s.getCount("tabItem", "disabled = 0")
	kpis = append(kpis, KPIData{
		Name:   "Items",
		Value:  float64(itemCount),
		Target: 2000,
		Unit:   "count",
		Trend:  "up",
	})

	return kpis
}

func (s *DashboardService) getCharts(req DashboardRequest) []ChartData {
	charts := []ChartData{}

	// Sales Trend
	salesTrend := s.getSalesTrend()
	charts = append(charts, salesTrend)

	// Top Customers
	topCustomers := s.getTopCustomers()
	charts = append(charts, topCustomers)

	return charts
}

func (s *DashboardService) getSalesTrend() ChartData {
	query := `
		SELECT 
			DATE(posting_date) as date,
			SUM(grand_total) as total
		FROM tabSalesInvoice
		WHERE docstatus = 1 AND posting_date >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)
		GROUP BY DATE(posting_date)
		ORDER BY date
	`

	rows, err := s.db.Query(query)
	if err != nil {
		return ChartData{}
	}
	defer rows.Close()

	var categories []string
	var values []float64

	for rows.Next() {
		var date string
		var total float64
		if err := rows.Scan(&date, &total); err == nil {
			categories = append(categories, date)
			values = append(values, total)
		}
	}

	return ChartData{
		ID:         "sales_trend",
		Type:       "line",
		Title:      "Sales Trend (30 Days)",
		Categories: categories,
		Series: []ChartSeries{
			{Name: "Sales", Data: values},
		},
	}
}

func (s *DashboardService) getTopCustomers() ChartData {
	query := `
		SELECT 
			customer_name,
			SUM(grand_total) as total
		FROM tabSalesInvoice
		WHERE docstatus = 1
		GROUP BY customer_name
		ORDER BY total DESC
		LIMIT 5
	`

	rows, err := s.db.Query(query)
	if err != nil {
		return ChartData{}
	}
	defer rows.Close()

	var categories []string
	var values []float64

	for rows.Next() {
		var name string
		var total float64
		if err := rows.Scan(&name, &total); err == nil {
			categories = append(categories, name)
			values = append(values, total)
		}
	}

	return ChartData{
		ID:         "top_customers",
		Type:       "bar",
		Title:      "Top Customers",
		Categories: categories,
		Series: []ChartSeries{
			{Name: "Sales", Data: values},
		},
	}
}

func (s *DashboardService) getActivity(req DashboardRequest) []ActivityItem {
	query := `
		SELECT 
			owner as user,
			CASE 
			 WHEN docstatus = 1 THEN 'Submit'
			 WHEN docstatus = 2 THEN 'Cancel'
			 ELSE 'Save'
			END as action,
			'doc_type' as doc_type,
			name as doc_name,
			modified as timestamp
		FROM tabSalesInvoice
		ORDER BY modified DESC
		LIMIT 10
	`

	rows, err := s.db.Query(query)
	if err != nil {
		return nil
	}
	defer rows.Close()

	var activity []ActivityItem
	for rows.Next() {
		var item ActivityItem
		if err := rows.Scan(&item.User, &item.Action, &item.DocType, &item.DocName, &item.Timestamp); err == nil {
			activity = append(activity, item)
		}
	}

	return activity
}

func (s *DashboardService) getAggregateValue(table, field, conditions string) float64 {
	query := fmt.Sprintf("SELECT COALESCE(SUM(%s), 0) FROM %s WHERE %s", field, table, conditions)
	var result float64
	s.db.QueryRow(query).Scan(&result)
	return result
}

func (s *DashboardService) getCount(table, conditions string) int {
	query := fmt.Sprintf("SELECT COUNT(*) FROM %s WHERE %s", table, conditions)
	var count int
	s.db.QueryRow(query).Scan(&count)
	return count
}
