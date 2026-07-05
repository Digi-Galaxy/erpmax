package services

import (
	"database/sql"
	"fmt"
	"log"
	"time"

	"erpmax-go/internal/config"
)

type ReportService struct {
	db    *sql.DB
	cache *CacheService
}

type ReportResult struct {
	ReportType string                 `json:"report_type"`
	Data       []map[string]interface{} `json:"data"`
	Summary    map[string]interface{} `json:"summary"`
	Columns    []ColumnInfo           `json:"columns"`
	GeneratedAt time.Time            `json:"generated_at"`
	Cached     bool                  `json:"cached"`
}

type ColumnInfo struct {
	Field   string `json:"field"`
	Label   string `json:"label"`
	Type    string `json:"type"`
	Width   int    `json:"width"`
}

func NewReportService(cfg *config.Config) *ReportService {
	db, err := sql.Open("mysql", fmt.Sprintf("%s:%s@tcp(%s:%d)/%s",
		cfg.DBUser, cfg.DBPassword, cfg.DBHost, cfg.DBPort, cfg.DBName))
	if err != nil {
		log.Fatalf("Failed to connect to database: %v", err)
	}

	return &ReportService{
		db:    db,
		cache: NewCacheService(cfg),
	}
}

// GenerateReport generates a report with caching
func (s *ReportService) GenerateReport(reportType string, filters map[string]interface{}) (*ReportResult, error) {
	// Build cache key
	cacheKey := fmt.Sprintf("report:%s:%v", reportType, filters)

	// Check cache
	if cached, exists := s.cache.Get(cacheKey); exists {
		result := cached.(*ReportResult)
		result.Cached = true
		return result, nil
	}

	// Generate report
	var result *ReportResult
	var err error

	switch reportType {
	case "trial_balance":
		result, err = s.generateTrialBalance(filters)
	case "general_ledger":
		result, err = s.generateGeneralLedger(filters)
	case "balance_sheet":
		result, err = s.generateBalanceSheet(filters)
	case "profit_and_loss":
		result, err = s.generateProfitAndLoss(filters)
	case "sales_register":
		result, err = s.generateSalesRegister(filters)
	case "purchase_register":
		result, err = s.generatePurchaseRegister(filters)
	case "customer_summary":
		result, err = s.generateCustomerSummary(filters)
	case "supplier_summary":
		result, err = s.generateSupplierSummary(filters)
	case "aged_receivables":
		result, err = s.generateAgedReceivables(filters)
	case "aged_payables":
		result, err = s.generateAgedPayables(filters)
	case "tax_summary":
		result, err = s.generateTaxSummary(filters)
	case "bank_summary":
		result, err = s.generateBankSummary(filters)
	default:
		return nil, fmt.Errorf("unknown report type: %s", reportType)
	}

	if err != nil {
		return nil, err
	}

	// Cache result for 30 minutes
	s.cache.Set(cacheKey, result, 30*time.Minute)

	return result, nil
}

func (s *ReportService) generateTrialBalance(filters map[string]interface{}) (*ReportResult, error) {
	query := `
		SELECT 
			account,
			SUM(debit) as debit,
			SUM(credit) as credit,
			SUM(debit) - SUM(credit) as balance
		FROM tabGLEntry
		WHERE is_cancelled = 0
		GROUP BY account
		ORDER BY account
	`

	rows, err := s.db.Query(query)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var data []map[string]interface{}
	for rows.Next() {
		var account string
		var debit, credit, balance float64
		if err := rows.Scan(&account, &debit, &credit, &balance); err != nil {
			continue
		}
		data = append(data, map[string]interface{}{
			"account": account,
			"debit":   debit,
			"credit":  credit,
			"balance": balance,
		})
	}

	// Calculate summary
	totalDebit := 0.0
	totalCredit := 0.0
	for _, row := range data {
		totalDebit += row["debit"].(float64)
		totalCredit += row["credit"].(float64)
	}

	return &ReportResult{
		ReportType:  "trial_balance",
		Data:        data,
		Summary: map[string]interface{}{
			"total_debit":  totalDebit,
			"total_credit": totalCredit,
		},
		Columns: []ColumnInfo{
			{Field: "account", Label: "Account", Type: "Link", Width: 300},
			{Field: "debit", Label: "Debit", Type: "Currency", Width: 120},
			{Field: "credit", Label: "Credit", Type: "Currency", Width: 120},
			{Field: "balance", Label: "Balance", Type: "Currency", Width: 120},
		},
		GeneratedAt: time.Now(),
		Cached:      false,
	}, nil
}

func (s *ReportService) generateGeneralLedger(filters map[string]interface{}) (*ReportResult, error) {
	query := `
		SELECT 
			posting_date,
			account,
			voucher_type,
			voucher_no,
			debit,
			credit
		FROM tabGLEntry
		WHERE is_cancelled = 0
		ORDER BY posting_date DESC
		LIMIT 1000
	`

	rows, err := s.db.Query(query)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var data []map[string]interface{}
	for rows.Next() {
		var postingDate time.Time
		var account, voucherType, voucherNo string
		var debit, credit float64
		if err := rows.Scan(&postingDate, &account, &voucherType, &voucherNo, &debit, &credit); err != nil {
			continue
		}
		data = append(data, map[string]interface{}{
			"posting_date": postingDate,
			"account":      account,
			"voucher_type": voucherType,
			"voucher_no":   voucherNo,
			"debit":        debit,
			"credit":       credit,
		})
	}

	return &ReportResult{
		ReportType: "general_ledger",
		Data:       data,
		Columns: []ColumnInfo{
			{Field: "posting_date", Label: "Date", Type: "Date", Width: 100},
			{Field: "account", Label: "Account", Type: "Link", Width: 200},
			{Field: "voucher_type", Label: "Voucher Type", Type: "Data", Width: 120},
			{Field: "voucher_no", Label: "Voucher No", Type: "Data", Width: 150},
			{Field: "debit", Label: "Debit", Type: "Currency", Width: 120},
			{Field: "credit", Label: "Credit", Type: "Currency", Width: 120},
		},
		GeneratedAt: time.Now(),
		Cached:      false,
	}, nil
}

func (s *ReportService) generateBalanceSheet(filters map[string]interface{}) (*ReportResult, error) {
	// Simplified balance sheet
	query := `
		SELECT 
			CASE 
			 WHEN account LIKE '1%' THEN 'Asset'
			 WHEN account LIKE '2%' THEN 'Liability'
			 WHEN account LIKE '3%' THEN 'Equity'
			 ELSE 'Other'
			END as root_type,
			SUM(debit) - SUM(credit) as balance
		FROM tabGLEntry
		WHERE is_cancelled = 0
		GROUP BY root_type
	`

	rows, err := s.db.Query(query)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var data []map[string]interface{}
	for rows.Next() {
		var rootType string
		var balance float64
		if err := rows.Scan(&rootType, &balance); err != nil {
			continue
		}
		data = append(data, map[string]interface{}{
			"root_type": rootType,
			"balance":   balance,
		})
	}

	return &ReportResult{
		ReportType: "balance_sheet",
		Data:       data,
		Columns: []ColumnInfo{
			{Field: "root_type", Label: "Type", Type: "Data", Width: 150},
			{Field: "balance", Label: "Balance", Type: "Currency", Width: 150},
		},
		GeneratedAt: time.Now(),
		Cached:      false,
	}, nil
}

func (s *ReportService) generateProfitAndLoss(filters map[string]interface{}) (*ReportResult, error) {
	query := `
		SELECT 
			CASE 
			 WHEN account LIKE '4%' THEN 'Income'
			 WHEN account LIKE '5%' THEN 'Expense'
			 ELSE 'Other'
			END as root_type,
			SUM(debit) - SUM(credit) as balance
		FROM tabGLEntry
		WHERE is_cancelled = 0
		GROUP BY root_type
	`

	rows, err := s.db.Query(query)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var data []map[string]interface{}
	for rows.Next() {
		var rootType string
		var balance float64
		if err := rows.Scan(&rootType, &balance); err != nil {
			continue
		}
		data = append(data, map[string]interface{}{
			"root_type": rootType,
			"balance":   balance,
		})
	}

	return &ReportResult{
		ReportType: "profit_and_loss",
		Data:       data,
		Columns: []ColumnInfo{
			{Field: "root_type", Label: "Type", Type: "Data", Width: 150},
			{Field: "balance", Label: "Amount", Type: "Currency", Width: 150},
		},
		GeneratedAt: time.Now(),
		Cached:      false,
	}, nil
}

func (s *ReportService) generateSalesRegister(filters map[string]interface{}) (*ReportResult, error) {
	query := `
		SELECT 
			name,
			customer,
			customer_name,
			grand_total,
			posting_date
		FROM tabSalesInvoice
		WHERE docstatus = 1
		ORDER BY posting_date DESC
		LIMIT 1000
	`

	rows, err := s.db.Query(query)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var data []map[string]interface{}
	for rows.Next() {
		var name, customer, customerName string
		var grandTotal float64
		var postingDate time.Time
		if err := rows.Scan(&name, &customer, &customerName, &grandTotal, &postingDate); err != nil {
			continue
		}
		data = append(data, map[string]interface{}{
			"name":           name,
			"customer":       customer,
			"customer_name":  customerName,
			"grand_total":    grandTotal,
			"posting_date":   postingDate,
		})
	}

	return &ReportResult{
		ReportType: "sales_register",
		Data:       data,
		Columns: []ColumnInfo{
			{Field: "name", Label: "Invoice No", Type: "Link", Width: 150},
			{Field: "customer_name", Label: "Customer", Type: "Data", Width: 200},
			{Field: "grand_total", Label: "Amount", Type: "Currency", Width: 120},
			{Field: "posting_date", Label: "Date", Type: "Date", Width: 100},
		},
		GeneratedAt: time.Now(),
		Cached:      false,
	}, nil
}

func (s *ReportService) generatePurchaseRegister(filters map[string]interface{}) (*ReportResult, error) {
	query := `
		SELECT 
			name,
			supplier,
			supplier_name,
			grand_total,
			posting_date
		FROM tabPurchaseInvoice
		WHERE docstatus = 1
		ORDER BY posting_date DESC
		LIMIT 1000
	`

	rows, err := s.db.Query(query)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var data []map[string]interface{}
	for rows.Next() {
		var name, supplier, supplierName string
		var grandTotal float64
		var postingDate time.Time
		if err := rows.Scan(&name, &supplier, &supplierName, &grandTotal, &postingDate); err != nil {
			continue
		}
		data = append(data, map[string]interface{}{
			"name":           name,
			"supplier":       supplier,
			"supplier_name":  supplierName,
			"grand_total":    grandTotal,
			"posting_date":   postingDate,
		})
	}

	return &ReportResult{
		ReportType: "purchase_register",
		Data:       data,
		Columns: []ColumnInfo{
			{Field: "name", Label: "Invoice No", Type: "Link", Width: 150},
			{Field: "supplier_name", Label: "Supplier", Type: "Data", Width: 200},
			{Field: "grand_total", Label: "Amount", Type: "Currency", Width: 120},
			{Field: "posting_date", Label: "Date", Type: "Date", Width: 100},
		},
		GeneratedAt: time.Now(),
		Cached:      false,
	}, nil
}

func (s *ReportService) generateCustomerSummary(filters map[string]interface{}) (*ReportResult, error) {
	query := `
		SELECT 
			customer,
			customer_name,
			SUM(grand_total) as total_invoiced,
			SUM(paid_amount) as total_paid,
			SUM(outstanding_amount) as outstanding
		FROM tabSalesInvoice
		WHERE docstatus = 1
		GROUP BY customer
		ORDER BY outstanding DESC
	`

	rows, err := s.db.Query(query)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var data []map[string]interface{}
	for rows.Next() {
		var customer, customerName string
		var totalInvoiced, totalPaid, outstanding float64
		if err := rows.Scan(&customer, &customerName, &totalInvoiced, &totalPaid, &outstanding); err != nil {
			continue
		}
		data = append(data, map[string]interface{}{
			"customer":       customer,
			"customer_name":  customerName,
			"total_invoiced": totalInvoiced,
			"total_paid":     totalPaid,
			"outstanding":    outstanding,
		})
	}

	return &ReportResult{
		ReportType: "customer_summary",
		Data:       data,
		Columns: []ColumnInfo{
			{Field: "customer_name", Label: "Customer", Type: "Data", Width: 200},
			{Field: "total_invoiced", Label: "Invoiced", Type: "Currency", Width: 120},
			{Field: "total_paid", Label: "Paid", Type: "Currency", Width: 120},
			{Field: "outstanding", Label: "Outstanding", Type: "Currency", Width: 120},
		},
		GeneratedAt: time.Now(),
		Cached:      false,
	}, nil
}

func (s *ReportService) generateSupplierSummary(filters map[string]interface{}) (*ReportResult, error) {
	query := `
		SELECT 
			supplier,
			supplier_name,
			SUM(grand_total) as total_purchased,
			SUM(paid_amount) as total_paid,
			SUM(outstanding_amount) as outstanding
		FROM tabPurchaseInvoice
		WHERE docstatus = 1
		GROUP BY supplier
		ORDER BY outstanding DESC
	`

	rows, err := s.db.Query(query)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var data []map[string]interface{}
	for rows.Next() {
		var supplier, supplierName string
		var totalPurchased, totalPaid, outstanding float64
		if err := rows.Scan(&supplier, &supplierName, &totalPurchased, &totalPaid, &outstanding); err != nil {
			continue
		}
		data = append(data, map[string]interface{}{
			"supplier":        supplier,
			"supplier_name":   supplierName,
			"total_purchased": totalPurchased,
			"total_paid":      totalPaid,
			"outstanding":     outstanding,
		})
	}

	return &ReportResult{
		ReportType: "supplier_summary",
		Data:       data,
		Columns: []ColumnInfo{
			{Field: "supplier_name", Label: "Supplier", Type: "Data", Width: 200},
			{Field: "total_purchased", Label: "Purchased", Type: "Currency", Width: 120},
			{Field: "total_paid", Label: "Paid", Type: "Currency", Width: 120},
			{Field: "outstanding", Label: "Outstanding", Type: "Currency", Width: 120},
		},
		GeneratedAt: time.Now(),
		Cached:      false,
	}, nil
}

func (s *ReportService) generateAgedReceivables(filters map[string]interface{}) (*ReportResult, error) {
	query := `
		SELECT 
			customer,
			customer_name,
			SUM(CASE WHEN DATEDIFF(CURDATE(), posting_date) <= 30 THEN outstanding_amount ELSE 0 END) as "0-30",
			SUM(CASE WHEN DATEDIFF(CURDATE(), posting_date) BETWEEN 31 AND 60 THEN outstanding_amount ELSE 0 END) as "31-60",
			SUM(CASE WHEN DATEDIFF(CURDATE(), posting_date) BETWEEN 61 AND 90 THEN outstanding_amount ELSE 0 END) as "61-90",
			SUM(CASE WHEN DATEDIFF(CURDATE(), posting_date) > 90 THEN outstanding_amount ELSE 0 END) as "90+",
			SUM(outstanding_amount) as total
		FROM tabSalesInvoice
		WHERE docstatus = 1 AND outstanding_amount > 0
		GROUP BY customer
		ORDER BY total DESC
	`

	rows, err := s.db.Query(query)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var data []map[string]interface{}
	for rows.Next() {
		var customer, customerName string
		var d30, d60, d90, d90plus, total float64
		if err := rows.Scan(&customer, &customerName, &d30, &d60, &d90, &d90plus, &total); err != nil {
			continue
		}
		data = append(data, map[string]interface{}{
			"customer":      customer,
			"customer_name": customerName,
			"d30":           d30,
			"d60":           d60,
			"d90":           d90,
			"d90plus":       d90plus,
			"total":         total,
		})
	}

	return &ReportResult{
		ReportType: "aged_receivables",
		Data:       data,
		Columns: []ColumnInfo{
			{Field: "customer_name", Label: "Customer", Type: "Data", Width: 200},
			{Field: "d30", Label: "0-30 Days", Type: "Currency", Width: 100},
			{Field: "d60", Label: "31-60 Days", Type: "Currency", Width: 100},
			{Field: "d90", Label: "61-90 Days", Type: "Currency", Width: 100},
			{Field: "d90plus", Label: "90+ Days", Type: "Currency", Width: 100},
			{Field: "total", Label: "Total", Type: "Currency", Width: 120},
		},
		GeneratedAt: time.Now(),
		Cached:      false,
	}, nil
}

func (s *ReportService) generateAgedPayables(filters map[string]interface{}) (*ReportResult, error) {
	query := `
		SELECT 
			supplier,
			supplier_name,
			SUM(CASE WHEN DATEDIFF(CURDATE(), posting_date) <= 30 THEN outstanding_amount ELSE 0 END) as "0-30",
			SUM(CASE WHEN DATEDIFF(CURDATE(), posting_date) BETWEEN 31 AND 60 THEN outstanding_amount ELSE 0 END) as "31-60",
			SUM(CASE WHEN DATEDIFF(CURDATE(), posting_date) BETWEEN 61 AND 90 THEN outstanding_amount ELSE 0 END) as "61-90",
			SUM(CASE WHEN DATEDIFF(CURDATE(), posting_date) > 90 THEN outstanding_amount ELSE 0 END) as "90+",
			SUM(outstanding_amount) as total
		FROM tabPurchaseInvoice
		WHERE docstatus = 1 AND outstanding_amount > 0
		GROUP BY supplier
		ORDER BY total DESC
	`

	rows, err := s.db.Query(query)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var data []map[string]interface{}
	for rows.Next() {
		var supplier, supplierName string
		var d30, d60, d90, d90plus, total float64
		if err := rows.Scan(&supplier, &supplierName, &d30, &d60, &d90, &d90plus, &total); err != nil {
			continue
		}
		data = append(data, map[string]interface{}{
			"supplier":      supplier,
			"supplier_name": supplierName,
			"d30":           d30,
			"d60":           d60,
			"d90":           d90,
			"d90plus":       d90plus,
			"total":         total,
		})
	}

	return &ReportResult{
		ReportType: "aged_payables",
		Data:       data,
		Columns: []ColumnInfo{
			{Field: "supplier_name", Label: "Supplier", Type: "Data", Width: 200},
			{Field: "d30", Label: "0-30 Days", Type: "Currency", Width: 100},
			{Field: "d60", Label: "31-60 Days", Type: "Currency", Width: 100},
			{Field: "d90", Label: "61-90 Days", Type: "Currency", Width: 100},
			{Field: "d90plus", Label: "90+ Days", Type: "Currency", Width: 100},
			{Field: "total", Label: "Total", Type: "Currency", Width: 120},
		},
		GeneratedAt: time.Now(),
		Cached:      false,
	}, nil
}

func (s *ReportService) generateTaxSummary(filters map[string]interface{}) (*ReportResult, error) {
	query := `
		SELECT 
			tax_type,
			rate,
			SUM(amount) as tax_amount
		FROM tabSalesInvoiceTax
		WHERE parent IN (SELECT name FROM tabSalesInvoice WHERE docstatus = 1)
		GROUP BY tax_type, rate
	`

	rows, err := s.db.Query(query)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var data []map[string]interface{}
	for rows.Next() {
		var taxType string
		var rate, taxAmount float64
		if err := rows.Scan(&taxType, &rate, &taxAmount); err != nil {
			continue
		}
		data = append(data, map[string]interface{}{
			"tax_type":   taxType,
			"rate":       rate,
			"tax_amount": taxAmount,
		})
	}

	return &ReportResult{
		ReportType: "tax_summary",
		Data:       data,
		Columns: []ColumnInfo{
			{Field: "tax_type", Label: "Tax Type", Type: "Data", Width: 150},
			{Field: "rate", Label: "Rate", Type: "Percent", Width: 100},
			{Field: "tax_amount", Label: "Amount", Type: "Currency", Width: 120},
		},
		GeneratedAt: time.Now(),
		Cached:      false,
	}, nil
}

func (s *ReportService) generateBankSummary(filters map[string]interface{}) (*ReportResult, error) {
	query := `
		SELECT 
			bank_account,
			SUM(CASE WHEN transaction_type = 'Credit' THEN amount ELSE 0 END) as deposits,
			SUM(CASE WHEN transaction_type = 'Debit' THEN amount ELSE 0 END) as withdrawals
		FROM tabBankTransaction
		WHERE status != 'Cancelled'
		GROUP BY bank_account
	`

	rows, err := s.db.Query(query)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var data []map[string]interface{}
	for rows.Next() {
		var bankAccount string
		var deposits, withdrawals float64
		if err := rows.Scan(&bankAccount, &deposits, &withdrawals); err != nil {
			continue
		}
		data = append(data, map[string]interface{}{
			"bank_account": bankAccount,
			"deposits":     deposits,
			"withdrawals":  withdrawals,
			"balance":      deposits - withdrawals,
		})
	}

	return &ReportResult{
		ReportType: "bank_summary",
		Data:       data,
		Columns: []ColumnInfo{
			{Field: "bank_account", Label: "Bank Account", Type: "Link", Width: 200},
			{Field: "deposits", Label: "Deposits", Type: "Currency", Width: 120},
			{Field: "withdrawals", Label: "Withdrawals", Type: "Currency", Width: 120},
			{Field: "balance", Label: "Balance", Type: "Currency", Width: 120},
		},
		GeneratedAt: time.Now(),
		Cached:      false,
	}, nil
}
