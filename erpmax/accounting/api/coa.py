import frappe
from frappe import _

GAAP_ACCOUNTS = [
 {
  "account_name": "1000 Assets",
  "root_type": "Asset",
  "is_group": 1
 },
 {
  "account_name": "1100 Cash and Cash Equivalents",
  "root_type": "Asset",
  "is_group": 1,
  "parent_account": "1000 Assets"
 },
 {
  "account_name": "1110 Cash - Operating",
  "root_type": "Asset",
  "is_group": 0,
  "parent_account": "1100 Cash and Cash Equivalents",
  "account_number": "1110"
 },
 {
  "account_name": "1120 Cash - Payroll",
  "root_type": "Asset",
  "is_group": 0,
  "parent_account": "1100 Cash and Cash Equivalents",
  "account_number": "1120"
 },
 {
  "account_name": "1130 Petty Cash",
  "root_type": "Asset",
  "is_group": 0,
  "parent_account": "1100 Cash and Cash Equivalents",
  "account_number": "1130"
 },
 {
  "account_name": "1140 Checking Account",
  "root_type": "Asset",
  "is_group": 0,
  "parent_account": "1100 Cash and Cash Equivalents",
  "account_number": "1140"
 },
 {
  "account_name": "1150 Savings Account",
  "root_type": "Asset",
  "is_group": 0,
  "parent_account": "1100 Cash and Cash Equivalents",
  "account_number": "1150"
 },
 {
  "account_name": "1200 Accounts Receivable",
  "root_type": "Asset",
  "is_group": 1,
  "parent_account": "1000 Assets"
 },
 {
  "account_name": "1210 Accounts Receivable - Trade",
  "root_type": "Asset",
  "is_group": 0,
  "parent_account": "1200 Accounts Receivable",
  "account_number": "1210"
 },
 {
  "account_name": "1220 Allowance for Doubtful Accounts",
  "root_type": "Asset",
  "is_group": 0,
  "parent_account": "1200 Accounts Receivable",
  "account_number": "1220"
 },
 {
  "account_name": "1230 Employee Receivables",
  "root_type": "Asset",
  "is_group": 0,
  "parent_account": "1200 Accounts Receivable",
  "account_number": "1230"
 },
 {
  "account_name": "1300 Inventory",
  "root_type": "Asset",
  "is_group": 1,
  "parent_account": "1000 Assets"
 },
 {
  "account_name": "1310 Raw Materials",
  "root_type": "Asset",
  "is_group": 0,
  "parent_account": "1300 Inventory",
  "account_number": "1310"
 },
 {
  "account_name": "1320 Work in Progress",
  "root_type": "Asset",
  "is_group": 0,
  "parent_account": "1300 Inventory",
  "account_number": "1320"
 },
 {
  "account_name": "1330 Finished Goods",
  "root_type": "Asset",
  "is_group": 0,
  "parent_account": "1300 Inventory",
  "account_number": "1330"
 },
 {
  "account_name": "1400 Prepaid Expenses",
  "root_type": "Asset",
  "is_group": 1,
  "parent_account": "1000 Assets"
 },
 {
  "account_name": "1410 Prepaid Insurance",
  "root_type": "Asset",
  "is_group": 0,
  "parent_account": "1400 Prepaid Expenses",
  "account_number": "1410"
 },
 {
  "account_name": "1420 Prepaid Rent",
  "root_type": "Asset",
  "is_group": 0,
  "parent_account": "1400 Prepaid Expenses",
  "account_number": "1420"
 },
 {
  "account_name": "1500 Fixed Assets",
  "root_type": "Asset",
  "is_group": 1,
  "parent_account": "1000 Assets"
 },
 {
  "account_name": "1510 Land",
  "root_type": "Asset",
  "is_group": 0,
  "parent_account": "1500 Fixed Assets",
  "account_number": "1510"
 },
 {
  "account_name": "1520 Buildings",
  "root_type": "Asset",
  "is_group": 0,
  "parent_account": "1500 Fixed Assets",
  "account_number": "1520"
 },
 {
  "account_name": "1530 Machinery and Equipment",
  "root_type": "Asset",
  "is_group": 0,
  "parent_account": "1500 Fixed Assets",
  "account_number": "1530"
 },
 {
  "account_name": "1540 Vehicles",
  "root_type": "Asset",
  "is_group": 0,
  "parent_account": "1500 Fixed Assets",
  "account_number": "1540"
 },
 {
  "account_name": "1550 Furniture and Fixtures",
  "root_type": "Asset",
  "is_group": 0,
  "parent_account": "1500 Fixed Assets",
  "account_number": "1550"
 },
 {
  "account_name": "1560 Computers and Software",
  "root_type": "Asset",
  "is_group": 0,
  "parent_account": "1500 Fixed Assets",
  "account_number": "1560"
 },
 {
  "account_name": "1600 Accumulated Depreciation",
  "root_type": "Asset",
  "is_group": 1,
  "parent_account": "1000 Assets"
 },
 {
  "account_name": "1610 Accum Dep - Buildings",
  "root_type": "Asset",
  "is_group": 0,
  "parent_account": "1600 Accumulated Depreciation",
  "account_number": "1610"
 },
 {
  "account_name": "1620 Accum Dep - Equipment",
  "root_type": "Asset",
  "is_group": 0,
  "parent_account": "1600 Accumulated Depreciation",
  "account_number": "1620"
 },
 {
  "account_name": "1630 Accum Dep - Vehicles",
  "root_type": "Asset",
  "is_group": 0,
  "parent_account": "1600 Accumulated Depreciation",
  "account_number": "1630"
 },
 {
  "account_name": "1700 Intangible Assets",
  "root_type": "Asset",
  "is_group": 1,
  "parent_account": "1000 Assets"
 },
 {
  "account_name": "1710 Goodwill",
  "root_type": "Asset",
  "is_group": 0,
  "parent_account": "1700 Intangible Assets",
  "account_number": "1710"
 },
 {
  "account_name": "1720 Patents",
  "root_type": "Asset",
  "is_group": 0,
  "parent_account": "1700 Intangible Assets",
  "account_number": "1720"
 },
 {
  "account_name": "1730 Trademarks",
  "root_type": "Asset",
  "is_group": 0,
  "parent_account": "1700 Intangible Assets",
  "account_number": "1730"
 },
 {
  "account_name": "1800 Other Assets",
  "root_type": "Asset",
  "is_group": 1,
  "parent_account": "1000 Assets"
 },
 {
  "account_name": "1810 Investments",
  "root_type": "Asset",
  "is_group": 0,
  "parent_account": "1800 Other Assets",
  "account_number": "1810"
 },
 {
  "account_name": "1820 Deposits",
  "root_type": "Asset",
  "is_group": 0,
  "parent_account": "1800 Other Assets",
  "account_number": "1820"
 },
 {
  "account_name": "2000 Liabilities",
  "root_type": "Liability",
  "is_group": 1
 },
 {
  "account_name": "2100 Accounts Payable",
  "root_type": "Liability",
  "is_group": 1,
  "parent_account": "2000 Liabilities"
 },
 {
  "account_name": "2110 Accounts Payable - Trade",
  "root_type": "Liability",
  "is_group": 0,
  "parent_account": "2100 Accounts Payable",
  "account_number": "2110"
 },
 {
  "account_name": "2120 Accrued Liabilities",
  "root_type": "Liability",
  "is_group": 0,
  "parent_account": "2100 Accounts Payable",
  "account_number": "2120"
 },
 {
  "account_name": "2200 Tax Payables",
  "root_type": "Liability",
  "is_group": 1,
  "parent_account": "2000 Liabilities"
 },
 {
  "account_name": "2210 VAT/Sales Tax Payable",
  "root_type": "Liability",
  "is_group": 0,
  "parent_account": "2200 Tax Payables",
  "account_number": "2210"
 },
 {
  "account_name": "2220 Income Tax Payable",
  "root_type": "Liability",
  "is_group": 0,
  "parent_account": "2200 Tax Payables",
  "account_number": "2220"
 },
 {
  "account_name": "2230 Payroll Tax Payable",
  "root_type": "Liability",
  "is_group": 0,
  "parent_account": "2200 Tax Payables",
  "account_number": "2230"
 },
 {
  "account_name": "2300 Accrued Expenses",
  "root_type": "Liability",
  "is_group": 1,
  "parent_account": "2000 Liabilities"
 },
 {
  "account_name": "2310 Accrued Salaries",
  "root_type": "Liability",
  "is_group": 0,
  "parent_account": "2300 Accrued Expenses",
  "account_number": "2310"
 },
 {
  "account_name": "2320 Accrued Interest",
  "root_type": "Liability",
  "is_group": 0,
  "parent_account": "2300 Accrued Expenses",
  "account_number": "2320"
 },
 {
  "account_name": "2400 Deferred Revenue",
  "root_type": "Liability",
  "is_group": 1,
  "parent_account": "2000 Liabilities"
 },
 {
  "account_name": "2410 Unearned Revenue",
  "root_type": "Liability",
  "is_group": 0,
  "parent_account": "2400 Deferred Revenue",
  "account_number": "2410"
 },
 {
  "account_name": "2500 Long Term Liabilities",
  "root_type": "Liability",
  "is_group": 1,
  "parent_account": "2000 Liabilities"
 },
 {
  "account_name": "2510 Bank Loans",
  "root_type": "Liability",
  "is_group": 0,
  "parent_account": "2500 Long Term Liabilities",
  "account_number": "2510"
 },
 {
  "account_name": "2520 Notes Payable",
  "root_type": "Liability",
  "is_group": 0,
  "parent_account": "2500 Long Term Liabilities",
  "account_number": "2520"
 },
 {
  "account_name": "2530 Bonds Payable",
  "root_type": "Liability",
  "is_group": 0,
  "parent_account": "2500 Long Term Liabilities",
  "account_number": "2530"
 },
 {
  "account_name": "3000 Equity",
  "root_type": "Equity",
  "is_group": 1
 },
 {
  "account_name": "3100 Common Stock",
  "root_type": "Equity",
  "is_group": 0,
  "parent_account": "3000 Equity",
  "account_number": "3100"
 },
 {
  "account_name": "3200 Additional Paid-in Capital",
  "root_type": "Equity",
  "is_group": 0,
  "parent_account": "3000 Equity",
  "account_number": "3200"
 },
 {
  "account_name": "3300 Retained Earnings",
  "root_type": "Equity",
  "is_group": 0,
  "parent_account": "3000 Equity",
  "account_number": "3300"
 },
 {
  "account_name": "3400 Current Year Earnings",
  "root_type": "Equity",
  "is_group": 0,
  "parent_account": "3000 Equity",
  "account_number": "3400"
 },
 {
  "account_name": "3500 Owner's Draws",
  "root_type": "Equity",
  "is_group": 0,
  "parent_account": "3000 Equity",
  "account_number": "3500"
 },
 {
  "account_name": "4000 Income",
  "root_type": "Income",
  "is_group": 1
 },
 {
  "account_name": "4100 Revenue",
  "root_type": "Income",
  "is_group": 1,
  "parent_account": "4000 Income"
 },
 {
  "account_name": "4110 Product Sales",
  "root_type": "Income",
  "is_group": 0,
  "parent_account": "4100 Revenue",
  "account_number": "4110"
 },
 {
  "account_name": "4120 Service Revenue",
  "root_type": "Income",
  "is_group": 0,
  "parent_account": "4100 Revenue",
  "account_number": "4120"
 },
 {
  "account_name": "4130 Interest Income",
  "root_type": "Income",
  "is_group": 0,
  "parent_account": "4100 Revenue",
  "account_number": "4130"
 },
 {
  "account_name": "4140 Rental Income",
  "root_type": "Income",
  "is_group": 0,
  "parent_account": "4100 Revenue",
  "account_number": "4140"
 },
 {
  "account_name": "4200 Other Income",
  "root_type": "Income",
  "is_group": 1,
  "parent_account": "4000 Income"
 },
 {
  "account_name": "4210 Gain on Sale of Assets",
  "root_type": "Income",
  "is_group": 0,
  "parent_account": "4200 Other Income",
  "account_number": "4210"
 },
 {
  "account_name": "4220 Foreign Exchange Gain",
  "root_type": "Income",
  "is_group": 0,
  "parent_account": "4200 Other Income",
  "account_number": "4220"
 },
 {
  "account_name": "5000 Expenses",
  "root_type": "Expense",
  "is_group": 1
 },
 {
  "account_name": "5100 Cost of Goods Sold",
  "root_type": "Expense",
  "is_group": 1,
  "parent_account": "5000 Expenses"
 },
 {
  "account_name": "5110 COGS - Materials",
  "root_type": "Expense",
  "is_group": 0,
  "parent_account": "5100 Cost of Goods Sold",
  "account_number": "5110"
 },
 {
  "account_name": "5120 COGS - Labor",
  "root_type": "Expense",
  "is_group": 0,
  "parent_account": "5100 Cost of Goods Sold",
  "account_number": "5120"
 },
 {
  "account_name": "5130 COGS - Overhead",
  "root_type": "Expense",
  "is_group": 0,
  "parent_account": "5100 Cost of Goods Sold",
  "account_number": "5130"
 },
 {
  "account_name": "5200 Salaries and Wages",
  "root_type": "Expense",
  "is_group": 0,
  "parent_account": "5000 Expenses",
  "account_number": "5200"
 },
 {
  "account_name": "5300 Rent and Utilities",
  "root_type": "Expense",
  "is_group": 1,
  "parent_account": "5000 Expenses"
 },
 {
  "account_name": "5310 Rent Expense",
  "root_type": "Expense",
  "is_group": 0,
  "parent_account": "5300 Rent and Utilities",
  "account_number": "5310"
 },
 {
  "account_name": "5320 Electricity",
  "root_type": "Expense",
  "is_group": 0,
  "parent_account": "5300 Rent and Utilities",
  "account_number": "5320"
 },
 {
  "account_name": "5330 Water and Gas",
  "root_type": "Expense",
  "is_group": 0,
  "parent_account": "5300 Rent and Utilities",
  "account_number": "5330"
 },
 {
  "account_name": "5340 Internet and Telephone",
  "root_type": "Expense",
  "is_group": 0,
  "parent_account": "5300 Rent and Utilities",
  "account_number": "5340"
 },
 {
  "account_name": "5400 Office and Admin",
  "root_type": "Expense",
  "is_group": 1,
  "parent_account": "5000 Expenses"
 },
 {
  "account_name": "5410 Office Supplies",
  "root_type": "Expense",
  "is_group": 0,
  "parent_account": "5400 Office and Admin",
  "account_number": "5410"
 },
 {
  "account_name": "5420 Insurance",
  "root_type": "Expense",
  "is_group": 0,
  "parent_account": "5400 Office and Admin",
  "account_number": "5420"
 },
 {
  "account_name": "5430 Legal and Professional",
  "root_type": "Expense",
  "is_group": 0,
  "parent_account": "5400 Office and Admin",
  "account_number": "5430"
 },
 {
  "account_name": "5440 Bank Charges",
  "root_type": "Expense",
  "is_group": 0,
  "parent_account": "5400 Office and Admin",
  "account_number": "5440"
 },
 {
  "account_name": "5500 Depreciation and Amortization",
  "root_type": "Expense",
  "is_group": 0,
  "parent_account": "5000 Expenses",
  "account_number": "5500"
 },
 {
  "account_name": "5600 Travel and Entertainment",
  "root_type": "Expense",
  "is_group": 1,
  "parent_account": "5000 Expenses"
 },
 {
  "account_name": "5610 Travel Expense",
  "root_type": "Expense",
  "is_group": 0,
  "parent_account": "5600 Travel and Entertainment",
  "account_number": "5610"
 },
 {
  "account_name": "5620 Meals and Entertainment",
  "root_type": "Expense",
  "is_group": 0,
  "parent_account": "5600 Travel and Entertainment",
  "account_number": "5620"
 },
 {
  "account_name": "5700 Marketing and Advertising",
  "root_type": "Expense",
  "is_group": 0,
  "parent_account": "5000 Expenses",
  "account_number": "5700"
 },
 {
  "account_name": "5800 Taxes and Licenses",
  "root_type": "Expense",
  "is_group": 0,
  "parent_account": "5000 Expenses",
  "account_number": "5800"
 },
 {
  "account_name": "5900 Other Expenses",
  "root_type": "Expense",
  "is_group": 1,
  "parent_account": "5000 Expenses"
 },
 {
  "account_name": "5910 Loss on Asset Disposal",
  "root_type": "Expense",
  "is_group": 0,
  "parent_account": "5900 Other Expenses",
  "account_number": "5910"
 },
 {
  "account_name": "5920 Foreign Exchange Loss",
  "root_type": "Expense",
  "is_group": 0,
  "parent_account": "5900 Other Expenses",
  "account_number": "5920"
 },
 {
  "account_name": "5990 Miscellaneous",
  "root_type": "Expense",
  "is_group": 0,
  "parent_account": "5900 Other Expenses",
  "account_number": "5990"
 }
]

IFRS_ACCOUNTS = [
 {
  "account_name": "Non-Current Assets",
  "root_type": "Asset",
  "is_group": 1
 },
 {
  "account_name": "Property, Plant and Equipment",
  "root_type": "Asset",
  "is_group": 1,
  "parent_account": "Non-Current Assets"
 },
 {
  "account_name": "Land and Buildings",
  "root_type": "Asset",
  "is_group": 0,
  "parent_account": "Property, Plant and Equipment"
 },
 {
  "account_name": "Plant and Machinery",
  "root_type": "Asset",
  "is_group": 0,
  "parent_account": "Property, Plant and Equipment"
 },
 {
  "account_name": "Fixtures and Fittings",
  "root_type": "Asset",
  "is_group": 0,
  "parent_account": "Property, Plant and Equipment"
 },
 {
  "account_name": "Right-of-Use Assets",
  "root_type": "Asset",
  "is_group": 0,
  "parent_account": "Non-Current Assets",
  "account_number": "IFRS16"
 },
 {
  "account_name": "Intangible Assets",
  "root_type": "Asset",
  "is_group": 1,
  "parent_account": "Non-Current Assets"
 },
 {
  "account_name": "Goodwill",
  "root_type": "Asset",
  "is_group": 0,
  "parent_account": "Intangible Assets"
 },
 {
  "account_name": "Patents and Trademarks",
  "root_type": "Asset",
  "is_group": 0,
  "parent_account": "Intangible Assets"
 },
 {
  "account_name": "Investments in Associates",
  "root_type": "Asset",
  "is_group": 0,
  "parent_account": "Non-Current Assets"
 },
 {
  "account_name": "Deferred Tax Assets",
  "root_type": "Asset",
  "is_group": 0,
  "parent_account": "Non-Current Assets"
 },
 {
  "account_name": "Current Assets",
  "root_type": "Asset",
  "is_group": 1
 },
 {
  "account_name": "Inventories",
  "root_type": "Asset",
  "is_group": 1,
  "parent_account": "Current Assets"
 },
 {
  "account_name": "Raw Materials",
  "root_type": "Asset",
  "is_group": 0,
  "parent_account": "Inventories"
 },
 {
  "account_name": "Work in Progress",
  "root_type": "Asset",
  "is_group": 0,
  "parent_account": "Inventories"
 },
 {
  "account_name": "Finished Goods",
  "root_type": "Asset",
  "is_group": 0,
  "parent_account": "Inventories"
 },
 {
  "account_name": "Trade Receivables",
  "root_type": "Asset",
  "is_group": 0,
  "parent_account": "Current Assets"
 },
 {
  "account_name": "Other Receivables",
  "root_type": "Asset",
  "is_group": 0,
  "parent_account": "Current Assets"
 },
 {
  "account_name": "Cash and Cash Equivalents",
  "root_type": "Asset",
  "is_group": 1,
  "parent_account": "Current Assets"
 },
 {
  "account_name": "Cash on Hand",
  "root_type": "Asset",
  "is_group": 0,
  "parent_account": "Cash and Cash Equivalents"
 },
 {
  "account_name": "Cash at Bank",
  "root_type": "Asset",
  "is_group": 0,
  "parent_account": "Cash and Cash Equivalents"
 },
 {
  "account_name": "Prepaid Expenses",
  "root_type": "Asset",
  "is_group": 0,
  "parent_account": "Current Assets"
 },
 {
  "account_name": "Current Tax Assets",
  "root_type": "Asset",
  "is_group": 0,
  "parent_account": "Current Assets"
 },
 {
  "account_name": "Equity",
  "root_type": "Equity",
  "is_group": 1
 },
 {
  "account_name": "Share Capital",
  "root_type": "Equity",
  "is_group": 0,
  "parent_account": "Equity"
 },
 {
  "account_name": "Share Premium",
  "root_type": "Equity",
  "is_group": 0,
  "parent_account": "Equity"
 },
 {
  "account_name": "Retained Earnings",
  "root_type": "Equity",
  "is_group": 0,
  "parent_account": "Equity"
 },
 {
  "account_name": "Revaluation Reserve",
  "root_type": "Equity",
  "is_group": 0,
  "parent_account": "Equity"
 },
 {
  "account_name": "Foreign Currency Translation Reserve",
  "root_type": "Equity",
  "is_group": 0,
  "parent_account": "Equity"
 },
 {
  "account_name": "Non-Controlling Interest",
  "root_type": "Equity",
  "is_group": 0,
  "parent_account": "Equity"
 },
 {
  "account_name": "Non-Current Liabilities",
  "root_type": "Liability",
  "is_group": 1
 },
 {
  "account_name": "Borrowings",
  "root_type": "Liability",
  "is_group": 0,
  "parent_account": "Non-Current Liabilities"
 },
 {
  "account_name": "Lease Liabilities",
  "root_type": "Liability",
  "is_group": 0,
  "parent_account": "Non-Current Liabilities"
 },
 {
  "account_name": "Deferred Tax Liabilities",
  "root_type": "Liability",
  "is_group": 0,
  "parent_account": "Non-Current Liabilities"
 },
 {
  "account_name": "Provisions",
  "root_type": "Liability",
  "is_group": 0,
  "parent_account": "Non-Current Liabilities"
 },
 {
  "account_name": "Current Liabilities",
  "root_type": "Liability",
  "is_group": 1
 },
 {
  "account_name": "Trade Payables",
  "root_type": "Liability",
  "is_group": 0,
  "parent_account": "Current Liabilities"
 },
 {
  "account_name": "Accrued Expenses",
  "root_type": "Liability",
  "is_group": 0,
  "parent_account": "Current Liabilities"
 },
 {
  "account_name": "Current Tax Payable",
  "root_type": "Liability",
  "is_group": 0,
  "parent_account": "Current Liabilities"
 },
 {
  "account_name": "VAT Payable",
  "root_type": "Liability",
  "is_group": 0,
  "parent_account": "Current Liabilities"
 },
 {
  "account_name": "Deferred Revenue",
  "root_type": "Liability",
  "is_group": 0,
  "parent_account": "Current Liabilities"
 },
 {
  "account_name": "Income",
  "root_type": "Income",
  "is_group": 1
 },
 {
  "account_name": "Revenue",
  "root_type": "Income",
  "is_group": 1,
  "parent_account": "Income"
 },
 {
  "account_name": "Sales of Goods",
  "root_type": "Income",
  "is_group": 0,
  "parent_account": "Revenue"
 },
 {
  "account_name": "Rendering of Services",
  "root_type": "Income",
  "is_group": 0,
  "parent_account": "Revenue"
 },
 {
  "account_name": "Interest Income",
  "root_type": "Income",
  "is_group": 0,
  "parent_account": "Income"
 },
 {
  "account_name": "Other Income",
  "root_type": "Income",
  "is_group": 0,
  "parent_account": "Income"
 },
 {
  "account_name": "Expenses",
  "root_type": "Expense",
  "is_group": 1
 },
 {
  "account_name": "Cost of Sales",
  "root_type": "Expense",
  "is_group": 0,
  "parent_account": "Expenses"
 },
 {
  "account_name": "Distribution Costs",
  "root_type": "Expense",
  "is_group": 0,
  "parent_account": "Expenses"
 },
 {
  "account_name": "Administrative Expenses",
  "root_type": "Expense",
  "is_group": 1,
  "parent_account": "Expenses"
 },
 {
  "account_name": "Salaries",
  "root_type": "Expense",
  "is_group": 0,
  "parent_account": "Administrative Expenses"
 },
 {
  "account_name": "Rent",
  "root_type": "Expense",
  "is_group": 0,
  "parent_account": "Administrative Expenses"
 },
 {
  "account_name": "Utilities",
  "root_type": "Expense",
  "is_group": 0,
  "parent_account": "Administrative Expenses"
 },
 {
  "account_name": "Office Expenses",
  "root_type": "Expense",
  "is_group": 0,
  "parent_account": "Administrative Expenses"
 },
 {
  "account_name": "Professional Fees",
  "root_type": "Expense",
  "is_group": 0,
  "parent_account": "Administrative Expenses"
 },
 {
  "account_name": "Depreciation",
  "root_type": "Expense",
  "is_group": 0,
  "parent_account": "Expenses"
 },
 {
  "account_name": "Amortization",
  "root_type": "Expense",
  "is_group": 0,
  "parent_account": "Expenses"
 },
 {
  "account_name": "Finance Costs",
  "root_type": "Expense",
  "is_group": 0,
  "parent_account": "Expenses"
 },
 {
  "account_name": "Income Tax Expense",
  "root_type": "Expense",
  "is_group": 0,
  "parent_account": "Expenses"
 }
]

UK_ACCOUNTS = [
 {
  "account_name": "Fixed Assets",
  "root_type": "Asset",
  "is_group": 1
 },
 {
  "account_name": "Tangible Assets",
  "root_type": "Asset",
  "is_group": 1,
  "parent_account": "Fixed Assets"
 },
 {
  "account_name": "Freehold Property",
  "root_type": "Asset",
  "is_group": 0,
  "parent_account": "Tangible Assets"
 },
 {
  "account_name": "Leasehold Improvements",
  "root_type": "Asset",
  "is_group": 0,
  "parent_account": "Tangible Assets"
 },
 {
  "account_name": "Plant and Machinery",
  "root_type": "Asset",
  "is_group": 0,
  "parent_account": "Tangible Assets"
 },
 {
  "account_name": "Office Equipment",
  "root_type": "Asset",
  "is_group": 0,
  "parent_account": "Tangible Assets"
 },
 {
  "account_name": "Motor Vehicles",
  "root_type": "Asset",
  "is_group": 0,
  "parent_account": "Tangible Assets"
 },
 {
  "account_name": "Intangible Assets",
  "root_type": "Asset",
  "is_group": 1,
  "parent_account": "Fixed Assets"
 },
 {
  "account_name": "Goodwill",
  "root_type": "Asset",
  "is_group": 0,
  "parent_account": "Intangible Assets"
 },
 {
  "account_name": "Software",
  "root_type": "Asset",
  "is_group": 0,
  "parent_account": "Intangible Assets"
 },
 {
  "account_name": "Investments",
  "root_type": "Asset",
  "is_group": 0,
  "parent_account": "Fixed Assets"
 },
 {
  "account_name": "Current Assets",
  "root_type": "Asset",
  "is_group": 1
 },
 {
  "account_name": "Stock",
  "root_type": "Asset",
  "is_group": 0,
  "parent_account": "Current Assets"
 },
 {
  "account_name": "Debtors",
  "root_type": "Asset",
  "is_group": 1,
  "parent_account": "Current Assets"
 },
 {
  "account_name": "Trade Debtors",
  "root_type": "Asset",
  "is_group": 0,
  "parent_account": "Debtors"
 },
 {
  "account_name": "Prepayments",
  "root_type": "Asset",
  "is_group": 0,
  "parent_account": "Debtors"
 },
 {
  "account_name": "Other Debtors",
  "root_type": "Asset",
  "is_group": 0,
  "parent_account": "Debtors"
 },
 {
  "account_name": "Cash at Bank",
  "root_type": "Asset",
  "is_group": 0,
  "parent_account": "Current Assets"
 },
 {
  "account_name": "Cash in Hand",
  "root_type": "Asset",
  "is_group": 0,
  "parent_account": "Current Assets"
 },
 {
  "account_name": "Creditors: Amounts Falling Due Within One Year",
  "root_type": "Liability",
  "is_group": 1
 },
 {
  "account_name": "Trade Creditors",
  "root_type": "Liability",
  "is_group": 0,
  "parent_account": "Creditors: Amounts Falling Due Within One Year"
 },
 {
  "account_name": "Accruals",
  "root_type": "Liability",
  "is_group": 0,
  "parent_account": "Creditors: Amounts Falling Due Within One Year"
 },
 {
  "account_name": "VAT Liability",
  "root_type": "Liability",
  "is_group": 0,
  "parent_account": "Creditors: Amounts Falling Due Within One Year"
 },
 {
  "account_name": "PAYE/NI Liability",
  "root_type": "Liability",
  "is_group": 0,
  "parent_account": "Creditors: Amounts Falling Due Within One Year"
 },
 {
  "account_name": "Corporation Tax Payable",
  "root_type": "Liability",
  "is_group": 0,
  "parent_account": "Creditors: Amounts Falling Due Within One Year"
 },
 {
  "account_name": "Deferred Income",
  "root_type": "Liability",
  "is_group": 0,
  "parent_account": "Creditors: Amounts Falling Due Within One Year"
 },
 {
  "account_name": "Creditors: Amounts Falling Due After One Year",
  "root_type": "Liability",
  "is_group": 1
 },
 {
  "account_name": "Bank Loans",
  "root_type": "Liability",
  "is_group": 0,
  "parent_account": "Creditors: Amounts Falling Due After One Year"
 },
 {
  "account_name": "Hire Purchase Creditors",
  "root_type": "Liability",
  "is_group": 0,
  "parent_account": "Creditors: Amounts Falling Due After One Year"
 },
 {
  "account_name": "Provisions for Liabilities",
  "root_type": "Liability",
  "is_group": 0,
  "parent_account": "Creditors: Amounts Falling Due After One Year"
 },
 {
  "account_name": "Capital and Reserves",
  "root_type": "Equity",
  "is_group": 1
 },
 {
  "account_name": "Called Up Share Capital",
  "root_type": "Equity",
  "is_group": 0,
  "parent_account": "Capital and Reserves"
 },
 {
  "account_name": "Share Premium Account",
  "root_type": "Equity",
  "is_group": 0,
  "parent_account": "Capital and Reserves"
 },
 {
  "account_name": "Profit and Loss Account",
  "root_type": "Equity",
  "is_group": 0,
  "parent_account": "Capital and Reserves"
 },
 {
  "account_name": "Revaluation Reserve",
  "root_type": "Equity",
  "is_group": 0,
  "parent_account": "Capital and Reserves"
 },
 {
  "account_name": "Capital Redemption Reserve",
  "root_type": "Equity",
  "is_group": 0,
  "parent_account": "Capital and Reserves"
 },
 {
  "account_name": "Turnover",
  "root_type": "Income",
  "is_group": 1
 },
 {
  "account_name": "Sales - UK",
  "root_type": "Income",
  "is_group": 0,
  "parent_account": "Turnover"
 },
 {
  "account_name": "Service Revenue",
  "root_type": "Income",
  "is_group": 0,
  "parent_account": "Turnover"
 },
 {
  "account_name": "Other Income",
  "root_type": "Income",
  "is_group": 0,
  "parent_account": "Turnover"
 },
 {
  "account_name": "Cost of Sales",
  "root_type": "Expense",
  "is_group": 1
 },
 {
  "account_name": "Cost of Materials",
  "root_type": "Expense",
  "is_group": 0,
  "parent_account": "Cost of Sales"
 },
 {
  "account_name": "Direct Labour",
  "root_type": "Expense",
  "is_group": 0,
  "parent_account": "Cost of Sales"
 },
 {
  "account_name": "Other Direct Costs",
  "root_type": "Expense",
  "is_group": 0,
  "parent_account": "Cost of Sales"
 },
 {
  "account_name": "Gross Profit/(Loss)",
  "root_type": "Expense",
  "is_group": 1
 },
 {
  "account_name": "Administrative Expenses",
  "root_type": "Expense",
  "is_group": 1,
  "parent_account": "Gross Profit/(Loss)"
 },
 {
  "account_name": "Wages and Salaries",
  "root_type": "Expense",
  "is_group": 0,
  "parent_account": "Administrative Expenses"
 },
 {
  "account_name": "Directors Remuneration",
  "root_type": "Expense",
  "is_group": 0,
  "parent_account": "Administrative Expenses"
 },
 {
  "account_name": "Rent and Rates",
  "root_type": "Expense",
  "is_group": 0,
  "parent_account": "Administrative Expenses"
 },
 {
  "account_name": "Heat, Light and Power",
  "root_type": "Expense",
  "is_group": 0,
  "parent_account": "Administrative Expenses"
 },
 {
  "account_name": "Telephone and Internet",
  "root_type": "Expense",
  "is_group": 0,
  "parent_account": "Administrative Expenses"
 },
 {
  "account_name": "Printing, Postage and Stationery",
  "root_type": "Expense",
  "is_group": 0,
  "parent_account": "Administrative Expenses"
 },
 {
  "account_name": "Insurance",
  "root_type": "Expense",
  "is_group": 0,
  "parent_account": "Administrative Expenses"
 },
 {
  "account_name": "Professional Fees",
  "root_type": "Expense",
  "is_group": 0,
  "parent_account": "Administrative Expenses"
 },
 {
  "account_name": "Depreciation",
  "root_type": "Expense",
  "is_group": 0,
  "parent_account": "Administrative Expenses"
 },
 {
  "account_name": "Amortisation",
  "root_type": "Expense",
  "is_group": 0,
  "parent_account": "Administrative Expenses"
 },
 {
  "account_name": "Finance Costs",
  "root_type": "Expense",
  "is_group": 1,
  "parent_account": "Gross Profit/(Loss)"
 },
 {
  "account_name": "Bank Charges",
  "root_type": "Expense",
  "is_group": 0,
  "parent_account": "Finance Costs"
 },
 {
  "account_name": "Interest Payable",
  "root_type": "Expense",
  "is_group": 0,
  "parent_account": "Finance Costs"
 },
 {
  "account_name": "Taxation",
  "root_type": "Expense",
  "is_group": 0,
  "parent_account": "Gross Profit/(Loss)"
 }
]

SKR03_ACCOUNTS = [
 {
  "account_name": "Aktivkonten",
  "root_type": "Asset",
  "is_group": 1
 },
 {
  "account_name": "Anlagevermögen",
  "root_type": "Asset",
  "is_group": 1,
  "parent_account": "Aktivkonten"
 },
 {
  "account_name": "Grundstücke und Bauten",
  "root_type": "Asset",
  "is_group": 0,
  "parent_account": "Anlagevermögen",
  "account_number": "0050"
 },
 {
  "account_name": "Maschinen",
  "root_type": "Asset",
  "is_group": 0,
  "parent_account": "Anlagevermögen",
  "account_number": "0200"
 },
 {
  "account_name": "Betriebsausstattung",
  "root_type": "Asset",
  "is_group": 0,
  "parent_account": "Anlagevermögen",
  "account_number": "0400"
 },
 {
  "account_name": "Fuhrpark",
  "root_type": "Asset",
  "is_group": 0,
  "parent_account": "Anlagevermögen",
  "account_number": "0500"
 },
 {
  "account_name": "Büroeinrichtung",
  "root_type": "Asset",
  "is_group": 0,
  "parent_account": "Anlagevermögen",
  "account_number": "0600"
 },
 {
  "account_name": "EDV-Anlagen",
  "root_type": "Asset",
  "is_group": 0,
  "parent_account": "Anlagevermögen",
  "account_number": "0630"
 },
 {
  "account_name": "Immaterielle Vermögensgegenstände",
  "root_type": "Asset",
  "is_group": 1,
  "parent_account": "Anlagevermögen"
 },
 {
  "account_name": "Konzessionen und Lizenzen",
  "root_type": "Asset",
  "is_group": 0,
  "parent_account": "Immaterielle Vermögensgegenstände",
  "account_number": "0005"
 },
 {
  "account_name": "Geschäfts- oder Firmenwert",
  "root_type": "Asset",
  "is_group": 0,
  "parent_account": "Immaterielle Vermögensgegenstände",
  "account_number": "0010"
 },
 {
  "account_name": "Umlaufvermögen",
  "root_type": "Asset",
  "is_group": 1,
  "parent_account": "Aktivkonten"
 },
 {
  "account_name": "Kasse",
  "root_type": "Asset",
  "is_group": 0,
  "parent_account": "Umlaufvermögen",
  "account_number": "1000"
 },
 {
  "account_name": "Bank",
  "root_type": "Asset",
  "is_group": 0,
  "parent_account": "Umlaufvermögen",
  "account_number": "1200"
 },
 {
  "account_name": "Forderungen aus Lieferungen und Leistungen",
  "root_type": "Asset",
  "is_group": 0,
  "parent_account": "Umlaufvermögen",
  "account_number": "1400"
 },
 {
  "account_name": "Sonstige Vermögensgegenstände",
  "root_type": "Asset",
  "is_group": 0,
  "parent_account": "Umlaufvermögen",
  "account_number": "1500"
 },
 {
  "account_name": "Vorräte",
  "root_type": "Asset",
  "is_group": 1,
  "parent_account": "Umlaufvermögen"
 },
 {
  "account_name": "Rohstoffe",
  "root_type": "Asset",
  "is_group": 0,
  "parent_account": "Vorräte",
  "account_number": "2000"
 },
 {
  "account_name": "Fertige Erzeugnisse",
  "root_type": "Asset",
  "is_group": 0,
  "parent_account": "Vorräte",
  "account_number": "2100"
 },
 {
  "account_name": "Aktive Rechnungsabgrenzung",
  "root_type": "Asset",
  "is_group": 0,
  "parent_account": "Umlaufvermögen",
  "account_number": "1900"
 },
 {
  "account_name": "Passivkonten",
  "root_type": "Liability",
  "is_group": 1
 },
 {
  "account_name": "Eigenkapital",
  "root_type": "Liability",
  "is_group": 1,
  "parent_account": "Passivkonten"
 },
 {
  "account_name": "Gezeichnetes Kapital",
  "root_type": "Equity",
  "is_group": 0,
  "parent_account": "Eigenkapital",
  "account_number": "2900"
 },
 {
  "account_name": "Kapitalrücklage",
  "root_type": "Equity",
  "is_group": 0,
  "parent_account": "Eigenkapital",
  "account_number": "2930"
 },
 {
  "account_name": "Gewinnrücklagen",
  "root_type": "Equity",
  "is_group": 0,
  "parent_account": "Eigenkapital",
  "account_number": "2970"
 },
 {
  "account_name": "Jahresüberschuss/Jahresfehlbetrag",
  "root_type": "Equity",
  "is_group": 0,
  "parent_account": "Eigenkapital",
  "account_number": "2990"
 },
 {
  "account_name": "Rückstellungen",
  "root_type": "Liability",
  "is_group": 1,
  "parent_account": "Passivkonten"
 },
 {
  "account_name": "Rückstellungen für Pensionen",
  "root_type": "Liability",
  "is_group": 0,
  "parent_account": "Rückstellungen",
  "account_number": "2400"
 },
 {
  "account_name": "Steuerrückstellungen",
  "root_type": "Liability",
  "is_group": 0,
  "parent_account": "Rückstellungen",
  "account_number": "2450"
 },
 {
  "account_name": "Sonstige Rückstellungen",
  "root_type": "Liability",
  "is_group": 0,
  "parent_account": "Rückstellungen",
  "account_number": "2480"
 },
 {
  "account_name": "Verbindlichkeiten",
  "root_type": "Liability",
  "is_group": 1,
  "parent_account": "Passivkonten"
 },
 {
  "account_name": "Verbindlichkeiten aus L+L",
  "root_type": "Liability",
  "is_group": 0,
  "parent_account": "Verbindlichkeiten",
  "account_number": "3300"
 },
 {
  "account_name": "Verbindlichkeiten ggü. Kreditinstituten",
  "root_type": "Liability",
  "is_group": 0,
  "parent_account": "Verbindlichkeiten",
  "account_number": "3400"
 },
 {
  "account_name": "Erhaltene Anzahlungen",
  "root_type": "Liability",
  "is_group": 0,
  "parent_account": "Verbindlichkeiten",
  "account_number": "3500"
 },
 {
  "account_name": "Verbindlichkeiten aus Steuern",
  "root_type": "Liability",
  "is_group": 0,
  "parent_account": "Verbindlichkeiten",
  "account_number": "3600"
 },
 {
  "account_name": "Umsatzsteuer 19%",
  "root_type": "Liability",
  "is_group": 0,
  "parent_account": "Verbindlichkeiten",
  "account_number": "3800",
  "tax_rate": 19
 },
 {
  "account_name": "Umsatzsteuer 7%",
  "root_type": "Liability",
  "is_group": 0,
  "parent_account": "Verbindlichkeiten",
  "account_number": "3806",
  "tax_rate": 7
 },
 {
  "account_name": "Passive Rechnungsabgrenzung",
  "root_type": "Liability",
  "is_group": 0,
  "parent_account": "Passivkonten",
  "account_number": "3900"
 },
 {
  "account_name": "Erträge",
  "root_type": "Income",
  "is_group": 1
 },
 {
  "account_name": "Betriebliche Erträge",
  "root_type": "Income",
  "is_group": 1,
  "parent_account": "Erträge"
 },
 {
  "account_name": "Umsatzerlöse 19%",
  "root_type": "Income",
  "is_group": 0,
  "parent_account": "Betriebliche Erträge",
  "account_number": "8000",
  "tax_rate": 19
 },
 {
  "account_name": "Umsatzerlöse 7%",
  "root_type": "Income",
  "is_group": 0,
  "parent_account": "Betriebliche Erträge",
  "account_number": "8100",
  "tax_rate": 7
 },
 {
  "account_name": "Umsatzerlöse steuerfrei",
  "root_type": "Income",
  "is_group": 0,
  "parent_account": "Betriebliche Erträge",
  "account_number": "8200"
 },
 {
  "account_name": "Bestandsveränderungen",
  "root_type": "Income",
  "is_group": 0,
  "parent_account": "Betriebliche Erträge",
  "account_number": "8400"
 },
 {
  "account_name": "Sonstige betriebliche Erträge",
  "root_type": "Income",
  "is_group": 0,
  "parent_account": "Betriebliche Erträge",
  "account_number": "8500"
 },
 {
  "account_name": "Nicht betriebliche Erträge",
  "root_type": "Income",
  "is_group": 0,
  "parent_account": "Erträge",
  "account_number": "8600"
 },
 {
  "account_name": "Aufwendungen",
  "root_type": "Expense",
  "is_group": 1
 },
 {
  "account_name": "Materialaufwand",
  "root_type": "Expense",
  "is_group": 1,
  "parent_account": "Aufwendungen"
 },
 {
  "account_name": "Wareneingang",
  "root_type": "Expense",
  "is_group": 0,
  "parent_account": "Materialaufwand",
  "account_number": "5000"
 },
 {
  "account_name": "Bezogene Leistungen",
  "root_type": "Expense",
  "is_group": 0,
  "parent_account": "Materialaufwand",
  "account_number": "5100"
 },
 {
  "account_name": "Personalkosten",
  "root_type": "Expense",
  "is_group": 1,
  "parent_account": "Aufwendungen"
 },
 {
  "account_name": "Gehälter",
  "root_type": "Expense",
  "is_group": 0,
  "parent_account": "Personalkosten",
  "account_number": "6100"
 },
 {
  "account_name": "Löhne",
  "root_type": "Expense",
  "is_group": 0,
  "parent_account": "Personalkosten",
  "account_number": "6000"
 },
 {
  "account_name": "Sozialversicherung",
  "root_type": "Expense",
  "is_group": 0,
  "parent_account": "Personalkosten",
  "account_number": "6130"
 },
 {
  "account_name": "Abschreibungen",
  "root_type": "Expense",
  "is_group": 0,
  "parent_account": "Aufwendungen",
  "account_number": "6500"
 },
 {
  "account_name": "Betriebliche Aufwendungen",
  "root_type": "Expense",
  "is_group": 1,
  "parent_account": "Aufwendungen"
 },
 {
  "account_name": "Miete",
  "root_type": "Expense",
  "is_group": 0,
  "parent_account": "Betriebliche Aufwendungen",
  "account_number": "4100"
 },
 {
  "account_name": "Bürobedarf",
  "root_type": "Expense",
  "is_group": 0,
  "parent_account": "Betriebliche Aufwendungen",
  "account_number": "4900"
 },
 {
  "account_name": "Versicherungen",
  "root_type": "Expense",
  "is_group": 0,
  "parent_account": "Betriebliche Aufwendungen",
  "account_number": "4350"
 },
 {
  "account_name": "Reisekosten",
  "root_type": "Expense",
  "is_group": 0,
  "parent_account": "Betriebliche Aufwendungen",
  "account_number": "4650"
 },
 {
  "account_name": "Fortbildung",
  "root_type": "Expense",
  "is_group": 0,
  "parent_account": "Betriebliche Aufwendungen",
  "account_number": "4520"
 },
 {
  "account_name": "Rechts- und Beratungskosten",
  "root_type": "Expense",
  "is_group": 0,
  "parent_account": "Betriebliche Aufwendungen",
  "account_number": "4800"
 },
 {
  "account_name": "Werbekosten",
  "root_type": "Expense",
  "is_group": 0,
  "parent_account": "Betriebliche Aufwendungen",
  "account_number": "4600"
 },
 {
  "account_name": "Telefon und Internet",
  "root_type": "Expense",
  "is_group": 0,
  "parent_account": "Betriebliche Aufwendungen",
  "account_number": "4920"
 },
 {
  "account_name": "Kfz-Kosten",
  "root_type": "Expense",
  "is_group": 0,
  "parent_account": "Betriebliche Aufwendungen",
  "account_number": "4550"
 },
 {
  "account_name": "Finanzaufwendungen",
  "root_type": "Expense",
  "is_group": 1,
  "parent_account": "Aufwendungen"
 },
 {
  "account_name": "Zinsen und ähnliche Aufwendungen",
  "root_type": "Expense",
  "is_group": 0,
  "parent_account": "Finanzaufwendungen",
  "account_number": "7300"
 },
 {
  "account_name": "Bankgebühren",
  "root_type": "Expense",
  "is_group": 0,
  "parent_account": "Finanzaufwendungen",
  "account_number": "7500"
 },
 {
  "account_name": "Steuern",
  "root_type": "Expense",
  "is_group": 0,
  "parent_account": "Aufwendungen",
  "account_number": "7600"
 }
]

PCG_ACCOUNTS = [
 {
  "account_name": "Comptes de Actif",
  "root_type": "Asset",
  "is_group": 1
 },
 {
  "account_name": "Actif Immobilisé",
  "root_type": "Asset",
  "is_group": 1,
  "parent_account": "Comptes de Actif"
 },
 {
  "account_name": "Immobilisations Incorporelles",
  "root_type": "Asset",
  "is_group": 1,
  "parent_account": "Actif Immobilisé"
 },
 {
  "account_name": "Frais d'Établissement",
  "root_type": "Asset",
  "is_group": 0,
  "parent_account": "Immobilisations Incorporelles",
  "account_number": "201"
 },
 {
  "account_name": "Logiciels",
  "root_type": "Asset",
  "is_group": 0,
  "parent_account": "Immobilisations Incorporelles",
  "account_number": "205"
 },
 {
  "account_name": "Immobilisations Corporelles",
  "root_type": "Asset",
  "is_group": 1,
  "parent_account": "Actif Immobilisé"
 },
 {
  "account_name": "Terrains",
  "root_type": "Asset",
  "is_group": 0,
  "parent_account": "Immobilisations Corporelles",
  "account_number": "211"
 },
 {
  "account_name": "Constructions",
  "root_type": "Asset",
  "is_group": 0,
  "parent_account": "Immobilisations Corporelles",
  "account_number": "213"
 },
 {
  "account_name": "Installations Techniques",
  "root_type": "Asset",
  "is_group": 0,
  "parent_account": "Immobilisations Corporelles",
  "account_number": "215"
 },
 {
  "account_name": "Matériel de Bureau",
  "root_type": "Asset",
  "is_group": 0,
  "parent_account": "Immobilisations Corporelles",
  "account_number": "218"
 },
 {
  "account_name": "Matériel Informatique",
  "root_type": "Asset",
  "is_group": 0,
  "parent_account": "Immobilisations Corporelles",
  "account_number": "2183"
 },
 {
  "account_name": "Mobilier",
  "root_type": "Asset",
  "is_group": 0,
  "parent_account": "Immobilisations Corporelles",
  "account_number": "2184"
 },
 {
  "account_name": "Amortissements",
  "root_type": "Asset",
  "is_group": 1,
  "parent_account": "Actif Immobilisé"
 },
 {
  "account_name": "Amortissements des Constructions",
  "root_type": "Asset",
  "is_group": 0,
  "parent_account": "Amortissements",
  "account_number": "2813"
 },
 {
  "account_name": "Amortissements du Matériel",
  "root_type": "Asset",
  "is_group": 0,
  "parent_account": "Amortissements",
  "account_number": "2815"
 },
 {
  "account_name": "Actif Circulant",
  "root_type": "Asset",
  "is_group": 1,
  "parent_account": "Comptes de Actif"
 },
 {
  "account_name": "Stocks",
  "root_type": "Asset",
  "is_group": 1,
  "parent_account": "Actif Circulant"
 },
 {
  "account_name": "Matières Premières",
  "root_type": "Asset",
  "is_group": 0,
  "parent_account": "Stocks",
  "account_number": "31"
 },
 {
  "account_name": "Produits Finis",
  "root_type": "Asset",
  "is_group": 0,
  "parent_account": "Stocks",
  "account_number": "35"
 },
 {
  "account_name": "Créances",
  "root_type": "Asset",
  "is_group": 1,
  "parent_account": "Actif Circulant"
 },
 {
  "account_name": "Clients",
  "root_type": "Asset",
  "is_group": 0,
  "parent_account": "Créances",
  "account_number": "411"
 },
 {
  "account_name": "Créances Sociales",
  "root_type": "Asset",
  "is_group": 0,
  "parent_account": "Créances",
  "account_number": "421"
 },
 {
  "account_name": "Trésorerie",
  "root_type": "Asset",
  "is_group": 1,
  "parent_account": "Actif Circulant"
 },
 {
  "account_name": "Caisse",
  "root_type": "Asset",
  "is_group": 0,
  "parent_account": "Trésorerie",
  "account_number": "53"
 },
 {
  "account_name": "Banque",
  "root_type": "Asset",
  "is_group": 0,
  "parent_account": "Trésorerie",
  "account_number": "512"
 },
 {
  "account_name": "Charges Constatées d'Avance",
  "root_type": "Asset",
  "is_group": 0,
  "parent_account": "Actif Circulant",
  "account_number": "486"
 },
 {
  "account_name": "Comptes de Passif",
  "root_type": "Liability",
  "is_group": 1
 },
 {
  "account_name": "Provisions",
  "root_type": "Liability",
  "is_group": 1,
  "parent_account": "Comptes de Passif"
 },
 {
  "account_name": "Provisions pour Risques",
  "root_type": "Liability",
  "is_group": 0,
  "parent_account": "Provisions",
  "account_number": "151"
 },
 {
  "account_name": "Provisions pour Charges",
  "root_type": "Liability",
  "is_group": 0,
  "parent_account": "Provisions",
  "account_number": "153"
 },
 {
  "account_name": "Dettes",
  "root_type": "Liability",
  "is_group": 1,
  "parent_account": "Comptes de Passif"
 },
 {
  "account_name": "Fournisseurs",
  "root_type": "Liability",
  "is_group": 0,
  "parent_account": "Dettes",
  "account_number": "401"
 },
 {
  "account_name": "Dettes Sociales",
  "root_type": "Liability",
  "is_group": 0,
  "parent_account": "Dettes",
  "account_number": "431"
 },
 {
  "account_name": "Dettes Fiscales",
  "root_type": "Liability",
  "is_group": 0,
  "parent_account": "Dettes",
  "account_number": "44"
 },
 {
  "account_name": "TVA à Décaisser",
  "root_type": "Liability",
  "is_group": 0,
  "parent_account": "Dettes Fiscales",
  "account_number": "445"
 },
 {
  "account_name": "Emprunts",
  "root_type": "Liability",
  "is_group": 0,
  "parent_account": "Comptes de Passif",
  "account_number": "164"
 },
 {
  "account_name": "Capitaux Propres",
  "root_type": "Equity",
  "is_group": 1
 },
 {
  "account_name": "Capital Social",
  "root_type": "Equity",
  "is_group": 0,
  "parent_account": "Capitaux Propres",
  "account_number": "101"
 },
 {
  "account_name": "Prime d'Émission",
  "root_type": "Equity",
  "is_group": 0,
  "parent_account": "Capitaux Propres",
  "account_number": "104"
 },
 {
  "account_name": "Réserves",
  "root_type": "Equity",
  "is_group": 0,
  "parent_account": "Capitaux Propres",
  "account_number": "106"
 },
 {
  "account_name": "Report à Nouveau",
  "root_type": "Equity",
  "is_group": 0,
  "parent_account": "Capitaux Propres",
  "account_number": "110"
 },
 {
  "account_name": "Résultat de l'Exercice",
  "root_type": "Equity",
  "is_group": 0,
  "parent_account": "Capitaux Propres",
  "account_number": "120"
 },
 {
  "account_name": "Comptes de Charges",
  "root_type": "Expense",
  "is_group": 1
 },
 {
  "account_name": "Achats",
  "root_type": "Expense",
  "is_group": 0,
  "parent_account": "Comptes de Charges",
  "account_number": "601"
 },
 {
  "account_name": "Charges Externes",
  "root_type": "Expense",
  "is_group": 1,
  "parent_account": "Comptes de Charges"
 },
 {
  "account_name": "Loyers",
  "root_type": "Expense",
  "is_group": 0,
  "parent_account": "Charges Externes",
  "account_number": "613"
 },
 {
  "account_name": "Honoraires",
  "root_type": "Expense",
  "is_group": 0,
  "parent_account": "Charges Externes",
  "account_number": "622"
 },
 {
  "account_name": "Publicité",
  "root_type": "Expense",
  "is_group": 0,
  "parent_account": "Charges Externes",
  "account_number": "623"
 },
 {
  "account_name": "Transports",
  "root_type": "Expense",
  "is_group": 0,
  "parent_account": "Charges Externes",
  "account_number": "624"
 },
 {
  "account_name": "Frais de Téléphone",
  "root_type": "Expense",
  "is_group": 0,
  "parent_account": "Charges Externes",
  "account_number": "626"
 },
 {
  "account_name": "Frais Bancaires",
  "root_type": "Expense",
  "is_group": 0,
  "parent_account": "Charges Externes",
  "account_number": "627"
 },
 {
  "account_name": "Charges de Personnel",
  "root_type": "Expense",
  "is_group": 1,
  "parent_account": "Comptes de Charges"
 },
 {
  "account_name": "Salaires",
  "root_type": "Expense",
  "is_group": 0,
  "parent_account": "Charges de Personnel",
  "account_number": "641"
 },
 {
  "account_name": "Charges Sociales",
  "root_type": "Expense",
  "is_group": 0,
  "parent_account": "Charges de Personnel",
  "account_number": "645"
 },
 {
  "account_name": "Impôts et Taxes",
  "root_type": "Expense",
  "is_group": 0,
  "parent_account": "Comptes de Charges",
  "account_number": "635"
 },
 {
  "account_name": "Dotations aux Amortissements",
  "root_type": "Expense",
  "is_group": 0,
  "parent_account": "Comptes de Charges",
  "account_number": "681"
 },
 {
  "account_name": "Intérêts et Charges Financières",
  "root_type": "Expense",
  "is_group": 0,
  "parent_account": "Comptes de Charges",
  "account_number": "661"
 },
 {
  "account_name": "Comptes de Produits",
  "root_type": "Income",
  "is_group": 1
 },
 {
  "account_name": "Ventes",
  "root_type": "Income",
  "is_group": 0,
  "parent_account": "Comptes de Produits",
  "account_number": "701"
 },
 {
  "account_name": "Prestations de Services",
  "root_type": "Income",
  "is_group": 0,
  "parent_account": "Comptes de Produits",
  "account_number": "706"
 },
 {
  "account_name": "Produits Financiers",
  "root_type": "Income",
  "is_group": 0,
  "parent_account": "Comptes de Produits",
  "account_number": "76"
 },
 {
  "account_name": "Produits Exceptionnels",
  "root_type": "Income",
  "is_group": 0,
  "parent_account": "Comptes de Produits",
  "account_number": "77"
 }
]

NGO_ACCOUNTS = [
 {
  "account_name": "ASSETS",
  "root_type": "Asset",
  "is_group": 1
 },
 {
  "account_name": "Current Assets",
  "root_type": "Asset",
  "is_group": 1,
  "parent_account": "ASSETS"
 },
 {
  "account_name": "Cash - Operations",
  "root_type": "Asset",
  "is_group": 0,
  "parent_account": "Current Assets"
 },
 {
  "account_name": "Cash - Restricted",
  "root_type": "Asset",
  "is_group": 0,
  "parent_account": "Current Assets"
 },
 {
  "account_name": "Bank Accounts",
  "root_type": "Asset",
  "is_group": 0,
  "parent_account": "Current Assets"
 },
 {
  "account_name": "Petty Cash",
  "root_type": "Asset",
  "is_group": 0,
  "parent_account": "Current Assets"
 },
 {
  "account_name": "Accounts Receivable",
  "root_type": "Asset",
  "is_group": 0,
  "parent_account": "Current Assets"
 },
 {
  "account_name": "Grants Receivable",
  "root_type": "Asset",
  "is_group": 0,
  "parent_account": "Current Assets"
 },
 {
  "account_name": "Prepaid Expenses",
  "root_type": "Asset",
  "is_group": 0,
  "parent_account": "Current Assets"
 },
 {
  "account_name": "Non-Current Assets",
  "root_type": "Asset",
  "is_group": 1,
  "parent_account": "ASSETS"
 },
 {
  "account_name": "Land and Buildings",
  "root_type": "Asset",
  "is_group": 0,
  "parent_account": "Non-Current Assets"
 },
 {
  "account_name": "Equipment",
  "root_type": "Asset",
  "is_group": 0,
  "parent_account": "Non-Current Assets"
 },
 {
  "account_name": "Vehicles",
  "root_type": "Asset",
  "is_group": 0,
  "parent_account": "Non-Current Assets"
 },
 {
  "account_name": "Furniture and Fixtures",
  "root_type": "Asset",
  "is_group": 0,
  "parent_account": "Non-Current Assets"
 },
 {
  "account_name": "Accumulated Depreciation",
  "root_type": "Asset",
  "is_group": 0,
  "parent_account": "Non-Current Assets"
 },
 {
  "account_name": "LIABILITIES",
  "root_type": "Liability",
  "is_group": 1
 },
 {
  "account_name": "Current Liabilities",
  "root_type": "Liability",
  "is_group": 1,
  "parent_account": "LIABILITIES"
 },
 {
  "account_name": "Accounts Payable",
  "root_type": "Liability",
  "is_group": 0,
  "parent_account": "Current Liabilities"
 },
 {
  "account_name": "Accrued Expenses",
  "root_type": "Liability",
  "is_group": 0,
  "parent_account": "Current Liabilities"
 },
 {
  "account_name": "Grants Payable",
  "root_type": "Liability",
  "is_group": 0,
  "parent_account": "Current Liabilities"
 },
 {
  "account_name": "Deferred Revenue",
  "root_type": "Liability",
  "is_group": 0,
  "parent_account": "Current Liabilities"
 },
 {
  "account_name": "Payroll Liabilities",
  "root_type": "Liability",
  "is_group": 0,
  "parent_account": "Current Liabilities"
 },
 {
  "account_name": "Long-Term Liabilities",
  "root_type": "Liability",
  "is_group": 1,
  "parent_account": "LIABILITIES"
 },
 {
  "account_name": "Loans Payable",
  "root_type": "Liability",
  "is_group": 0,
  "parent_account": "Long-Term Liabilities"
 },
 {
  "account_name": "NET ASSETS",
  "root_type": "Equity",
  "is_group": 1
 },
 {
  "account_name": "Unrestricted Net Assets",
  "root_type": "Equity",
  "is_group": 0,
  "parent_account": "NET ASSETS"
 },
 {
  "account_name": "Temporarily Restricted Net Assets",
  "root_type": "Equity",
  "is_group": 0,
  "parent_account": "NET ASSETS"
 },
 {
  "account_name": "Permanently Restricted Net Assets",
  "root_type": "Equity",
  "is_group": 0,
  "parent_account": "NET ASSETS"
 },
 {
  "account_name": "Current Year Activity",
  "root_type": "Equity",
  "is_group": 0,
  "parent_account": "NET ASSETS"
 },
 {
  "account_name": "REVENUE",
  "root_type": "Income",
  "is_group": 1
 },
 {
  "account_name": "Contributions",
  "root_type": "Income",
  "is_group": 1,
  "parent_account": "REVENUE"
 },
 {
  "account_name": "Individual Donations",
  "root_type": "Income",
  "is_group": 0,
  "parent_account": "Contributions"
 },
 {
  "account_name": "Corporate Sponsorships",
  "root_type": "Income",
  "is_group": 0,
  "parent_account": "Contributions"
 },
 {
  "account_name": "Foundation Grants",
  "root_type": "Income",
  "is_group": 0,
  "parent_account": "Contributions"
 },
 {
  "account_name": "Government Grants",
  "root_type": "Income",
  "is_group": 0,
  "parent_account": "Contributions"
 },
 {
  "account_name": "Membership Fees",
  "root_type": "Income",
  "is_group": 0,
  "parent_account": "REVENUE"
 },
 {
  "account_name": "Program Service Revenue",
  "root_type": "Income",
  "is_group": 0,
  "parent_account": "REVENUE"
 },
 {
  "account_name": "Interest and Investment Income",
  "root_type": "Income",
  "is_group": 0,
  "parent_account": "REVENUE"
 },
 {
  "account_name": "Fundraising Events",
  "root_type": "Income",
  "is_group": 0,
  "parent_account": "REVENUE"
 },
 {
  "account_name": "EXPENSES",
  "root_type": "Expense",
  "is_group": 1
 },
 {
  "account_name": "Program Expenses",
  "root_type": "Expense",
  "is_group": 1,
  "parent_account": "EXPENSES"
 },
 {
  "account_name": "Program A - Direct Costs",
  "root_type": "Expense",
  "is_group": 0,
  "parent_account": "Program Expenses"
 },
 {
  "account_name": "Program B - Direct Costs",
  "root_type": "Expense",
  "is_group": 0,
  "parent_account": "Program Expenses"
 },
 {
  "account_name": "Program Travel",
  "root_type": "Expense",
  "is_group": 0,
  "parent_account": "Program Expenses"
 },
 {
  "account_name": "Program Supplies",
  "root_type": "Expense",
  "is_group": 0,
  "parent_account": "Program Expenses"
 },
 {
  "account_name": "Program Personnel",
  "root_type": "Expense",
  "is_group": 0,
  "parent_account": "Program Expenses"
 },
 {
  "account_name": "Management and General",
  "root_type": "Expense",
  "is_group": 1,
  "parent_account": "EXPENSES"
 },
 {
  "account_name": "Administrative Salaries",
  "root_type": "Expense",
  "is_group": 0,
  "parent_account": "Management and General"
 },
 {
  "account_name": "Office Rent",
  "root_type": "Expense",
  "is_group": 0,
  "parent_account": "Management and General"
 },
 {
  "account_name": "Office Utilities",
  "root_type": "Expense",
  "is_group": 0,
  "parent_account": "Management and General"
 },
 {
  "account_name": "Office Supplies",
  "root_type": "Expense",
  "is_group": 0,
  "parent_account": "Management and General"
 },
 {
  "account_name": "Insurance",
  "root_type": "Expense",
  "is_group": 0,
  "parent_account": "Management and General"
 },
 {
  "account_name": "Professional Fees",
  "root_type": "Expense",
  "is_group": 0,
  "parent_account": "Management and General"
 },
 {
  "account_name": "Depreciation",
  "root_type": "Expense",
  "is_group": 0,
  "parent_account": "Management and General"
 },
 {
  "account_name": "Fundraising",
  "root_type": "Expense",
  "is_group": 1,
  "parent_account": "EXPENSES"
 },
 {
  "account_name": "Fundraising Personnel",
  "root_type": "Expense",
  "is_group": 0,
  "parent_account": "Fundraising"
 },
 {
  "account_name": "Fundraising Events Costs",
  "root_type": "Expense",
  "is_group": 0,
  "parent_account": "Fundraising"
 },
 {
  "account_name": "Marketing and Communications",
  "root_type": "Expense",
  "is_group": 0,
  "parent_account": "Fundraising"
 }
]

KSA_ACCOUNTS = [
 {
  "account_name": "الأصول",
  "root_type": "Asset",
  "is_group": 1,
  "account_number": "1"
 },
 {
  "account_name": "الأصول المتداولة",
  "root_type": "Asset",
  "is_group": 1,
  "parent_account": "الأصول",
  "account_number": "11"
 },
 {
  "account_name": "النقدية",
  "root_type": "Asset",
  "is_group": 0,
  "parent_account": "الأصول المتداولة",
  "account_number": "111"
 },
 {
  "account_name": "البنك",
  "root_type": "Asset",
  "is_group": 0,
  "parent_account": "الأصول المتداولة",
  "account_number": "112"
 },
 {
  "account_name": "حسابات القبض",
  "root_type": "Asset",
  "is_group": 0,
  "parent_account": "الأصول المتداولة",
  "account_number": "113"
 },
 {
  "account_name": "مخزون",
  "root_type": "Asset",
  "is_group": 0,
  "parent_account": "الأصول المتداولة",
  "account_number": "114"
 },
 {
  "account_name": "مصروفات مدفوعة قبلا",
  "root_type": "Asset",
  "is_group": 0,
  "parent_account": "الأصول المتداولة",
  "account_number": "115"
 },
 {
  "account_name": "الأصول غير المتداولة",
  "root_type": "Asset",
  "is_group": 1,
  "parent_account": "الأصول",
  "account_number": "12"
 },
 {
  "account_name": "أراضي",
  "root_type": "Asset",
  "is_group": 0,
  "parent_account": "الأصول غير المتداولة",
  "account_number": "121"
 },
 {
  "account_name": "مباني",
  "root_type": "Asset",
  "is_group": 0,
  "parent_account": "الأصول غير المتداولة",
  "account_number": "122"
 },
 {
  "account_name": "آلات ومعدات",
  "root_type": "Asset",
  "is_group": 0,
  "parent_account": "الأصول غير المتداولة",
  "account_number": "123"
 },
 {
  "account_name": "مركبات",
  "root_type": "Asset",
  "is_group": 0,
  "parent_account": "الأصول غير المتداولة",
  "account_number": "124"
 },
 {
  "account_name": "أثاث ومفروشات",
  "root_type": "Asset",
  "is_group": 0,
  "parent_account": "الأصول غير المتداولة",
  "account_number": "125"
 },
 {
  "account_name": "مجمّع الإهلاك",
  "root_type": "Asset",
  "is_group": 0,
  "parent_account": "الأصول غير المتداولة",
  "account_number": "129"
 },
 {
  "account_name": "الأصول غير الملموسة",
  "root_type": "Asset",
  "is_group": 0,
  "parent_account": "الأصول غير المتداولة",
  "account_number": "127"
 },
 {
  "account_name": "الخصوم",
  "root_type": "Liability",
  "is_group": 1,
  "account_number": "2"
 },
 {
  "account_name": "الخصوم المتداولة",
  "root_type": "Liability",
  "is_group": 1,
  "parent_account": "الخصوم",
  "account_number": "21"
 },
 {
  "account_name": "حسابات الدفع",
  "root_type": "Liability",
  "is_group": 0,
  "parent_account": "الخصوم المتداولة",
  "account_number": "211"
 },
 {
  "account_name": "ضريبة القيمة المضافة",
  "root_type": "Liability",
  "is_group": 0,
  "parent_account": "الخصوم المتداولة",
  "account_number": "212",
  "tax_rate": 15
 },
 {
  "account_name": "الرواتب والأجور المستحقة",
  "root_type": "Liability",
  "is_group": 0,
  "parent_account": "الخصوم المتداولة",
  "account_number": "213"
 },
 {
  "account_name": "مصروفات مستحقة",
  "root_type": "Liability",
  "is_group": 0,
  "parent_account": "الخصوم المتداولة",
  "account_number": "214"
 },
 {
  "account_name": "إيرادات مؤجلة",
  "root_type": "Liability",
  "is_group": 0,
  "parent_account": "الخصوم المتداولة",
  "account_number": "215"
 },
 {
  "account_name": "الخصوم غير المتداولة",
  "root_type": "Liability",
  "is_group": 1,
  "parent_account": "الخصوم",
  "account_number": "22"
 },
 {
  "account_name": "قروض طويلة الأجل",
  "root_type": "Liability",
  "is_group": 0,
  "parent_account": "الخصوم غير المتداولة",
  "account_number": "221"
 },
 {
  "account_name": "حقوق الملكية",
  "root_type": "Equity",
  "is_group": 1,
  "account_number": "3"
 },
 {
  "account_name": "رأس المال",
  "root_type": "Equity",
  "is_group": 0,
  "parent_account": "حقوق الملكية",
  "account_number": "31"
 },
 {
  "account_name": "الأرباح المحتجزة",
  "root_type": "Equity",
  "is_group": 0,
  "parent_account": "حقوق الملكية",
  "account_number": "32"
 },
 {
  "account_name": "أرباح السنة الحالية",
  "root_type": "Equity",
  "is_group": 0,
  "parent_account": "حقوق الملكية",
  "account_number": "33"
 },
 {
  "account_name": "الإيرادات",
  "root_type": "Income",
  "is_group": 1,
  "account_number": "4"
 },
 {
  "account_name": "إيرادات المبيعات",
  "root_type": "Income",
  "is_group": 0,
  "parent_account": "الإيرادات",
  "account_number": "41"
 },
 {
  "account_name": "إيرادات الخدمات",
  "root_type": "Income",
  "is_group": 0,
  "parent_account": "الإيرادات",
  "account_number": "42"
 },
 {
  "account_name": "إيرادات أخرى",
  "root_type": "Income",
  "is_group": 0,
  "parent_account": "الإيرادات",
  "account_number": "43"
 },
 {
  "account_name": "المصروفات",
  "root_type": "Expense",
  "is_group": 1,
  "account_number": "5"
 },
 {
  "account_name": "تكلفة البضاعة المباعة",
  "root_type": "Expense",
  "is_group": 0,
  "parent_account": "المصروفات",
  "account_number": "51"
 },
 {
  "account_name": "الرواتب والأجور",
  "root_type": "Expense",
  "is_group": 0,
  "parent_account": "المصروفات",
  "account_number": "52"
 },
 {
  "account_name": "الإيجار",
  "root_type": "Expense",
  "is_group": 0,
  "parent_account": "المصروفات",
  "account_number": "53"
 },
 {
  "account_name": "المرافق",
  "root_type": "Expense",
  "is_group": 0,
  "parent_account": "المصروفات",
  "account_number": "54"
 },
 {
  "account_name": "اللوازم المكتبية",
  "root_type": "Expense",
  "is_group": 0,
  "parent_account": "المصروفات",
  "account_number": "55"
 },
 {
  "account_name": "مصاريف السفر",
  "root_type": "Expense",
  "is_group": 0,
  "parent_account": "المصروفات",
  "account_number": "56"
 },
 {
  "account_name": "الإهلاك",
  "root_type": "Expense",
  "is_group": 0,
  "parent_account": "المصروفات",
  "account_number": "57"
 },
 {
  "account_name": "مصاريف أخرى",
  "root_type": "Expense",
  "is_group": 0,
  "parent_account": "المصروفات",
  "account_number": "59"
 }
]

COA_TEMPLATES = {
 "GAAP": {
  "title": "US GAAP",
  "currency": "USD",
  "vat_rate": 15,
  "accounts": [
   {
    "account_name": "1000 Assets",
    "root_type": "Asset",
    "is_group": 1
   },
   {
    "account_name": "1100 Cash and Cash Equivalents",
    "root_type": "Asset",
    "is_group": 1,
    "parent_account": "1000 Assets"
   },
   {
    "account_name": "1110 Cash - Operating",
    "root_type": "Asset",
    "is_group": 0,
    "parent_account": "1100 Cash and Cash Equivalents",
    "account_number": "1110"
   },
   {
    "account_name": "1120 Cash - Payroll",
    "root_type": "Asset",
    "is_group": 0,
    "parent_account": "1100 Cash and Cash Equivalents",
    "account_number": "1120"
   },
   {
    "account_name": "1130 Petty Cash",
    "root_type": "Asset",
    "is_group": 0,
    "parent_account": "1100 Cash and Cash Equivalents",
    "account_number": "1130"
   },
   {
    "account_name": "1140 Checking Account",
    "root_type": "Asset",
    "is_group": 0,
    "parent_account": "1100 Cash and Cash Equivalents",
    "account_number": "1140"
   },
   {
    "account_name": "1150 Savings Account",
    "root_type": "Asset",
    "is_group": 0,
    "parent_account": "1100 Cash and Cash Equivalents",
    "account_number": "1150"
   },
   {
    "account_name": "1200 Accounts Receivable",
    "root_type": "Asset",
    "is_group": 1,
    "parent_account": "1000 Assets"
   },
   {
    "account_name": "1210 Accounts Receivable - Trade",
    "root_type": "Asset",
    "is_group": 0,
    "parent_account": "1200 Accounts Receivable",
    "account_number": "1210"
   },
   {
    "account_name": "1220 Allowance for Doubtful Accounts",
    "root_type": "Asset",
    "is_group": 0,
    "parent_account": "1200 Accounts Receivable",
    "account_number": "1220"
   },
   {
    "account_name": "1230 Employee Receivables",
    "root_type": "Asset",
    "is_group": 0,
    "parent_account": "1200 Accounts Receivable",
    "account_number": "1230"
   },
   {
    "account_name": "1300 Inventory",
    "root_type": "Asset",
    "is_group": 1,
    "parent_account": "1000 Assets"
   },
   {
    "account_name": "1310 Raw Materials",
    "root_type": "Asset",
    "is_group": 0,
    "parent_account": "1300 Inventory",
    "account_number": "1310"
   },
   {
    "account_name": "1320 Work in Progress",
    "root_type": "Asset",
    "is_group": 0,
    "parent_account": "1300 Inventory",
    "account_number": "1320"
   },
   {
    "account_name": "1330 Finished Goods",
    "root_type": "Asset",
    "is_group": 0,
    "parent_account": "1300 Inventory",
    "account_number": "1330"
   },
   {
    "account_name": "1400 Prepaid Expenses",
    "root_type": "Asset",
    "is_group": 1,
    "parent_account": "1000 Assets"
   },
   {
    "account_name": "1410 Prepaid Insurance",
    "root_type": "Asset",
    "is_group": 0,
    "parent_account": "1400 Prepaid Expenses",
    "account_number": "1410"
   },
   {
    "account_name": "1420 Prepaid Rent",
    "root_type": "Asset",
    "is_group": 0,
    "parent_account": "1400 Prepaid Expenses",
    "account_number": "1420"
   },
   {
    "account_name": "1500 Fixed Assets",
    "root_type": "Asset",
    "is_group": 1,
    "parent_account": "1000 Assets"
   },
   {
    "account_name": "1510 Land",
    "root_type": "Asset",
    "is_group": 0,
    "parent_account": "1500 Fixed Assets",
    "account_number": "1510"
   },
   {
    "account_name": "1520 Buildings",
    "root_type": "Asset",
    "is_group": 0,
    "parent_account": "1500 Fixed Assets",
    "account_number": "1520"
   },
   {
    "account_name": "1530 Machinery and Equipment",
    "root_type": "Asset",
    "is_group": 0,
    "parent_account": "1500 Fixed Assets",
    "account_number": "1530"
   },
   {
    "account_name": "1540 Vehicles",
    "root_type": "Asset",
    "is_group": 0,
    "parent_account": "1500 Fixed Assets",
    "account_number": "1540"
   },
   {
    "account_name": "1550 Furniture and Fixtures",
    "root_type": "Asset",
    "is_group": 0,
    "parent_account": "1500 Fixed Assets",
    "account_number": "1550"
   },
   {
    "account_name": "1560 Computers and Software",
    "root_type": "Asset",
    "is_group": 0,
    "parent_account": "1500 Fixed Assets",
    "account_number": "1560"
   },
   {
    "account_name": "1600 Accumulated Depreciation",
    "root_type": "Asset",
    "is_group": 1,
    "parent_account": "1000 Assets"
   },
   {
    "account_name": "1610 Accum Dep - Buildings",
    "root_type": "Asset",
    "is_group": 0,
    "parent_account": "1600 Accumulated Depreciation",
    "account_number": "1610"
   },
   {
    "account_name": "1620 Accum Dep - Equipment",
    "root_type": "Asset",
    "is_group": 0,
    "parent_account": "1600 Accumulated Depreciation",
    "account_number": "1620"
   },
   {
    "account_name": "1630 Accum Dep - Vehicles",
    "root_type": "Asset",
    "is_group": 0,
    "parent_account": "1600 Accumulated Depreciation",
    "account_number": "1630"
   },
   {
    "account_name": "1700 Intangible Assets",
    "root_type": "Asset",
    "is_group": 1,
    "parent_account": "1000 Assets"
   },
   {
    "account_name": "1710 Goodwill",
    "root_type": "Asset",
    "is_group": 0,
    "parent_account": "1700 Intangible Assets",
    "account_number": "1710"
   },
   {
    "account_name": "1720 Patents",
    "root_type": "Asset",
    "is_group": 0,
    "parent_account": "1700 Intangible Assets",
    "account_number": "1720"
   },
   {
    "account_name": "1730 Trademarks",
    "root_type": "Asset",
    "is_group": 0,
    "parent_account": "1700 Intangible Assets",
    "account_number": "1730"
   },
   {
    "account_name": "1800 Other Assets",
    "root_type": "Asset",
    "is_group": 1,
    "parent_account": "1000 Assets"
   },
   {
    "account_name": "1810 Investments",
    "root_type": "Asset",
    "is_group": 0,
    "parent_account": "1800 Other Assets",
    "account_number": "1810"
   },
   {
    "account_name": "1820 Deposits",
    "root_type": "Asset",
    "is_group": 0,
    "parent_account": "1800 Other Assets",
    "account_number": "1820"
   },
   {
    "account_name": "2000 Liabilities",
    "root_type": "Liability",
    "is_group": 1
   },
   {
    "account_name": "2100 Accounts Payable",
    "root_type": "Liability",
    "is_group": 1,
    "parent_account": "2000 Liabilities"
   },
   {
    "account_name": "2110 Accounts Payable - Trade",
    "root_type": "Liability",
    "is_group": 0,
    "parent_account": "2100 Accounts Payable",
    "account_number": "2110"
   },
   {
    "account_name": "2120 Accrued Liabilities",
    "root_type": "Liability",
    "is_group": 0,
    "parent_account": "2100 Accounts Payable",
    "account_number": "2120"
   },
   {
    "account_name": "2200 Tax Payables",
    "root_type": "Liability",
    "is_group": 1,
    "parent_account": "2000 Liabilities"
   },
   {
    "account_name": "2210 VAT/Sales Tax Payable",
    "root_type": "Liability",
    "is_group": 0,
    "parent_account": "2200 Tax Payables",
    "account_number": "2210"
   },
   {
    "account_name": "2220 Income Tax Payable",
    "root_type": "Liability",
    "is_group": 0,
    "parent_account": "2200 Tax Payables",
    "account_number": "2220"
   },
   {
    "account_name": "2230 Payroll Tax Payable",
    "root_type": "Liability",
    "is_group": 0,
    "parent_account": "2200 Tax Payables",
    "account_number": "2230"
   },
   {
    "account_name": "2300 Accrued Expenses",
    "root_type": "Liability",
    "is_group": 1,
    "parent_account": "2000 Liabilities"
   },
   {
    "account_name": "2310 Accrued Salaries",
    "root_type": "Liability",
    "is_group": 0,
    "parent_account": "2300 Accrued Expenses",
    "account_number": "2310"
   },
   {
    "account_name": "2320 Accrued Interest",
    "root_type": "Liability",
    "is_group": 0,
    "parent_account": "2300 Accrued Expenses",
    "account_number": "2320"
   },
   {
    "account_name": "2400 Deferred Revenue",
    "root_type": "Liability",
    "is_group": 1,
    "parent_account": "2000 Liabilities"
   },
   {
    "account_name": "2410 Unearned Revenue",
    "root_type": "Liability",
    "is_group": 0,
    "parent_account": "2400 Deferred Revenue",
    "account_number": "2410"
   },
   {
    "account_name": "2500 Long Term Liabilities",
    "root_type": "Liability",
    "is_group": 1,
    "parent_account": "2000 Liabilities"
   },
   {
    "account_name": "2510 Bank Loans",
    "root_type": "Liability",
    "is_group": 0,
    "parent_account": "2500 Long Term Liabilities",
    "account_number": "2510"
   },
   {
    "account_name": "2520 Notes Payable",
    "root_type": "Liability",
    "is_group": 0,
    "parent_account": "2500 Long Term Liabilities",
    "account_number": "2520"
   },
   {
    "account_name": "2530 Bonds Payable",
    "root_type": "Liability",
    "is_group": 0,
    "parent_account": "2500 Long Term Liabilities",
    "account_number": "2530"
   },
   {
    "account_name": "3000 Equity",
    "root_type": "Equity",
    "is_group": 1
   },
   {
    "account_name": "3100 Common Stock",
    "root_type": "Equity",
    "is_group": 0,
    "parent_account": "3000 Equity",
    "account_number": "3100"
   },
   {
    "account_name": "3200 Additional Paid-in Capital",
    "root_type": "Equity",
    "is_group": 0,
    "parent_account": "3000 Equity",
    "account_number": "3200"
   },
   {
    "account_name": "3300 Retained Earnings",
    "root_type": "Equity",
    "is_group": 0,
    "parent_account": "3000 Equity",
    "account_number": "3300"
   },
   {
    "account_name": "3400 Current Year Earnings",
    "root_type": "Equity",
    "is_group": 0,
    "parent_account": "3000 Equity",
    "account_number": "3400"
   },
   {
    "account_name": "3500 Owner's Draws",
    "root_type": "Equity",
    "is_group": 0,
    "parent_account": "3000 Equity",
    "account_number": "3500"
   },
   {
    "account_name": "4000 Income",
    "root_type": "Income",
    "is_group": 1
   },
   {
    "account_name": "4100 Revenue",
    "root_type": "Income",
    "is_group": 1,
    "parent_account": "4000 Income"
   },
   {
    "account_name": "4110 Product Sales",
    "root_type": "Income",
    "is_group": 0,
    "parent_account": "4100 Revenue",
    "account_number": "4110"
   },
   {
    "account_name": "4120 Service Revenue",
    "root_type": "Income",
    "is_group": 0,
    "parent_account": "4100 Revenue",
    "account_number": "4120"
   },
   {
    "account_name": "4130 Interest Income",
    "root_type": "Income",
    "is_group": 0,
    "parent_account": "4100 Revenue",
    "account_number": "4130"
   },
   {
    "account_name": "4140 Rental Income",
    "root_type": "Income",
    "is_group": 0,
    "parent_account": "4100 Revenue",
    "account_number": "4140"
   },
   {
    "account_name": "4200 Other Income",
    "root_type": "Income",
    "is_group": 1,
    "parent_account": "4000 Income"
   },
   {
    "account_name": "4210 Gain on Sale of Assets",
    "root_type": "Income",
    "is_group": 0,
    "parent_account": "4200 Other Income",
    "account_number": "4210"
   },
   {
    "account_name": "4220 Foreign Exchange Gain",
    "root_type": "Income",
    "is_group": 0,
    "parent_account": "4200 Other Income",
    "account_number": "4220"
   },
   {
    "account_name": "5000 Expenses",
    "root_type": "Expense",
    "is_group": 1
   },
   {
    "account_name": "5100 Cost of Goods Sold",
    "root_type": "Expense",
    "is_group": 1,
    "parent_account": "5000 Expenses"
   },
   {
    "account_name": "5110 COGS - Materials",
    "root_type": "Expense",
    "is_group": 0,
    "parent_account": "5100 Cost of Goods Sold",
    "account_number": "5110"
   },
   {
    "account_name": "5120 COGS - Labor",
    "root_type": "Expense",
    "is_group": 0,
    "parent_account": "5100 Cost of Goods Sold",
    "account_number": "5120"
   },
   {
    "account_name": "5130 COGS - Overhead",
    "root_type": "Expense",
    "is_group": 0,
    "parent_account": "5100 Cost of Goods Sold",
    "account_number": "5130"
   },
   {
    "account_name": "5200 Salaries and Wages",
    "root_type": "Expense",
    "is_group": 0,
    "parent_account": "5000 Expenses",
    "account_number": "5200"
   },
   {
    "account_name": "5300 Rent and Utilities",
    "root_type": "Expense",
    "is_group": 1,
    "parent_account": "5000 Expenses"
   },
   {
    "account_name": "5310 Rent Expense",
    "root_type": "Expense",
    "is_group": 0,
    "parent_account": "5300 Rent and Utilities",
    "account_number": "5310"
   },
   {
    "account_name": "5320 Electricity",
    "root_type": "Expense",
    "is_group": 0,
    "parent_account": "5300 Rent and Utilities",
    "account_number": "5320"
   },
   {
    "account_name": "5330 Water and Gas",
    "root_type": "Expense",
    "is_group": 0,
    "parent_account": "5300 Rent and Utilities",
    "account_number": "5330"
   },
   {
    "account_name": "5340 Internet and Telephone",
    "root_type": "Expense",
    "is_group": 0,
    "parent_account": "5300 Rent and Utilities",
    "account_number": "5340"
   },
   {
    "account_name": "5400 Office and Admin",
    "root_type": "Expense",
    "is_group": 1,
    "parent_account": "5000 Expenses"
   },
   {
    "account_name": "5410 Office Supplies",
    "root_type": "Expense",
    "is_group": 0,
    "parent_account": "5400 Office and Admin",
    "account_number": "5410"
   },
   {
    "account_name": "5420 Insurance",
    "root_type": "Expense",
    "is_group": 0,
    "parent_account": "5400 Office and Admin",
    "account_number": "5420"
   },
   {
    "account_name": "5430 Legal and Professional",
    "root_type": "Expense",
    "is_group": 0,
    "parent_account": "5400 Office and Admin",
    "account_number": "5430"
   },
   {
    "account_name": "5440 Bank Charges",
    "root_type": "Expense",
    "is_group": 0,
    "parent_account": "5400 Office and Admin",
    "account_number": "5440"
   },
   {
    "account_name": "5500 Depreciation and Amortization",
    "root_type": "Expense",
    "is_group": 0,
    "parent_account": "5000 Expenses",
    "account_number": "5500"
   },
   {
    "account_name": "5600 Travel and Entertainment",
    "root_type": "Expense",
    "is_group": 1,
    "parent_account": "5000 Expenses"
   },
   {
    "account_name": "5610 Travel Expense",
    "root_type": "Expense",
    "is_group": 0,
    "parent_account": "5600 Travel and Entertainment",
    "account_number": "5610"
   },
   {
    "account_name": "5620 Meals and Entertainment",
    "root_type": "Expense",
    "is_group": 0,
    "parent_account": "5600 Travel and Entertainment",
    "account_number": "5620"
   },
   {
    "account_name": "5700 Marketing and Advertising",
    "root_type": "Expense",
    "is_group": 0,
    "parent_account": "5000 Expenses",
    "account_number": "5700"
   },
   {
    "account_name": "5800 Taxes and Licenses",
    "root_type": "Expense",
    "is_group": 0,
    "parent_account": "5000 Expenses",
    "account_number": "5800"
   },
   {
    "account_name": "5900 Other Expenses",
    "root_type": "Expense",
    "is_group": 1,
    "parent_account": "5000 Expenses"
   },
   {
    "account_name": "5910 Loss on Asset Disposal",
    "root_type": "Expense",
    "is_group": 0,
    "parent_account": "5900 Other Expenses",
    "account_number": "5910"
   },
   {
    "account_name": "5920 Foreign Exchange Loss",
    "root_type": "Expense",
    "is_group": 0,
    "parent_account": "5900 Other Expenses",
    "account_number": "5920"
   },
   {
    "account_name": "5990 Miscellaneous",
    "root_type": "Expense",
    "is_group": 0,
    "parent_account": "5900 Other Expenses",
    "account_number": "5990"
   }
  ]
 },
 "IFRS": {
  "title": "International IFRS",
  "currency": "USD",
  "vat_rate": 15,
  "accounts": [
   {
    "account_name": "Non-Current Assets",
    "root_type": "Asset",
    "is_group": 1
   },
   {
    "account_name": "Property, Plant and Equipment",
    "root_type": "Asset",
    "is_group": 1,
    "parent_account": "Non-Current Assets"
   },
   {
    "account_name": "Land and Buildings",
    "root_type": "Asset",
    "is_group": 0,
    "parent_account": "Property, Plant and Equipment"
   },
   {
    "account_name": "Plant and Machinery",
    "root_type": "Asset",
    "is_group": 0,
    "parent_account": "Property, Plant and Equipment"
   },
   {
    "account_name": "Fixtures and Fittings",
    "root_type": "Asset",
    "is_group": 0,
    "parent_account": "Property, Plant and Equipment"
   },
   {
    "account_name": "Right-of-Use Assets",
    "root_type": "Asset",
    "is_group": 0,
    "parent_account": "Non-Current Assets",
    "account_number": "IFRS16"
   },
   {
    "account_name": "Intangible Assets",
    "root_type": "Asset",
    "is_group": 1,
    "parent_account": "Non-Current Assets"
   },
   {
    "account_name": "Goodwill",
    "root_type": "Asset",
    "is_group": 0,
    "parent_account": "Intangible Assets"
   },
   {
    "account_name": "Patents and Trademarks",
    "root_type": "Asset",
    "is_group": 0,
    "parent_account": "Intangible Assets"
   },
   {
    "account_name": "Investments in Associates",
    "root_type": "Asset",
    "is_group": 0,
    "parent_account": "Non-Current Assets"
   },
   {
    "account_name": "Deferred Tax Assets",
    "root_type": "Asset",
    "is_group": 0,
    "parent_account": "Non-Current Assets"
   },
   {
    "account_name": "Current Assets",
    "root_type": "Asset",
    "is_group": 1
   },
   {
    "account_name": "Inventories",
    "root_type": "Asset",
    "is_group": 1,
    "parent_account": "Current Assets"
   },
   {
    "account_name": "Raw Materials",
    "root_type": "Asset",
    "is_group": 0,
    "parent_account": "Inventories"
   },
   {
    "account_name": "Work in Progress",
    "root_type": "Asset",
    "is_group": 0,
    "parent_account": "Inventories"
   },
   {
    "account_name": "Finished Goods",
    "root_type": "Asset",
    "is_group": 0,
    "parent_account": "Inventories"
   },
   {
    "account_name": "Trade Receivables",
    "root_type": "Asset",
    "is_group": 0,
    "parent_account": "Current Assets"
   },
   {
    "account_name": "Other Receivables",
    "root_type": "Asset",
    "is_group": 0,
    "parent_account": "Current Assets"
   },
   {
    "account_name": "Cash and Cash Equivalents",
    "root_type": "Asset",
    "is_group": 1,
    "parent_account": "Current Assets"
   },
   {
    "account_name": "Cash on Hand",
    "root_type": "Asset",
    "is_group": 0,
    "parent_account": "Cash and Cash Equivalents"
   },
   {
    "account_name": "Cash at Bank",
    "root_type": "Asset",
    "is_group": 0,
    "parent_account": "Cash and Cash Equivalents"
   },
   {
    "account_name": "Prepaid Expenses",
    "root_type": "Asset",
    "is_group": 0,
    "parent_account": "Current Assets"
   },
   {
    "account_name": "Current Tax Assets",
    "root_type": "Asset",
    "is_group": 0,
    "parent_account": "Current Assets"
   },
   {
    "account_name": "Equity",
    "root_type": "Equity",
    "is_group": 1
   },
   {
    "account_name": "Share Capital",
    "root_type": "Equity",
    "is_group": 0,
    "parent_account": "Equity"
   },
   {
    "account_name": "Share Premium",
    "root_type": "Equity",
    "is_group": 0,
    "parent_account": "Equity"
   },
   {
    "account_name": "Retained Earnings",
    "root_type": "Equity",
    "is_group": 0,
    "parent_account": "Equity"
   },
   {
    "account_name": "Revaluation Reserve",
    "root_type": "Equity",
    "is_group": 0,
    "parent_account": "Equity"
   },
   {
    "account_name": "Foreign Currency Translation Reserve",
    "root_type": "Equity",
    "is_group": 0,
    "parent_account": "Equity"
   },
   {
    "account_name": "Non-Controlling Interest",
    "root_type": "Equity",
    "is_group": 0,
    "parent_account": "Equity"
   },
   {
    "account_name": "Non-Current Liabilities",
    "root_type": "Liability",
    "is_group": 1
   },
   {
    "account_name": "Borrowings",
    "root_type": "Liability",
    "is_group": 0,
    "parent_account": "Non-Current Liabilities"
   },
   {
    "account_name": "Lease Liabilities",
    "root_type": "Liability",
    "is_group": 0,
    "parent_account": "Non-Current Liabilities"
   },
   {
    "account_name": "Deferred Tax Liabilities",
    "root_type": "Liability",
    "is_group": 0,
    "parent_account": "Non-Current Liabilities"
   },
   {
    "account_name": "Provisions",
    "root_type": "Liability",
    "is_group": 0,
    "parent_account": "Non-Current Liabilities"
   },
   {
    "account_name": "Current Liabilities",
    "root_type": "Liability",
    "is_group": 1
   },
   {
    "account_name": "Trade Payables",
    "root_type": "Liability",
    "is_group": 0,
    "parent_account": "Current Liabilities"
   },
   {
    "account_name": "Accrued Expenses",
    "root_type": "Liability",
    "is_group": 0,
    "parent_account": "Current Liabilities"
   },
   {
    "account_name": "Current Tax Payable",
    "root_type": "Liability",
    "is_group": 0,
    "parent_account": "Current Liabilities"
   },
   {
    "account_name": "VAT Payable",
    "root_type": "Liability",
    "is_group": 0,
    "parent_account": "Current Liabilities"
   },
   {
    "account_name": "Deferred Revenue",
    "root_type": "Liability",
    "is_group": 0,
    "parent_account": "Current Liabilities"
   },
   {
    "account_name": "Income",
    "root_type": "Income",
    "is_group": 1
   },
   {
    "account_name": "Revenue",
    "root_type": "Income",
    "is_group": 1,
    "parent_account": "Income"
   },
   {
    "account_name": "Sales of Goods",
    "root_type": "Income",
    "is_group": 0,
    "parent_account": "Revenue"
   },
   {
    "account_name": "Rendering of Services",
    "root_type": "Income",
    "is_group": 0,
    "parent_account": "Revenue"
   },
   {
    "account_name": "Interest Income",
    "root_type": "Income",
    "is_group": 0,
    "parent_account": "Income"
   },
   {
    "account_name": "Other Income",
    "root_type": "Income",
    "is_group": 0,
    "parent_account": "Income"
   },
   {
    "account_name": "Expenses",
    "root_type": "Expense",
    "is_group": 1
   },
   {
    "account_name": "Cost of Sales",
    "root_type": "Expense",
    "is_group": 0,
    "parent_account": "Expenses"
   },
   {
    "account_name": "Distribution Costs",
    "root_type": "Expense",
    "is_group": 0,
    "parent_account": "Expenses"
   },
   {
    "account_name": "Administrative Expenses",
    "root_type": "Expense",
    "is_group": 1,
    "parent_account": "Expenses"
   },
   {
    "account_name": "Salaries",
    "root_type": "Expense",
    "is_group": 0,
    "parent_account": "Administrative Expenses"
   },
   {
    "account_name": "Rent",
    "root_type": "Expense",
    "is_group": 0,
    "parent_account": "Administrative Expenses"
   },
   {
    "account_name": "Utilities",
    "root_type": "Expense",
    "is_group": 0,
    "parent_account": "Administrative Expenses"
   },
   {
    "account_name": "Office Expenses",
    "root_type": "Expense",
    "is_group": 0,
    "parent_account": "Administrative Expenses"
   },
   {
    "account_name": "Professional Fees",
    "root_type": "Expense",
    "is_group": 0,
    "parent_account": "Administrative Expenses"
   },
   {
    "account_name": "Depreciation",
    "root_type": "Expense",
    "is_group": 0,
    "parent_account": "Expenses"
   },
   {
    "account_name": "Amortization",
    "root_type": "Expense",
    "is_group": 0,
    "parent_account": "Expenses"
   },
   {
    "account_name": "Finance Costs",
    "root_type": "Expense",
    "is_group": 0,
    "parent_account": "Expenses"
   },
   {
    "account_name": "Income Tax Expense",
    "root_type": "Expense",
    "is_group": 0,
    "parent_account": "Expenses"
   }
  ]
 },
 "UK": {
  "title": "United Kingdom",
  "currency": "GBP",
  "vat_rate": 20,
  "accounts": [
   {
    "account_name": "Fixed Assets",
    "root_type": "Asset",
    "is_group": 1
   },
   {
    "account_name": "Tangible Assets",
    "root_type": "Asset",
    "is_group": 1,
    "parent_account": "Fixed Assets"
   },
   {
    "account_name": "Freehold Property",
    "root_type": "Asset",
    "is_group": 0,
    "parent_account": "Tangible Assets"
   },
   {
    "account_name": "Leasehold Improvements",
    "root_type": "Asset",
    "is_group": 0,
    "parent_account": "Tangible Assets"
   },
   {
    "account_name": "Plant and Machinery",
    "root_type": "Asset",
    "is_group": 0,
    "parent_account": "Tangible Assets"
   },
   {
    "account_name": "Office Equipment",
    "root_type": "Asset",
    "is_group": 0,
    "parent_account": "Tangible Assets"
   },
   {
    "account_name": "Motor Vehicles",
    "root_type": "Asset",
    "is_group": 0,
    "parent_account": "Tangible Assets"
   },
   {
    "account_name": "Intangible Assets",
    "root_type": "Asset",
    "is_group": 1,
    "parent_account": "Fixed Assets"
   },
   {
    "account_name": "Goodwill",
    "root_type": "Asset",
    "is_group": 0,
    "parent_account": "Intangible Assets"
   },
   {
    "account_name": "Software",
    "root_type": "Asset",
    "is_group": 0,
    "parent_account": "Intangible Assets"
   },
   {
    "account_name": "Investments",
    "root_type": "Asset",
    "is_group": 0,
    "parent_account": "Fixed Assets"
   },
   {
    "account_name": "Current Assets",
    "root_type": "Asset",
    "is_group": 1
   },
   {
    "account_name": "Stock",
    "root_type": "Asset",
    "is_group": 0,
    "parent_account": "Current Assets"
   },
   {
    "account_name": "Debtors",
    "root_type": "Asset",
    "is_group": 1,
    "parent_account": "Current Assets"
   },
   {
    "account_name": "Trade Debtors",
    "root_type": "Asset",
    "is_group": 0,
    "parent_account": "Debtors"
   },
   {
    "account_name": "Prepayments",
    "root_type": "Asset",
    "is_group": 0,
    "parent_account": "Debtors"
   },
   {
    "account_name": "Other Debtors",
    "root_type": "Asset",
    "is_group": 0,
    "parent_account": "Debtors"
   },
   {
    "account_name": "Cash at Bank",
    "root_type": "Asset",
    "is_group": 0,
    "parent_account": "Current Assets"
   },
   {
    "account_name": "Cash in Hand",
    "root_type": "Asset",
    "is_group": 0,
    "parent_account": "Current Assets"
   },
   {
    "account_name": "Creditors: Amounts Falling Due Within One Year",
    "root_type": "Liability",
    "is_group": 1
   },
   {
    "account_name": "Trade Creditors",
    "root_type": "Liability",
    "is_group": 0,
    "parent_account": "Creditors: Amounts Falling Due Within One Year"
   },
   {
    "account_name": "Accruals",
    "root_type": "Liability",
    "is_group": 0,
    "parent_account": "Creditors: Amounts Falling Due Within One Year"
   },
   {
    "account_name": "VAT Liability",
    "root_type": "Liability",
    "is_group": 0,
    "parent_account": "Creditors: Amounts Falling Due Within One Year"
   },
   {
    "account_name": "PAYE/NI Liability",
    "root_type": "Liability",
    "is_group": 0,
    "parent_account": "Creditors: Amounts Falling Due Within One Year"
   },
   {
    "account_name": "Corporation Tax Payable",
    "root_type": "Liability",
    "is_group": 0,
    "parent_account": "Creditors: Amounts Falling Due Within One Year"
   },
   {
    "account_name": "Deferred Income",
    "root_type": "Liability",
    "is_group": 0,
    "parent_account": "Creditors: Amounts Falling Due Within One Year"
   },
   {
    "account_name": "Creditors: Amounts Falling Due After One Year",
    "root_type": "Liability",
    "is_group": 1
   },
   {
    "account_name": "Bank Loans",
    "root_type": "Liability",
    "is_group": 0,
    "parent_account": "Creditors: Amounts Falling Due After One Year"
   },
   {
    "account_name": "Hire Purchase Creditors",
    "root_type": "Liability",
    "is_group": 0,
    "parent_account": "Creditors: Amounts Falling Due After One Year"
   },
   {
    "account_name": "Provisions for Liabilities",
    "root_type": "Liability",
    "is_group": 0,
    "parent_account": "Creditors: Amounts Falling Due After One Year"
   },
   {
    "account_name": "Capital and Reserves",
    "root_type": "Equity",
    "is_group": 1
   },
   {
    "account_name": "Called Up Share Capital",
    "root_type": "Equity",
    "is_group": 0,
    "parent_account": "Capital and Reserves"
   },
   {
    "account_name": "Share Premium Account",
    "root_type": "Equity",
    "is_group": 0,
    "parent_account": "Capital and Reserves"
   },
   {
    "account_name": "Profit and Loss Account",
    "root_type": "Equity",
    "is_group": 0,
    "parent_account": "Capital and Reserves"
   },
   {
    "account_name": "Revaluation Reserve",
    "root_type": "Equity",
    "is_group": 0,
    "parent_account": "Capital and Reserves"
   },
   {
    "account_name": "Capital Redemption Reserve",
    "root_type": "Equity",
    "is_group": 0,
    "parent_account": "Capital and Reserves"
   },
   {
    "account_name": "Turnover",
    "root_type": "Income",
    "is_group": 1
   },
   {
    "account_name": "Sales - UK",
    "root_type": "Income",
    "is_group": 0,
    "parent_account": "Turnover"
   },
   {
    "account_name": "Service Revenue",
    "root_type": "Income",
    "is_group": 0,
    "parent_account": "Turnover"
   },
   {
    "account_name": "Other Income",
    "root_type": "Income",
    "is_group": 0,
    "parent_account": "Turnover"
   },
   {
    "account_name": "Cost of Sales",
    "root_type": "Expense",
    "is_group": 1
   },
   {
    "account_name": "Cost of Materials",
    "root_type": "Expense",
    "is_group": 0,
    "parent_account": "Cost of Sales"
   },
   {
    "account_name": "Direct Labour",
    "root_type": "Expense",
    "is_group": 0,
    "parent_account": "Cost of Sales"
   },
   {
    "account_name": "Other Direct Costs",
    "root_type": "Expense",
    "is_group": 0,
    "parent_account": "Cost of Sales"
   },
   {
    "account_name": "Gross Profit/(Loss)",
    "root_type": "Expense",
    "is_group": 1
   },
   {
    "account_name": "Administrative Expenses",
    "root_type": "Expense",
    "is_group": 1,
    "parent_account": "Gross Profit/(Loss)"
   },
   {
    "account_name": "Wages and Salaries",
    "root_type": "Expense",
    "is_group": 0,
    "parent_account": "Administrative Expenses"
   },
   {
    "account_name": "Directors Remuneration",
    "root_type": "Expense",
    "is_group": 0,
    "parent_account": "Administrative Expenses"
   },
   {
    "account_name": "Rent and Rates",
    "root_type": "Expense",
    "is_group": 0,
    "parent_account": "Administrative Expenses"
   },
   {
    "account_name": "Heat, Light and Power",
    "root_type": "Expense",
    "is_group": 0,
    "parent_account": "Administrative Expenses"
   },
   {
    "account_name": "Telephone and Internet",
    "root_type": "Expense",
    "is_group": 0,
    "parent_account": "Administrative Expenses"
   },
   {
    "account_name": "Printing, Postage and Stationery",
    "root_type": "Expense",
    "is_group": 0,
    "parent_account": "Administrative Expenses"
   },
   {
    "account_name": "Insurance",
    "root_type": "Expense",
    "is_group": 0,
    "parent_account": "Administrative Expenses"
   },
   {
    "account_name": "Professional Fees",
    "root_type": "Expense",
    "is_group": 0,
    "parent_account": "Administrative Expenses"
   },
   {
    "account_name": "Depreciation",
    "root_type": "Expense",
    "is_group": 0,
    "parent_account": "Administrative Expenses"
   },
   {
    "account_name": "Amortisation",
    "root_type": "Expense",
    "is_group": 0,
    "parent_account": "Administrative Expenses"
   },
   {
    "account_name": "Finance Costs",
    "root_type": "Expense",
    "is_group": 1,
    "parent_account": "Gross Profit/(Loss)"
   },
   {
    "account_name": "Bank Charges",
    "root_type": "Expense",
    "is_group": 0,
    "parent_account": "Finance Costs"
   },
   {
    "account_name": "Interest Payable",
    "root_type": "Expense",
    "is_group": 0,
    "parent_account": "Finance Costs"
   },
   {
    "account_name": "Taxation",
    "root_type": "Expense",
    "is_group": 0,
    "parent_account": "Gross Profit/(Loss)"
   }
  ]
 },
 "SKR03": {
  "title": "Germany SKR03",
  "currency": "EUR",
  "vat_rate": 19,
  "accounts": [
   {
    "account_name": "Aktivkonten",
    "root_type": "Asset",
    "is_group": 1
   },
   {
    "account_name": "Anlagevermögen",
    "root_type": "Asset",
    "is_group": 1,
    "parent_account": "Aktivkonten"
   },
   {
    "account_name": "Grundstücke und Bauten",
    "root_type": "Asset",
    "is_group": 0,
    "parent_account": "Anlagevermögen",
    "account_number": "0050"
   },
   {
    "account_name": "Maschinen",
    "root_type": "Asset",
    "is_group": 0,
    "parent_account": "Anlagevermögen",
    "account_number": "0200"
   },
   {
    "account_name": "Betriebsausstattung",
    "root_type": "Asset",
    "is_group": 0,
    "parent_account": "Anlagevermögen",
    "account_number": "0400"
   },
   {
    "account_name": "Fuhrpark",
    "root_type": "Asset",
    "is_group": 0,
    "parent_account": "Anlagevermögen",
    "account_number": "0500"
   },
   {
    "account_name": "Büroeinrichtung",
    "root_type": "Asset",
    "is_group": 0,
    "parent_account": "Anlagevermögen",
    "account_number": "0600"
   },
   {
    "account_name": "EDV-Anlagen",
    "root_type": "Asset",
    "is_group": 0,
    "parent_account": "Anlagevermögen",
    "account_number": "0630"
   },
   {
    "account_name": "Immaterielle Vermögensgegenstände",
    "root_type": "Asset",
    "is_group": 1,
    "parent_account": "Anlagevermögen"
   },
   {
    "account_name": "Konzessionen und Lizenzen",
    "root_type": "Asset",
    "is_group": 0,
    "parent_account": "Immaterielle Vermögensgegenstände",
    "account_number": "0005"
   },
   {
    "account_name": "Geschäfts- oder Firmenwert",
    "root_type": "Asset",
    "is_group": 0,
    "parent_account": "Immaterielle Vermögensgegenstände",
    "account_number": "0010"
   },
   {
    "account_name": "Umlaufvermögen",
    "root_type": "Asset",
    "is_group": 1,
    "parent_account": "Aktivkonten"
   },
   {
    "account_name": "Kasse",
    "root_type": "Asset",
    "is_group": 0,
    "parent_account": "Umlaufvermögen",
    "account_number": "1000"
   },
   {
    "account_name": "Bank",
    "root_type": "Asset",
    "is_group": 0,
    "parent_account": "Umlaufvermögen",
    "account_number": "1200"
   },
   {
    "account_name": "Forderungen aus Lieferungen und Leistungen",
    "root_type": "Asset",
    "is_group": 0,
    "parent_account": "Umlaufvermögen",
    "account_number": "1400"
   },
   {
    "account_name": "Sonstige Vermögensgegenstände",
    "root_type": "Asset",
    "is_group": 0,
    "parent_account": "Umlaufvermögen",
    "account_number": "1500"
   },
   {
    "account_name": "Vorräte",
    "root_type": "Asset",
    "is_group": 1,
    "parent_account": "Umlaufvermögen"
   },
   {
    "account_name": "Rohstoffe",
    "root_type": "Asset",
    "is_group": 0,
    "parent_account": "Vorräte",
    "account_number": "2000"
   },
   {
    "account_name": "Fertige Erzeugnisse",
    "root_type": "Asset",
    "is_group": 0,
    "parent_account": "Vorräte",
    "account_number": "2100"
   },
   {
    "account_name": "Aktive Rechnungsabgrenzung",
    "root_type": "Asset",
    "is_group": 0,
    "parent_account": "Umlaufvermögen",
    "account_number": "1900"
   },
   {
    "account_name": "Passivkonten",
    "root_type": "Liability",
    "is_group": 1
   },
   {
    "account_name": "Eigenkapital",
    "root_type": "Liability",
    "is_group": 1,
    "parent_account": "Passivkonten"
   },
   {
    "account_name": "Gezeichnetes Kapital",
    "root_type": "Equity",
    "is_group": 0,
    "parent_account": "Eigenkapital",
    "account_number": "2900"
   },
   {
    "account_name": "Kapitalrücklage",
    "root_type": "Equity",
    "is_group": 0,
    "parent_account": "Eigenkapital",
    "account_number": "2930"
   },
   {
    "account_name": "Gewinnrücklagen",
    "root_type": "Equity",
    "is_group": 0,
    "parent_account": "Eigenkapital",
    "account_number": "2970"
   },
   {
    "account_name": "Jahresüberschuss/Jahresfehlbetrag",
    "root_type": "Equity",
    "is_group": 0,
    "parent_account": "Eigenkapital",
    "account_number": "2990"
   },
   {
    "account_name": "Rückstellungen",
    "root_type": "Liability",
    "is_group": 1,
    "parent_account": "Passivkonten"
   },
   {
    "account_name": "Rückstellungen für Pensionen",
    "root_type": "Liability",
    "is_group": 0,
    "parent_account": "Rückstellungen",
    "account_number": "2400"
   },
   {
    "account_name": "Steuerrückstellungen",
    "root_type": "Liability",
    "is_group": 0,
    "parent_account": "Rückstellungen",
    "account_number": "2450"
   },
   {
    "account_name": "Sonstige Rückstellungen",
    "root_type": "Liability",
    "is_group": 0,
    "parent_account": "Rückstellungen",
    "account_number": "2480"
   },
   {
    "account_name": "Verbindlichkeiten",
    "root_type": "Liability",
    "is_group": 1,
    "parent_account": "Passivkonten"
   },
   {
    "account_name": "Verbindlichkeiten aus L+L",
    "root_type": "Liability",
    "is_group": 0,
    "parent_account": "Verbindlichkeiten",
    "account_number": "3300"
   },
   {
    "account_name": "Verbindlichkeiten ggü. Kreditinstituten",
    "root_type": "Liability",
    "is_group": 0,
    "parent_account": "Verbindlichkeiten",
    "account_number": "3400"
   },
   {
    "account_name": "Erhaltene Anzahlungen",
    "root_type": "Liability",
    "is_group": 0,
    "parent_account": "Verbindlichkeiten",
    "account_number": "3500"
   },
   {
    "account_name": "Verbindlichkeiten aus Steuern",
    "root_type": "Liability",
    "is_group": 0,
    "parent_account": "Verbindlichkeiten",
    "account_number": "3600"
   },
   {
    "account_name": "Umsatzsteuer 19%",
    "root_type": "Liability",
    "is_group": 0,
    "parent_account": "Verbindlichkeiten",
    "account_number": "3800",
    "tax_rate": 19
   },
   {
    "account_name": "Umsatzsteuer 7%",
    "root_type": "Liability",
    "is_group": 0,
    "parent_account": "Verbindlichkeiten",
    "account_number": "3806",
    "tax_rate": 7
   },
   {
    "account_name": "Passive Rechnungsabgrenzung",
    "root_type": "Liability",
    "is_group": 0,
    "parent_account": "Passivkonten",
    "account_number": "3900"
   },
   {
    "account_name": "Erträge",
    "root_type": "Income",
    "is_group": 1
   },
   {
    "account_name": "Betriebliche Erträge",
    "root_type": "Income",
    "is_group": 1,
    "parent_account": "Erträge"
   },
   {
    "account_name": "Umsatzerlöse 19%",
    "root_type": "Income",
    "is_group": 0,
    "parent_account": "Betriebliche Erträge",
    "account_number": "8000",
    "tax_rate": 19
   },
   {
    "account_name": "Umsatzerlöse 7%",
    "root_type": "Income",
    "is_group": 0,
    "parent_account": "Betriebliche Erträge",
    "account_number": "8100",
    "tax_rate": 7
   },
   {
    "account_name": "Umsatzerlöse steuerfrei",
    "root_type": "Income",
    "is_group": 0,
    "parent_account": "Betriebliche Erträge",
    "account_number": "8200"
   },
   {
    "account_name": "Bestandsveränderungen",
    "root_type": "Income",
    "is_group": 0,
    "parent_account": "Betriebliche Erträge",
    "account_number": "8400"
   },
   {
    "account_name": "Sonstige betriebliche Erträge",
    "root_type": "Income",
    "is_group": 0,
    "parent_account": "Betriebliche Erträge",
    "account_number": "8500"
   },
   {
    "account_name": "Nicht betriebliche Erträge",
    "root_type": "Income",
    "is_group": 0,
    "parent_account": "Erträge",
    "account_number": "8600"
   },
   {
    "account_name": "Aufwendungen",
    "root_type": "Expense",
    "is_group": 1
   },
   {
    "account_name": "Materialaufwand",
    "root_type": "Expense",
    "is_group": 1,
    "parent_account": "Aufwendungen"
   },
   {
    "account_name": "Wareneingang",
    "root_type": "Expense",
    "is_group": 0,
    "parent_account": "Materialaufwand",
    "account_number": "5000"
   },
   {
    "account_name": "Bezogene Leistungen",
    "root_type": "Expense",
    "is_group": 0,
    "parent_account": "Materialaufwand",
    "account_number": "5100"
   },
   {
    "account_name": "Personalkosten",
    "root_type": "Expense",
    "is_group": 1,
    "parent_account": "Aufwendungen"
   },
   {
    "account_name": "Gehälter",
    "root_type": "Expense",
    "is_group": 0,
    "parent_account": "Personalkosten",
    "account_number": "6100"
   },
   {
    "account_name": "Löhne",
    "root_type": "Expense",
    "is_group": 0,
    "parent_account": "Personalkosten",
    "account_number": "6000"
   },
   {
    "account_name": "Sozialversicherung",
    "root_type": "Expense",
    "is_group": 0,
    "parent_account": "Personalkosten",
    "account_number": "6130"
   },
   {
    "account_name": "Abschreibungen",
    "root_type": "Expense",
    "is_group": 0,
    "parent_account": "Aufwendungen",
    "account_number": "6500"
   },
   {
    "account_name": "Betriebliche Aufwendungen",
    "root_type": "Expense",
    "is_group": 1,
    "parent_account": "Aufwendungen"
   },
   {
    "account_name": "Miete",
    "root_type": "Expense",
    "is_group": 0,
    "parent_account": "Betriebliche Aufwendungen",
    "account_number": "4100"
   },
   {
    "account_name": "Bürobedarf",
    "root_type": "Expense",
    "is_group": 0,
    "parent_account": "Betriebliche Aufwendungen",
    "account_number": "4900"
   },
   {
    "account_name": "Versicherungen",
    "root_type": "Expense",
    "is_group": 0,
    "parent_account": "Betriebliche Aufwendungen",
    "account_number": "4350"
   },
   {
    "account_name": "Reisekosten",
    "root_type": "Expense",
    "is_group": 0,
    "parent_account": "Betriebliche Aufwendungen",
    "account_number": "4650"
   },
   {
    "account_name": "Fortbildung",
    "root_type": "Expense",
    "is_group": 0,
    "parent_account": "Betriebliche Aufwendungen",
    "account_number": "4520"
   },
   {
    "account_name": "Rechts- und Beratungskosten",
    "root_type": "Expense",
    "is_group": 0,
    "parent_account": "Betriebliche Aufwendungen",
    "account_number": "4800"
   },
   {
    "account_name": "Werbekosten",
    "root_type": "Expense",
    "is_group": 0,
    "parent_account": "Betriebliche Aufwendungen",
    "account_number": "4600"
   },
   {
    "account_name": "Telefon und Internet",
    "root_type": "Expense",
    "is_group": 0,
    "parent_account": "Betriebliche Aufwendungen",
    "account_number": "4920"
   },
   {
    "account_name": "Kfz-Kosten",
    "root_type": "Expense",
    "is_group": 0,
    "parent_account": "Betriebliche Aufwendungen",
    "account_number": "4550"
   },
   {
    "account_name": "Finanzaufwendungen",
    "root_type": "Expense",
    "is_group": 1,
    "parent_account": "Aufwendungen"
   },
   {
    "account_name": "Zinsen und ähnliche Aufwendungen",
    "root_type": "Expense",
    "is_group": 0,
    "parent_account": "Finanzaufwendungen",
    "account_number": "7300"
   },
   {
    "account_name": "Bankgebühren",
    "root_type": "Expense",
    "is_group": 0,
    "parent_account": "Finanzaufwendungen",
    "account_number": "7500"
   },
   {
    "account_name": "Steuern",
    "root_type": "Expense",
    "is_group": 0,
    "parent_account": "Aufwendungen",
    "account_number": "7600"
   }
  ]
 },
 "PCG": {
  "title": "France PCG",
  "currency": "EUR",
  "vat_rate": 20,
  "accounts": [
   {
    "account_name": "Comptes de Actif",
    "root_type": "Asset",
    "is_group": 1
   },
   {
    "account_name": "Actif Immobilisé",
    "root_type": "Asset",
    "is_group": 1,
    "parent_account": "Comptes de Actif"
   },
   {
    "account_name": "Immobilisations Incorporelles",
    "root_type": "Asset",
    "is_group": 1,
    "parent_account": "Actif Immobilisé"
   },
   {
    "account_name": "Frais d'Établissement",
    "root_type": "Asset",
    "is_group": 0,
    "parent_account": "Immobilisations Incorporelles",
    "account_number": "201"
   },
   {
    "account_name": "Logiciels",
    "root_type": "Asset",
    "is_group": 0,
    "parent_account": "Immobilisations Incorporelles",
    "account_number": "205"
   },
   {
    "account_name": "Immobilisations Corporelles",
    "root_type": "Asset",
    "is_group": 1,
    "parent_account": "Actif Immobilisé"
   },
   {
    "account_name": "Terrains",
    "root_type": "Asset",
    "is_group": 0,
    "parent_account": "Immobilisations Corporelles",
    "account_number": "211"
   },
   {
    "account_name": "Constructions",
    "root_type": "Asset",
    "is_group": 0,
    "parent_account": "Immobilisations Corporelles",
    "account_number": "213"
   },
   {
    "account_name": "Installations Techniques",
    "root_type": "Asset",
    "is_group": 0,
    "parent_account": "Immobilisations Corporelles",
    "account_number": "215"
   },
   {
    "account_name": "Matériel de Bureau",
    "root_type": "Asset",
    "is_group": 0,
    "parent_account": "Immobilisations Corporelles",
    "account_number": "218"
   },
   {
    "account_name": "Matériel Informatique",
    "root_type": "Asset",
    "is_group": 0,
    "parent_account": "Immobilisations Corporelles",
    "account_number": "2183"
   },
   {
    "account_name": "Mobilier",
    "root_type": "Asset",
    "is_group": 0,
    "parent_account": "Immobilisations Corporelles",
    "account_number": "2184"
   },
   {
    "account_name": "Amortissements",
    "root_type": "Asset",
    "is_group": 1,
    "parent_account": "Actif Immobilisé"
   },
   {
    "account_name": "Amortissements des Constructions",
    "root_type": "Asset",
    "is_group": 0,
    "parent_account": "Amortissements",
    "account_number": "2813"
   },
   {
    "account_name": "Amortissements du Matériel",
    "root_type": "Asset",
    "is_group": 0,
    "parent_account": "Amortissements",
    "account_number": "2815"
   },
   {
    "account_name": "Actif Circulant",
    "root_type": "Asset",
    "is_group": 1,
    "parent_account": "Comptes de Actif"
   },
   {
    "account_name": "Stocks",
    "root_type": "Asset",
    "is_group": 1,
    "parent_account": "Actif Circulant"
   },
   {
    "account_name": "Matières Premières",
    "root_type": "Asset",
    "is_group": 0,
    "parent_account": "Stocks",
    "account_number": "31"
   },
   {
    "account_name": "Produits Finis",
    "root_type": "Asset",
    "is_group": 0,
    "parent_account": "Stocks",
    "account_number": "35"
   },
   {
    "account_name": "Créances",
    "root_type": "Asset",
    "is_group": 1,
    "parent_account": "Actif Circulant"
   },
   {
    "account_name": "Clients",
    "root_type": "Asset",
    "is_group": 0,
    "parent_account": "Créances",
    "account_number": "411"
   },
   {
    "account_name": "Créances Sociales",
    "root_type": "Asset",
    "is_group": 0,
    "parent_account": "Créances",
    "account_number": "421"
   },
   {
    "account_name": "Trésorerie",
    "root_type": "Asset",
    "is_group": 1,
    "parent_account": "Actif Circulant"
   },
   {
    "account_name": "Caisse",
    "root_type": "Asset",
    "is_group": 0,
    "parent_account": "Trésorerie",
    "account_number": "53"
   },
   {
    "account_name": "Banque",
    "root_type": "Asset",
    "is_group": 0,
    "parent_account": "Trésorerie",
    "account_number": "512"
   },
   {
    "account_name": "Charges Constatées d'Avance",
    "root_type": "Asset",
    "is_group": 0,
    "parent_account": "Actif Circulant",
    "account_number": "486"
   },
   {
    "account_name": "Comptes de Passif",
    "root_type": "Liability",
    "is_group": 1
   },
   {
    "account_name": "Provisions",
    "root_type": "Liability",
    "is_group": 1,
    "parent_account": "Comptes de Passif"
   },
   {
    "account_name": "Provisions pour Risques",
    "root_type": "Liability",
    "is_group": 0,
    "parent_account": "Provisions",
    "account_number": "151"
   },
   {
    "account_name": "Provisions pour Charges",
    "root_type": "Liability",
    "is_group": 0,
    "parent_account": "Provisions",
    "account_number": "153"
   },
   {
    "account_name": "Dettes",
    "root_type": "Liability",
    "is_group": 1,
    "parent_account": "Comptes de Passif"
   },
   {
    "account_name": "Fournisseurs",
    "root_type": "Liability",
    "is_group": 0,
    "parent_account": "Dettes",
    "account_number": "401"
   },
   {
    "account_name": "Dettes Sociales",
    "root_type": "Liability",
    "is_group": 0,
    "parent_account": "Dettes",
    "account_number": "431"
   },
   {
    "account_name": "Dettes Fiscales",
    "root_type": "Liability",
    "is_group": 0,
    "parent_account": "Dettes",
    "account_number": "44"
   },
   {
    "account_name": "TVA à Décaisser",
    "root_type": "Liability",
    "is_group": 0,
    "parent_account": "Dettes Fiscales",
    "account_number": "445"
   },
   {
    "account_name": "Emprunts",
    "root_type": "Liability",
    "is_group": 0,
    "parent_account": "Comptes de Passif",
    "account_number": "164"
   },
   {
    "account_name": "Capitaux Propres",
    "root_type": "Equity",
    "is_group": 1
   },
   {
    "account_name": "Capital Social",
    "root_type": "Equity",
    "is_group": 0,
    "parent_account": "Capitaux Propres",
    "account_number": "101"
   },
   {
    "account_name": "Prime d'Émission",
    "root_type": "Equity",
    "is_group": 0,
    "parent_account": "Capitaux Propres",
    "account_number": "104"
   },
   {
    "account_name": "Réserves",
    "root_type": "Equity",
    "is_group": 0,
    "parent_account": "Capitaux Propres",
    "account_number": "106"
   },
   {
    "account_name": "Report à Nouveau",
    "root_type": "Equity",
    "is_group": 0,
    "parent_account": "Capitaux Propres",
    "account_number": "110"
   },
   {
    "account_name": "Résultat de l'Exercice",
    "root_type": "Equity",
    "is_group": 0,
    "parent_account": "Capitaux Propres",
    "account_number": "120"
   },
   {
    "account_name": "Comptes de Charges",
    "root_type": "Expense",
    "is_group": 1
   },
   {
    "account_name": "Achats",
    "root_type": "Expense",
    "is_group": 0,
    "parent_account": "Comptes de Charges",
    "account_number": "601"
   },
   {
    "account_name": "Charges Externes",
    "root_type": "Expense",
    "is_group": 1,
    "parent_account": "Comptes de Charges"
   },
   {
    "account_name": "Loyers",
    "root_type": "Expense",
    "is_group": 0,
    "parent_account": "Charges Externes",
    "account_number": "613"
   },
   {
    "account_name": "Honoraires",
    "root_type": "Expense",
    "is_group": 0,
    "parent_account": "Charges Externes",
    "account_number": "622"
   },
   {
    "account_name": "Publicité",
    "root_type": "Expense",
    "is_group": 0,
    "parent_account": "Charges Externes",
    "account_number": "623"
   },
   {
    "account_name": "Transports",
    "root_type": "Expense",
    "is_group": 0,
    "parent_account": "Charges Externes",
    "account_number": "624"
   },
   {
    "account_name": "Frais de Téléphone",
    "root_type": "Expense",
    "is_group": 0,
    "parent_account": "Charges Externes",
    "account_number": "626"
   },
   {
    "account_name": "Frais Bancaires",
    "root_type": "Expense",
    "is_group": 0,
    "parent_account": "Charges Externes",
    "account_number": "627"
   },
   {
    "account_name": "Charges de Personnel",
    "root_type": "Expense",
    "is_group": 1,
    "parent_account": "Comptes de Charges"
   },
   {
    "account_name": "Salaires",
    "root_type": "Expense",
    "is_group": 0,
    "parent_account": "Charges de Personnel",
    "account_number": "641"
   },
   {
    "account_name": "Charges Sociales",
    "root_type": "Expense",
    "is_group": 0,
    "parent_account": "Charges de Personnel",
    "account_number": "645"
   },
   {
    "account_name": "Impôts et Taxes",
    "root_type": "Expense",
    "is_group": 0,
    "parent_account": "Comptes de Charges",
    "account_number": "635"
   },
   {
    "account_name": "Dotations aux Amortissements",
    "root_type": "Expense",
    "is_group": 0,
    "parent_account": "Comptes de Charges",
    "account_number": "681"
   },
   {
    "account_name": "Intérêts et Charges Financières",
    "root_type": "Expense",
    "is_group": 0,
    "parent_account": "Comptes de Charges",
    "account_number": "661"
   },
   {
    "account_name": "Comptes de Produits",
    "root_type": "Income",
    "is_group": 1
   },
   {
    "account_name": "Ventes",
    "root_type": "Income",
    "is_group": 0,
    "parent_account": "Comptes de Produits",
    "account_number": "701"
   },
   {
    "account_name": "Prestations de Services",
    "root_type": "Income",
    "is_group": 0,
    "parent_account": "Comptes de Produits",
    "account_number": "706"
   },
   {
    "account_name": "Produits Financiers",
    "root_type": "Income",
    "is_group": 0,
    "parent_account": "Comptes de Produits",
    "account_number": "76"
   },
   {
    "account_name": "Produits Exceptionnels",
    "root_type": "Income",
    "is_group": 0,
    "parent_account": "Comptes de Produits",
    "account_number": "77"
   }
  ]
 },
 "KSA": {
  "title": "Saudi Arabia (SOCPA)",
  "currency": "SAR",
  "vat_rate": 15,
  "accounts": [
   {
    "account_name": "الأصول",
    "root_type": "Asset",
    "is_group": 1,
    "account_number": "1"
   },
   {
    "account_name": "الأصول المتداولة",
    "root_type": "Asset",
    "is_group": 1,
    "parent_account": "الأصول",
    "account_number": "11"
   },
   {
    "account_name": "النقدية",
    "root_type": "Asset",
    "is_group": 0,
    "parent_account": "الأصول المتداولة",
    "account_number": "111"
   },
   {
    "account_name": "البنك",
    "root_type": "Asset",
    "is_group": 0,
    "parent_account": "الأصول المتداولة",
    "account_number": "112"
   },
   {
    "account_name": "حسابات القبض",
    "root_type": "Asset",
    "is_group": 0,
    "parent_account": "الأصول المتداولة",
    "account_number": "113"
   },
   {
    "account_name": "مخزون",
    "root_type": "Asset",
    "is_group": 0,
    "parent_account": "الأصول المتداولة",
    "account_number": "114"
   },
   {
    "account_name": "مصروفات مدفوعة قبلا",
    "root_type": "Asset",
    "is_group": 0,
    "parent_account": "الأصول المتداولة",
    "account_number": "115"
   },
   {
    "account_name": "الأصول غير المتداولة",
    "root_type": "Asset",
    "is_group": 1,
    "parent_account": "الأصول",
    "account_number": "12"
   },
   {
    "account_name": "أراضي",
    "root_type": "Asset",
    "is_group": 0,
    "parent_account": "الأصول غير المتداولة",
    "account_number": "121"
   },
   {
    "account_name": "مباني",
    "root_type": "Asset",
    "is_group": 0,
    "parent_account": "الأصول غير المتداولة",
    "account_number": "122"
   },
   {
    "account_name": "آلات ومعدات",
    "root_type": "Asset",
    "is_group": 0,
    "parent_account": "الأصول غير المتداولة",
    "account_number": "123"
   },
   {
    "account_name": "مركبات",
    "root_type": "Asset",
    "is_group": 0,
    "parent_account": "الأصول غير المتداولة",
    "account_number": "124"
   },
   {
    "account_name": "أثاث ومفروشات",
    "root_type": "Asset",
    "is_group": 0,
    "parent_account": "الأصول غير المتداولة",
    "account_number": "125"
   },
   {
    "account_name": "مجمّع الإهلاك",
    "root_type": "Asset",
    "is_group": 0,
    "parent_account": "الأصول غير المتداولة",
    "account_number": "129"
   },
   {
    "account_name": "الأصول غير الملموسة",
    "root_type": "Asset",
    "is_group": 0,
    "parent_account": "الأصول غير المتداولة",
    "account_number": "127"
   },
   {
    "account_name": "الخصوم",
    "root_type": "Liability",
    "is_group": 1,
    "account_number": "2"
   },
   {
    "account_name": "الخصوم المتداولة",
    "root_type": "Liability",
    "is_group": 1,
    "parent_account": "الخصوم",
    "account_number": "21"
   },
   {
    "account_name": "حسابات الدفع",
    "root_type": "Liability",
    "is_group": 0,
    "parent_account": "الخصوم المتداولة",
    "account_number": "211"
   },
   {
    "account_name": "ضريبة القيمة المضافة",
    "root_type": "Liability",
    "is_group": 0,
    "parent_account": "الخصوم المتداولة",
    "account_number": "212",
    "tax_rate": 15
   },
   {
    "account_name": "الرواتب والأجور المستحقة",
    "root_type": "Liability",
    "is_group": 0,
    "parent_account": "الخصوم المتداولة",
    "account_number": "213"
   },
   {
    "account_name": "مصروفات مستحقة",
    "root_type": "Liability",
    "is_group": 0,
    "parent_account": "الخصوم المتداولة",
    "account_number": "214"
   },
   {
    "account_name": "إيرادات مؤجلة",
    "root_type": "Liability",
    "is_group": 0,
    "parent_account": "الخصوم المتداولة",
    "account_number": "215"
   },
   {
    "account_name": "الخصوم غير المتداولة",
    "root_type": "Liability",
    "is_group": 1,
    "parent_account": "الخصوم",
    "account_number": "22"
   },
   {
    "account_name": "قروض طويلة الأجل",
    "root_type": "Liability",
    "is_group": 0,
    "parent_account": "الخصوم غير المتداولة",
    "account_number": "221"
   },
   {
    "account_name": "حقوق الملكية",
    "root_type": "Equity",
    "is_group": 1,
    "account_number": "3"
   },
   {
    "account_name": "رأس المال",
    "root_type": "Equity",
    "is_group": 0,
    "parent_account": "حقوق الملكية",
    "account_number": "31"
   },
   {
    "account_name": "الأرباح المحتجزة",
    "root_type": "Equity",
    "is_group": 0,
    "parent_account": "حقوق الملكية",
    "account_number": "32"
   },
   {
    "account_name": "أرباح السنة الحالية",
    "root_type": "Equity",
    "is_group": 0,
    "parent_account": "حقوق الملكية",
    "account_number": "33"
   },
   {
    "account_name": "الإيرادات",
    "root_type": "Income",
    "is_group": 1,
    "account_number": "4"
   },
   {
    "account_name": "إيرادات المبيعات",
    "root_type": "Income",
    "is_group": 0,
    "parent_account": "الإيرادات",
    "account_number": "41"
   },
   {
    "account_name": "إيرادات الخدمات",
    "root_type": "Income",
    "is_group": 0,
    "parent_account": "الإيرادات",
    "account_number": "42"
   },
   {
    "account_name": "إيرادات أخرى",
    "root_type": "Income",
    "is_group": 0,
    "parent_account": "الإيرادات",
    "account_number": "43"
   },
   {
    "account_name": "المصروفات",
    "root_type": "Expense",
    "is_group": 1,
    "account_number": "5"
   },
   {
    "account_name": "تكلفة البضاعة المباعة",
    "root_type": "Expense",
    "is_group": 0,
    "parent_account": "المصروفات",
    "account_number": "51"
   },
   {
    "account_name": "الرواتب والأجور",
    "root_type": "Expense",
    "is_group": 0,
    "parent_account": "المصروفات",
    "account_number": "52"
   },
   {
    "account_name": "الإيجار",
    "root_type": "Expense",
    "is_group": 0,
    "parent_account": "المصروفات",
    "account_number": "53"
   },
   {
    "account_name": "المرافق",
    "root_type": "Expense",
    "is_group": 0,
    "parent_account": "المصروفات",
    "account_number": "54"
   },
   {
    "account_name": "اللوازم المكتبية",
    "root_type": "Expense",
    "is_group": 0,
    "parent_account": "المصروفات",
    "account_number": "55"
   },
   {
    "account_name": "مصاريف السفر",
    "root_type": "Expense",
    "is_group": 0,
    "parent_account": "المصروفات",
    "account_number": "56"
   },
   {
    "account_name": "الإهلاك",
    "root_type": "Expense",
    "is_group": 0,
    "parent_account": "المصروفات",
    "account_number": "57"
   },
   {
    "account_name": "مصاريف أخرى",
    "root_type": "Expense",
    "is_group": 0,
    "parent_account": "المصروفات",
    "account_number": "59"
   }
  ]
 },
 "NGO": {
  "title": "Non-Profit (SFAS 117)",
  "currency": "USD",
  "vat_rate": 0,
  "accounts": [
   {
    "account_name": "ASSETS",
    "root_type": "Asset",
    "is_group": 1
   },
   {
    "account_name": "Current Assets",
    "root_type": "Asset",
    "is_group": 1,
    "parent_account": "ASSETS"
   },
   {
    "account_name": "Cash - Operations",
    "root_type": "Asset",
    "is_group": 0,
    "parent_account": "Current Assets"
   },
   {
    "account_name": "Cash - Restricted",
    "root_type": "Asset",
    "is_group": 0,
    "parent_account": "Current Assets"
   },
   {
    "account_name": "Bank Accounts",
    "root_type": "Asset",
    "is_group": 0,
    "parent_account": "Current Assets"
   },
   {
    "account_name": "Petty Cash",
    "root_type": "Asset",
    "is_group": 0,
    "parent_account": "Current Assets"
   },
   {
    "account_name": "Accounts Receivable",
    "root_type": "Asset",
    "is_group": 0,
    "parent_account": "Current Assets"
   },
   {
    "account_name": "Grants Receivable",
    "root_type": "Asset",
    "is_group": 0,
    "parent_account": "Current Assets"
   },
   {
    "account_name": "Prepaid Expenses",
    "root_type": "Asset",
    "is_group": 0,
    "parent_account": "Current Assets"
   },
   {
    "account_name": "Non-Current Assets",
    "root_type": "Asset",
    "is_group": 1,
    "parent_account": "ASSETS"
   },
   {
    "account_name": "Land and Buildings",
    "root_type": "Asset",
    "is_group": 0,
    "parent_account": "Non-Current Assets"
   },
   {
    "account_name": "Equipment",
    "root_type": "Asset",
    "is_group": 0,
    "parent_account": "Non-Current Assets"
   },
   {
    "account_name": "Vehicles",
    "root_type": "Asset",
    "is_group": 0,
    "parent_account": "Non-Current Assets"
   },
   {
    "account_name": "Furniture and Fixtures",
    "root_type": "Asset",
    "is_group": 0,
    "parent_account": "Non-Current Assets"
   },
   {
    "account_name": "Accumulated Depreciation",
    "root_type": "Asset",
    "is_group": 0,
    "parent_account": "Non-Current Assets"
   },
   {
    "account_name": "LIABILITIES",
    "root_type": "Liability",
    "is_group": 1
   },
   {
    "account_name": "Current Liabilities",
    "root_type": "Liability",
    "is_group": 1,
    "parent_account": "LIABILITIES"
   },
   {
    "account_name": "Accounts Payable",
    "root_type": "Liability",
    "is_group": 0,
    "parent_account": "Current Liabilities"
   },
   {
    "account_name": "Accrued Expenses",
    "root_type": "Liability",
    "is_group": 0,
    "parent_account": "Current Liabilities"
   },
   {
    "account_name": "Grants Payable",
    "root_type": "Liability",
    "is_group": 0,
    "parent_account": "Current Liabilities"
   },
   {
    "account_name": "Deferred Revenue",
    "root_type": "Liability",
    "is_group": 0,
    "parent_account": "Current Liabilities"
   },
   {
    "account_name": "Payroll Liabilities",
    "root_type": "Liability",
    "is_group": 0,
    "parent_account": "Current Liabilities"
   },
   {
    "account_name": "Long-Term Liabilities",
    "root_type": "Liability",
    "is_group": 1,
    "parent_account": "LIABILITIES"
   },
   {
    "account_name": "Loans Payable",
    "root_type": "Liability",
    "is_group": 0,
    "parent_account": "Long-Term Liabilities"
   },
   {
    "account_name": "NET ASSETS",
    "root_type": "Equity",
    "is_group": 1
   },
   {
    "account_name": "Unrestricted Net Assets",
    "root_type": "Equity",
    "is_group": 0,
    "parent_account": "NET ASSETS"
   },
   {
    "account_name": "Temporarily Restricted Net Assets",
    "root_type": "Equity",
    "is_group": 0,
    "parent_account": "NET ASSETS"
   },
   {
    "account_name": "Permanently Restricted Net Assets",
    "root_type": "Equity",
    "is_group": 0,
    "parent_account": "NET ASSETS"
   },
   {
    "account_name": "Current Year Activity",
    "root_type": "Equity",
    "is_group": 0,
    "parent_account": "NET ASSETS"
   },
   {
    "account_name": "REVENUE",
    "root_type": "Income",
    "is_group": 1
   },
   {
    "account_name": "Contributions",
    "root_type": "Income",
    "is_group": 1,
    "parent_account": "REVENUE"
   },
   {
    "account_name": "Individual Donations",
    "root_type": "Income",
    "is_group": 0,
    "parent_account": "Contributions"
   },
   {
    "account_name": "Corporate Sponsorships",
    "root_type": "Income",
    "is_group": 0,
    "parent_account": "Contributions"
   },
   {
    "account_name": "Foundation Grants",
    "root_type": "Income",
    "is_group": 0,
    "parent_account": "Contributions"
   },
   {
    "account_name": "Government Grants",
    "root_type": "Income",
    "is_group": 0,
    "parent_account": "Contributions"
   },
   {
    "account_name": "Membership Fees",
    "root_type": "Income",
    "is_group": 0,
    "parent_account": "REVENUE"
   },
   {
    "account_name": "Program Service Revenue",
    "root_type": "Income",
    "is_group": 0,
    "parent_account": "REVENUE"
   },
   {
    "account_name": "Interest and Investment Income",
    "root_type": "Income",
    "is_group": 0,
    "parent_account": "REVENUE"
   },
   {
    "account_name": "Fundraising Events",
    "root_type": "Income",
    "is_group": 0,
    "parent_account": "REVENUE"
   },
   {
    "account_name": "EXPENSES",
    "root_type": "Expense",
    "is_group": 1
   },
   {
    "account_name": "Program Expenses",
    "root_type": "Expense",
    "is_group": 1,
    "parent_account": "EXPENSES"
   },
   {
    "account_name": "Program A - Direct Costs",
    "root_type": "Expense",
    "is_group": 0,
    "parent_account": "Program Expenses"
   },
   {
    "account_name": "Program B - Direct Costs",
    "root_type": "Expense",
    "is_group": 0,
    "parent_account": "Program Expenses"
   },
   {
    "account_name": "Program Travel",
    "root_type": "Expense",
    "is_group": 0,
    "parent_account": "Program Expenses"
   },
   {
    "account_name": "Program Supplies",
    "root_type": "Expense",
    "is_group": 0,
    "parent_account": "Program Expenses"
   },
   {
    "account_name": "Program Personnel",
    "root_type": "Expense",
    "is_group": 0,
    "parent_account": "Program Expenses"
   },
   {
    "account_name": "Management and General",
    "root_type": "Expense",
    "is_group": 1,
    "parent_account": "EXPENSES"
   },
   {
    "account_name": "Administrative Salaries",
    "root_type": "Expense",
    "is_group": 0,
    "parent_account": "Management and General"
   },
   {
    "account_name": "Office Rent",
    "root_type": "Expense",
    "is_group": 0,
    "parent_account": "Management and General"
   },
   {
    "account_name": "Office Utilities",
    "root_type": "Expense",
    "is_group": 0,
    "parent_account": "Management and General"
   },
   {
    "account_name": "Office Supplies",
    "root_type": "Expense",
    "is_group": 0,
    "parent_account": "Management and General"
   },
   {
    "account_name": "Insurance",
    "root_type": "Expense",
    "is_group": 0,
    "parent_account": "Management and General"
   },
   {
    "account_name": "Professional Fees",
    "root_type": "Expense",
    "is_group": 0,
    "parent_account": "Management and General"
   },
   {
    "account_name": "Depreciation",
    "root_type": "Expense",
    "is_group": 0,
    "parent_account": "Management and General"
   },
   {
    "account_name": "Fundraising",
    "root_type": "Expense",
    "is_group": 1,
    "parent_account": "EXPENSES"
   },
   {
    "account_name": "Fundraising Personnel",
    "root_type": "Expense",
    "is_group": 0,
    "parent_account": "Fundraising"
   },
   {
    "account_name": "Fundraising Events Costs",
    "root_type": "Expense",
    "is_group": 0,
    "parent_account": "Fundraising"
   },
   {
    "account_name": "Marketing and Communications",
    "root_type": "Expense",
    "is_group": 0,
    "parent_account": "Fundraising"
   }
  ]
 },
 "PK": {
  "title": "Pakistan",
  "currency": "PKR",
  "vat_rate": 18,
  "accounts": [
   {
    "account_name": "1000 Assets",
    "root_type": "Asset",
    "is_group": 1
   },
   {
    "account_name": "1100 Cash and Cash Equivalents",
    "root_type": "Asset",
    "is_group": 1,
    "parent_account": "1000 Assets"
   },
   {
    "account_name": "1110 Cash - Operating",
    "root_type": "Asset",
    "is_group": 0,
    "parent_account": "1100 Cash and Cash Equivalents",
    "account_number": "1110"
   },
   {
    "account_name": "1120 Cash - Payroll",
    "root_type": "Asset",
    "is_group": 0,
    "parent_account": "1100 Cash and Cash Equivalents",
    "account_number": "1120"
   },
   {
    "account_name": "1130 Petty Cash",
    "root_type": "Asset",
    "is_group": 0,
    "parent_account": "1100 Cash and Cash Equivalents",
    "account_number": "1130"
   },
   {
    "account_name": "1140 Checking Account",
    "root_type": "Asset",
    "is_group": 0,
    "parent_account": "1100 Cash and Cash Equivalents",
    "account_number": "1140"
   },
   {
    "account_name": "1150 Savings Account",
    "root_type": "Asset",
    "is_group": 0,
    "parent_account": "1100 Cash and Cash Equivalents",
    "account_number": "1150"
   },
   {
    "account_name": "1200 Accounts Receivable",
    "root_type": "Asset",
    "is_group": 1,
    "parent_account": "1000 Assets"
   },
   {
    "account_name": "1210 Accounts Receivable - Trade",
    "root_type": "Asset",
    "is_group": 0,
    "parent_account": "1200 Accounts Receivable",
    "account_number": "1210"
   },
   {
    "account_name": "1220 Allowance for Doubtful Accounts",
    "root_type": "Asset",
    "is_group": 0,
    "parent_account": "1200 Accounts Receivable",
    "account_number": "1220"
   },
   {
    "account_name": "1230 Employee Receivables",
    "root_type": "Asset",
    "is_group": 0,
    "parent_account": "1200 Accounts Receivable",
    "account_number": "1230"
   },
   {
    "account_name": "1300 Inventory",
    "root_type": "Asset",
    "is_group": 1,
    "parent_account": "1000 Assets"
   },
   {
    "account_name": "1310 Raw Materials",
    "root_type": "Asset",
    "is_group": 0,
    "parent_account": "1300 Inventory",
    "account_number": "1310"
   },
   {
    "account_name": "1320 Work in Progress",
    "root_type": "Asset",
    "is_group": 0,
    "parent_account": "1300 Inventory",
    "account_number": "1320"
   },
   {
    "account_name": "1330 Finished Goods",
    "root_type": "Asset",
    "is_group": 0,
    "parent_account": "1300 Inventory",
    "account_number": "1330"
   },
   {
    "account_name": "1400 Prepaid Expenses",
    "root_type": "Asset",
    "is_group": 1,
    "parent_account": "1000 Assets"
   },
   {
    "account_name": "1410 Prepaid Insurance",
    "root_type": "Asset",
    "is_group": 0,
    "parent_account": "1400 Prepaid Expenses",
    "account_number": "1410"
   },
   {
    "account_name": "1420 Prepaid Rent",
    "root_type": "Asset",
    "is_group": 0,
    "parent_account": "1400 Prepaid Expenses",
    "account_number": "1420"
   },
   {
    "account_name": "1500 Fixed Assets",
    "root_type": "Asset",
    "is_group": 1,
    "parent_account": "1000 Assets"
   },
   {
    "account_name": "1510 Land",
    "root_type": "Asset",
    "is_group": 0,
    "parent_account": "1500 Fixed Assets",
    "account_number": "1510"
   },
   {
    "account_name": "1520 Buildings",
    "root_type": "Asset",
    "is_group": 0,
    "parent_account": "1500 Fixed Assets",
    "account_number": "1520"
   },
   {
    "account_name": "1530 Machinery and Equipment",
    "root_type": "Asset",
    "is_group": 0,
    "parent_account": "1500 Fixed Assets",
    "account_number": "1530"
   },
   {
    "account_name": "1540 Vehicles",
    "root_type": "Asset",
    "is_group": 0,
    "parent_account": "1500 Fixed Assets",
    "account_number": "1540"
   },
   {
    "account_name": "1550 Furniture and Fixtures",
    "root_type": "Asset",
    "is_group": 0,
    "parent_account": "1500 Fixed Assets",
    "account_number": "1550"
   },
   {
    "account_name": "1560 Computers and Software",
    "root_type": "Asset",
    "is_group": 0,
    "parent_account": "1500 Fixed Assets",
    "account_number": "1560"
   },
   {
    "account_name": "1600 Accumulated Depreciation",
    "root_type": "Asset",
    "is_group": 1,
    "parent_account": "1000 Assets"
   },
   {
    "account_name": "1610 Accum Dep - Buildings",
    "root_type": "Asset",
    "is_group": 0,
    "parent_account": "1600 Accumulated Depreciation",
    "account_number": "1610"
   },
   {
    "account_name": "1620 Accum Dep - Equipment",
    "root_type": "Asset",
    "is_group": 0,
    "parent_account": "1600 Accumulated Depreciation",
    "account_number": "1620"
   },
   {
    "account_name": "1630 Accum Dep - Vehicles",
    "root_type": "Asset",
    "is_group": 0,
    "parent_account": "1600 Accumulated Depreciation",
    "account_number": "1630"
   },
   {
    "account_name": "1700 Intangible Assets",
    "root_type": "Asset",
    "is_group": 1,
    "parent_account": "1000 Assets"
   },
   {
    "account_name": "1710 Goodwill",
    "root_type": "Asset",
    "is_group": 0,
    "parent_account": "1700 Intangible Assets",
    "account_number": "1710"
   },
   {
    "account_name": "1720 Patents",
    "root_type": "Asset",
    "is_group": 0,
    "parent_account": "1700 Intangible Assets",
    "account_number": "1720"
   },
   {
    "account_name": "1730 Trademarks",
    "root_type": "Asset",
    "is_group": 0,
    "parent_account": "1700 Intangible Assets",
    "account_number": "1730"
   },
   {
    "account_name": "1800 Other Assets",
    "root_type": "Asset",
    "is_group": 1,
    "parent_account": "1000 Assets"
   },
   {
    "account_name": "1810 Investments",
    "root_type": "Asset",
    "is_group": 0,
    "parent_account": "1800 Other Assets",
    "account_number": "1810"
   },
   {
    "account_name": "1820 Deposits",
    "root_type": "Asset",
    "is_group": 0,
    "parent_account": "1800 Other Assets",
    "account_number": "1820"
   },
   {
    "account_name": "2000 Liabilities",
    "root_type": "Liability",
    "is_group": 1
   },
   {
    "account_name": "2100 Accounts Payable",
    "root_type": "Liability",
    "is_group": 1,
    "parent_account": "2000 Liabilities"
   },
   {
    "account_name": "2110 Accounts Payable - Trade",
    "root_type": "Liability",
    "is_group": 0,
    "parent_account": "2100 Accounts Payable",
    "account_number": "2110"
   },
   {
    "account_name": "2120 Accrued Liabilities",
    "root_type": "Liability",
    "is_group": 0,
    "parent_account": "2100 Accounts Payable",
    "account_number": "2120"
   },
   {
    "account_name": "2200 Tax Payables",
    "root_type": "Liability",
    "is_group": 1,
    "parent_account": "2000 Liabilities"
   },
   {
    "account_name": "2210 VAT/Sales Tax Payable",
    "root_type": "Liability",
    "is_group": 0,
    "parent_account": "2200 Tax Payables",
    "account_number": "2210"
   },
   {
    "account_name": "2220 Income Tax Payable",
    "root_type": "Liability",
    "is_group": 0,
    "parent_account": "2200 Tax Payables",
    "account_number": "2220"
   },
   {
    "account_name": "2230 Payroll Tax Payable",
    "root_type": "Liability",
    "is_group": 0,
    "parent_account": "2200 Tax Payables",
    "account_number": "2230"
   },
   {
    "account_name": "2300 Accrued Expenses",
    "root_type": "Liability",
    "is_group": 1,
    "parent_account": "2000 Liabilities"
   },
   {
    "account_name": "2310 Accrued Salaries",
    "root_type": "Liability",
    "is_group": 0,
    "parent_account": "2300 Accrued Expenses",
    "account_number": "2310"
   },
   {
    "account_name": "2320 Accrued Interest",
    "root_type": "Liability",
    "is_group": 0,
    "parent_account": "2300 Accrued Expenses",
    "account_number": "2320"
   },
   {
    "account_name": "2400 Deferred Revenue",
    "root_type": "Liability",
    "is_group": 1,
    "parent_account": "2000 Liabilities"
   },
   {
    "account_name": "2410 Unearned Revenue",
    "root_type": "Liability",
    "is_group": 0,
    "parent_account": "2400 Deferred Revenue",
    "account_number": "2410"
   },
   {
    "account_name": "2500 Long Term Liabilities",
    "root_type": "Liability",
    "is_group": 1,
    "parent_account": "2000 Liabilities"
   },
   {
    "account_name": "2510 Bank Loans",
    "root_type": "Liability",
    "is_group": 0,
    "parent_account": "2500 Long Term Liabilities",
    "account_number": "2510"
   },
   {
    "account_name": "2520 Notes Payable",
    "root_type": "Liability",
    "is_group": 0,
    "parent_account": "2500 Long Term Liabilities",
    "account_number": "2520"
   },
   {
    "account_name": "2530 Bonds Payable",
    "root_type": "Liability",
    "is_group": 0,
    "parent_account": "2500 Long Term Liabilities",
    "account_number": "2530"
   },
   {
    "account_name": "3000 Equity",
    "root_type": "Equity",
    "is_group": 1
   },
   {
    "account_name": "3100 Common Stock",
    "root_type": "Equity",
    "is_group": 0,
    "parent_account": "3000 Equity",
    "account_number": "3100"
   },
   {
    "account_name": "3200 Additional Paid-in Capital",
    "root_type": "Equity",
    "is_group": 0,
    "parent_account": "3000 Equity",
    "account_number": "3200"
   },
   {
    "account_name": "3300 Retained Earnings",
    "root_type": "Equity",
    "is_group": 0,
    "parent_account": "3000 Equity",
    "account_number": "3300"
   },
   {
    "account_name": "3400 Current Year Earnings",
    "root_type": "Equity",
    "is_group": 0,
    "parent_account": "3000 Equity",
    "account_number": "3400"
   },
   {
    "account_name": "3500 Owner's Draws",
    "root_type": "Equity",
    "is_group": 0,
    "parent_account": "3000 Equity",
    "account_number": "3500"
   },
   {
    "account_name": "4000 Income",
    "root_type": "Income",
    "is_group": 1
   },
   {
    "account_name": "4100 Revenue",
    "root_type": "Income",
    "is_group": 1,
    "parent_account": "4000 Income"
   },
   {
    "account_name": "4110 Product Sales",
    "root_type": "Income",
    "is_group": 0,
    "parent_account": "4100 Revenue",
    "account_number": "4110"
   },
   {
    "account_name": "4120 Service Revenue",
    "root_type": "Income",
    "is_group": 0,
    "parent_account": "4100 Revenue",
    "account_number": "4120"
   },
   {
    "account_name": "4130 Interest Income",
    "root_type": "Income",
    "is_group": 0,
    "parent_account": "4100 Revenue",
    "account_number": "4130"
   },
   {
    "account_name": "4140 Rental Income",
    "root_type": "Income",
    "is_group": 0,
    "parent_account": "4100 Revenue",
    "account_number": "4140"
   },
   {
    "account_name": "4200 Other Income",
    "root_type": "Income",
    "is_group": 1,
    "parent_account": "4000 Income"
   },
   {
    "account_name": "4210 Gain on Sale of Assets",
    "root_type": "Income",
    "is_group": 0,
    "parent_account": "4200 Other Income",
    "account_number": "4210"
   },
   {
    "account_name": "4220 Foreign Exchange Gain",
    "root_type": "Income",
    "is_group": 0,
    "parent_account": "4200 Other Income",
    "account_number": "4220"
   },
   {
    "account_name": "5000 Expenses",
    "root_type": "Expense",
    "is_group": 1
   },
   {
    "account_name": "5100 Cost of Goods Sold",
    "root_type": "Expense",
    "is_group": 1,
    "parent_account": "5000 Expenses"
   },
   {
    "account_name": "5110 COGS - Materials",
    "root_type": "Expense",
    "is_group": 0,
    "parent_account": "5100 Cost of Goods Sold",
    "account_number": "5110"
   },
   {
    "account_name": "5120 COGS - Labor",
    "root_type": "Expense",
    "is_group": 0,
    "parent_account": "5100 Cost of Goods Sold",
    "account_number": "5120"
   },
   {
    "account_name": "5130 COGS - Overhead",
    "root_type": "Expense",
    "is_group": 0,
    "parent_account": "5100 Cost of Goods Sold",
    "account_number": "5130"
   },
   {
    "account_name": "5200 Salaries and Wages",
    "root_type": "Expense",
    "is_group": 0,
    "parent_account": "5000 Expenses",
    "account_number": "5200"
   },
   {
    "account_name": "5300 Rent and Utilities",
    "root_type": "Expense",
    "is_group": 1,
    "parent_account": "5000 Expenses"
   },
   {
    "account_name": "5310 Rent Expense",
    "root_type": "Expense",
    "is_group": 0,
    "parent_account": "5300 Rent and Utilities",
    "account_number": "5310"
   },
   {
    "account_name": "5320 Electricity",
    "root_type": "Expense",
    "is_group": 0,
    "parent_account": "5300 Rent and Utilities",
    "account_number": "5320"
   },
   {
    "account_name": "5330 Water and Gas",
    "root_type": "Expense",
    "is_group": 0,
    "parent_account": "5300 Rent and Utilities",
    "account_number": "5330"
   },
   {
    "account_name": "5340 Internet and Telephone",
    "root_type": "Expense",
    "is_group": 0,
    "parent_account": "5300 Rent and Utilities",
    "account_number": "5340"
   },
   {
    "account_name": "5400 Office and Admin",
    "root_type": "Expense",
    "is_group": 1,
    "parent_account": "5000 Expenses"
   },
   {
    "account_name": "5410 Office Supplies",
    "root_type": "Expense",
    "is_group": 0,
    "parent_account": "5400 Office and Admin",
    "account_number": "5410"
   },
   {
    "account_name": "5420 Insurance",
    "root_type": "Expense",
    "is_group": 0,
    "parent_account": "5400 Office and Admin",
    "account_number": "5420"
   },
   {
    "account_name": "5430 Legal and Professional",
    "root_type": "Expense",
    "is_group": 0,
    "parent_account": "5400 Office and Admin",
    "account_number": "5430"
   },
   {
    "account_name": "5440 Bank Charges",
    "root_type": "Expense",
    "is_group": 0,
    "parent_account": "5400 Office and Admin",
    "account_number": "5440"
   },
   {
    "account_name": "5500 Depreciation and Amortization",
    "root_type": "Expense",
    "is_group": 0,
    "parent_account": "5000 Expenses",
    "account_number": "5500"
   },
   {
    "account_name": "5600 Travel and Entertainment",
    "root_type": "Expense",
    "is_group": 1,
    "parent_account": "5000 Expenses"
   },
   {
    "account_name": "5610 Travel Expense",
    "root_type": "Expense",
    "is_group": 0,
    "parent_account": "5600 Travel and Entertainment",
    "account_number": "5610"
   },
   {
    "account_name": "5620 Meals and Entertainment",
    "root_type": "Expense",
    "is_group": 0,
    "parent_account": "5600 Travel and Entertainment",
    "account_number": "5620"
   },
   {
    "account_name": "5700 Marketing and Advertising",
    "root_type": "Expense",
    "is_group": 0,
    "parent_account": "5000 Expenses",
    "account_number": "5700"
   },
   {
    "account_name": "5800 Taxes and Licenses",
    "root_type": "Expense",
    "is_group": 0,
    "parent_account": "5000 Expenses",
    "account_number": "5800"
   },
   {
    "account_name": "5900 Other Expenses",
    "root_type": "Expense",
    "is_group": 1,
    "parent_account": "5000 Expenses"
   },
   {
    "account_name": "5910 Loss on Asset Disposal",
    "root_type": "Expense",
    "is_group": 0,
    "parent_account": "5900 Other Expenses",
    "account_number": "5910"
   },
   {
    "account_name": "5920 Foreign Exchange Loss",
    "root_type": "Expense",
    "is_group": 0,
    "parent_account": "5900 Other Expenses",
    "account_number": "5920"
   },
   {
    "account_name": "5990 Miscellaneous",
    "root_type": "Expense",
    "is_group": 0,
    "parent_account": "5900 Other Expenses",
    "account_number": "5990"
   }
  ]
 },
 "MY": {
  "title": "Malaysia",
  "currency": "MYR",
  "vat_rate": 6,
  "accounts": [
   {
    "account_name": "1000 Assets",
    "root_type": "Asset",
    "is_group": 1
   },
   {
    "account_name": "1100 Cash and Cash Equivalents",
    "root_type": "Asset",
    "is_group": 1,
    "parent_account": "1000 Assets"
   },
   {
    "account_name": "1110 Cash - Operating",
    "root_type": "Asset",
    "is_group": 0,
    "parent_account": "1100 Cash and Cash Equivalents",
    "account_number": "1110"
   },
   {
    "account_name": "1120 Cash - Payroll",
    "root_type": "Asset",
    "is_group": 0,
    "parent_account": "1100 Cash and Cash Equivalents",
    "account_number": "1120"
   },
   {
    "account_name": "1130 Petty Cash",
    "root_type": "Asset",
    "is_group": 0,
    "parent_account": "1100 Cash and Cash Equivalents",
    "account_number": "1130"
   },
   {
    "account_name": "1140 Checking Account",
    "root_type": "Asset",
    "is_group": 0,
    "parent_account": "1100 Cash and Cash Equivalents",
    "account_number": "1140"
   },
   {
    "account_name": "1150 Savings Account",
    "root_type": "Asset",
    "is_group": 0,
    "parent_account": "1100 Cash and Cash Equivalents",
    "account_number": "1150"
   },
   {
    "account_name": "1200 Accounts Receivable",
    "root_type": "Asset",
    "is_group": 1,
    "parent_account": "1000 Assets"
   },
   {
    "account_name": "1210 Accounts Receivable - Trade",
    "root_type": "Asset",
    "is_group": 0,
    "parent_account": "1200 Accounts Receivable",
    "account_number": "1210"
   },
   {
    "account_name": "1220 Allowance for Doubtful Accounts",
    "root_type": "Asset",
    "is_group": 0,
    "parent_account": "1200 Accounts Receivable",
    "account_number": "1220"
   },
   {
    "account_name": "1230 Employee Receivables",
    "root_type": "Asset",
    "is_group": 0,
    "parent_account": "1200 Accounts Receivable",
    "account_number": "1230"
   },
   {
    "account_name": "1300 Inventory",
    "root_type": "Asset",
    "is_group": 1,
    "parent_account": "1000 Assets"
   },
   {
    "account_name": "1310 Raw Materials",
    "root_type": "Asset",
    "is_group": 0,
    "parent_account": "1300 Inventory",
    "account_number": "1310"
   },
   {
    "account_name": "1320 Work in Progress",
    "root_type": "Asset",
    "is_group": 0,
    "parent_account": "1300 Inventory",
    "account_number": "1320"
   },
   {
    "account_name": "1330 Finished Goods",
    "root_type": "Asset",
    "is_group": 0,
    "parent_account": "1300 Inventory",
    "account_number": "1330"
   },
   {
    "account_name": "1400 Prepaid Expenses",
    "root_type": "Asset",
    "is_group": 1,
    "parent_account": "1000 Assets"
   },
   {
    "account_name": "1410 Prepaid Insurance",
    "root_type": "Asset",
    "is_group": 0,
    "parent_account": "1400 Prepaid Expenses",
    "account_number": "1410"
   },
   {
    "account_name": "1420 Prepaid Rent",
    "root_type": "Asset",
    "is_group": 0,
    "parent_account": "1400 Prepaid Expenses",
    "account_number": "1420"
   },
   {
    "account_name": "1500 Fixed Assets",
    "root_type": "Asset",
    "is_group": 1,
    "parent_account": "1000 Assets"
   },
   {
    "account_name": "1510 Land",
    "root_type": "Asset",
    "is_group": 0,
    "parent_account": "1500 Fixed Assets",
    "account_number": "1510"
   },
   {
    "account_name": "1520 Buildings",
    "root_type": "Asset",
    "is_group": 0,
    "parent_account": "1500 Fixed Assets",
    "account_number": "1520"
   },
   {
    "account_name": "1530 Machinery and Equipment",
    "root_type": "Asset",
    "is_group": 0,
    "parent_account": "1500 Fixed Assets",
    "account_number": "1530"
   },
   {
    "account_name": "1540 Vehicles",
    "root_type": "Asset",
    "is_group": 0,
    "parent_account": "1500 Fixed Assets",
    "account_number": "1540"
   },
   {
    "account_name": "1550 Furniture and Fixtures",
    "root_type": "Asset",
    "is_group": 0,
    "parent_account": "1500 Fixed Assets",
    "account_number": "1550"
   },
   {
    "account_name": "1560 Computers and Software",
    "root_type": "Asset",
    "is_group": 0,
    "parent_account": "1500 Fixed Assets",
    "account_number": "1560"
   },
   {
    "account_name": "1600 Accumulated Depreciation",
    "root_type": "Asset",
    "is_group": 1,
    "parent_account": "1000 Assets"
   },
   {
    "account_name": "1610 Accum Dep - Buildings",
    "root_type": "Asset",
    "is_group": 0,
    "parent_account": "1600 Accumulated Depreciation",
    "account_number": "1610"
   },
   {
    "account_name": "1620 Accum Dep - Equipment",
    "root_type": "Asset",
    "is_group": 0,
    "parent_account": "1600 Accumulated Depreciation",
    "account_number": "1620"
   },
   {
    "account_name": "1630 Accum Dep - Vehicles",
    "root_type": "Asset",
    "is_group": 0,
    "parent_account": "1600 Accumulated Depreciation",
    "account_number": "1630"
   },
   {
    "account_name": "1700 Intangible Assets",
    "root_type": "Asset",
    "is_group": 1,
    "parent_account": "1000 Assets"
   },
   {
    "account_name": "1710 Goodwill",
    "root_type": "Asset",
    "is_group": 0,
    "parent_account": "1700 Intangible Assets",
    "account_number": "1710"
   },
   {
    "account_name": "1720 Patents",
    "root_type": "Asset",
    "is_group": 0,
    "parent_account": "1700 Intangible Assets",
    "account_number": "1720"
   },
   {
    "account_name": "1730 Trademarks",
    "root_type": "Asset",
    "is_group": 0,
    "parent_account": "1700 Intangible Assets",
    "account_number": "1730"
   },
   {
    "account_name": "1800 Other Assets",
    "root_type": "Asset",
    "is_group": 1,
    "parent_account": "1000 Assets"
   },
   {
    "account_name": "1810 Investments",
    "root_type": "Asset",
    "is_group": 0,
    "parent_account": "1800 Other Assets",
    "account_number": "1810"
   },
   {
    "account_name": "1820 Deposits",
    "root_type": "Asset",
    "is_group": 0,
    "parent_account": "1800 Other Assets",
    "account_number": "1820"
   },
   {
    "account_name": "2000 Liabilities",
    "root_type": "Liability",
    "is_group": 1
   },
   {
    "account_name": "2100 Accounts Payable",
    "root_type": "Liability",
    "is_group": 1,
    "parent_account": "2000 Liabilities"
   },
   {
    "account_name": "2110 Accounts Payable - Trade",
    "root_type": "Liability",
    "is_group": 0,
    "parent_account": "2100 Accounts Payable",
    "account_number": "2110"
   },
   {
    "account_name": "2120 Accrued Liabilities",
    "root_type": "Liability",
    "is_group": 0,
    "parent_account": "2100 Accounts Payable",
    "account_number": "2120"
   },
   {
    "account_name": "2200 Tax Payables",
    "root_type": "Liability",
    "is_group": 1,
    "parent_account": "2000 Liabilities"
   },
   {
    "account_name": "2210 VAT/Sales Tax Payable",
    "root_type": "Liability",
    "is_group": 0,
    "parent_account": "2200 Tax Payables",
    "account_number": "2210"
   },
   {
    "account_name": "2220 Income Tax Payable",
    "root_type": "Liability",
    "is_group": 0,
    "parent_account": "2200 Tax Payables",
    "account_number": "2220"
   },
   {
    "account_name": "2230 Payroll Tax Payable",
    "root_type": "Liability",
    "is_group": 0,
    "parent_account": "2200 Tax Payables",
    "account_number": "2230"
   },
   {
    "account_name": "2300 Accrued Expenses",
    "root_type": "Liability",
    "is_group": 1,
    "parent_account": "2000 Liabilities"
   },
   {
    "account_name": "2310 Accrued Salaries",
    "root_type": "Liability",
    "is_group": 0,
    "parent_account": "2300 Accrued Expenses",
    "account_number": "2310"
   },
   {
    "account_name": "2320 Accrued Interest",
    "root_type": "Liability",
    "is_group": 0,
    "parent_account": "2300 Accrued Expenses",
    "account_number": "2320"
   },
   {
    "account_name": "2400 Deferred Revenue",
    "root_type": "Liability",
    "is_group": 1,
    "parent_account": "2000 Liabilities"
   },
   {
    "account_name": "2410 Unearned Revenue",
    "root_type": "Liability",
    "is_group": 0,
    "parent_account": "2400 Deferred Revenue",
    "account_number": "2410"
   },
   {
    "account_name": "2500 Long Term Liabilities",
    "root_type": "Liability",
    "is_group": 1,
    "parent_account": "2000 Liabilities"
   },
   {
    "account_name": "2510 Bank Loans",
    "root_type": "Liability",
    "is_group": 0,
    "parent_account": "2500 Long Term Liabilities",
    "account_number": "2510"
   },
   {
    "account_name": "2520 Notes Payable",
    "root_type": "Liability",
    "is_group": 0,
    "parent_account": "2500 Long Term Liabilities",
    "account_number": "2520"
   },
   {
    "account_name": "2530 Bonds Payable",
    "root_type": "Liability",
    "is_group": 0,
    "parent_account": "2500 Long Term Liabilities",
    "account_number": "2530"
   },
   {
    "account_name": "3000 Equity",
    "root_type": "Equity",
    "is_group": 1
   },
   {
    "account_name": "3100 Common Stock",
    "root_type": "Equity",
    "is_group": 0,
    "parent_account": "3000 Equity",
    "account_number": "3100"
   },
   {
    "account_name": "3200 Additional Paid-in Capital",
    "root_type": "Equity",
    "is_group": 0,
    "parent_account": "3000 Equity",
    "account_number": "3200"
   },
   {
    "account_name": "3300 Retained Earnings",
    "root_type": "Equity",
    "is_group": 0,
    "parent_account": "3000 Equity",
    "account_number": "3300"
   },
   {
    "account_name": "3400 Current Year Earnings",
    "root_type": "Equity",
    "is_group": 0,
    "parent_account": "3000 Equity",
    "account_number": "3400"
   },
   {
    "account_name": "3500 Owner's Draws",
    "root_type": "Equity",
    "is_group": 0,
    "parent_account": "3000 Equity",
    "account_number": "3500"
   },
   {
    "account_name": "4000 Income",
    "root_type": "Income",
    "is_group": 1
   },
   {
    "account_name": "4100 Revenue",
    "root_type": "Income",
    "is_group": 1,
    "parent_account": "4000 Income"
   },
   {
    "account_name": "4110 Product Sales",
    "root_type": "Income",
    "is_group": 0,
    "parent_account": "4100 Revenue",
    "account_number": "4110"
   },
   {
    "account_name": "4120 Service Revenue",
    "root_type": "Income",
    "is_group": 0,
    "parent_account": "4100 Revenue",
    "account_number": "4120"
   },
   {
    "account_name": "4130 Interest Income",
    "root_type": "Income",
    "is_group": 0,
    "parent_account": "4100 Revenue",
    "account_number": "4130"
   },
   {
    "account_name": "4140 Rental Income",
    "root_type": "Income",
    "is_group": 0,
    "parent_account": "4100 Revenue",
    "account_number": "4140"
   },
   {
    "account_name": "4200 Other Income",
    "root_type": "Income",
    "is_group": 1,
    "parent_account": "4000 Income"
   },
   {
    "account_name": "4210 Gain on Sale of Assets",
    "root_type": "Income",
    "is_group": 0,
    "parent_account": "4200 Other Income",
    "account_number": "4210"
   },
   {
    "account_name": "4220 Foreign Exchange Gain",
    "root_type": "Income",
    "is_group": 0,
    "parent_account": "4200 Other Income",
    "account_number": "4220"
   },
   {
    "account_name": "5000 Expenses",
    "root_type": "Expense",
    "is_group": 1
   },
   {
    "account_name": "5100 Cost of Goods Sold",
    "root_type": "Expense",
    "is_group": 1,
    "parent_account": "5000 Expenses"
   },
   {
    "account_name": "5110 COGS - Materials",
    "root_type": "Expense",
    "is_group": 0,
    "parent_account": "5100 Cost of Goods Sold",
    "account_number": "5110"
   },
   {
    "account_name": "5120 COGS - Labor",
    "root_type": "Expense",
    "is_group": 0,
    "parent_account": "5100 Cost of Goods Sold",
    "account_number": "5120"
   },
   {
    "account_name": "5130 COGS - Overhead",
    "root_type": "Expense",
    "is_group": 0,
    "parent_account": "5100 Cost of Goods Sold",
    "account_number": "5130"
   },
   {
    "account_name": "5200 Salaries and Wages",
    "root_type": "Expense",
    "is_group": 0,
    "parent_account": "5000 Expenses",
    "account_number": "5200"
   },
   {
    "account_name": "5300 Rent and Utilities",
    "root_type": "Expense",
    "is_group": 1,
    "parent_account": "5000 Expenses"
   },
   {
    "account_name": "5310 Rent Expense",
    "root_type": "Expense",
    "is_group": 0,
    "parent_account": "5300 Rent and Utilities",
    "account_number": "5310"
   },
   {
    "account_name": "5320 Electricity",
    "root_type": "Expense",
    "is_group": 0,
    "parent_account": "5300 Rent and Utilities",
    "account_number": "5320"
   },
   {
    "account_name": "5330 Water and Gas",
    "root_type": "Expense",
    "is_group": 0,
    "parent_account": "5300 Rent and Utilities",
    "account_number": "5330"
   },
   {
    "account_name": "5340 Internet and Telephone",
    "root_type": "Expense",
    "is_group": 0,
    "parent_account": "5300 Rent and Utilities",
    "account_number": "5340"
   },
   {
    "account_name": "5400 Office and Admin",
    "root_type": "Expense",
    "is_group": 1,
    "parent_account": "5000 Expenses"
   },
   {
    "account_name": "5410 Office Supplies",
    "root_type": "Expense",
    "is_group": 0,
    "parent_account": "5400 Office and Admin",
    "account_number": "5410"
   },
   {
    "account_name": "5420 Insurance",
    "root_type": "Expense",
    "is_group": 0,
    "parent_account": "5400 Office and Admin",
    "account_number": "5420"
   },
   {
    "account_name": "5430 Legal and Professional",
    "root_type": "Expense",
    "is_group": 0,
    "parent_account": "5400 Office and Admin",
    "account_number": "5430"
   },
   {
    "account_name": "5440 Bank Charges",
    "root_type": "Expense",
    "is_group": 0,
    "parent_account": "5400 Office and Admin",
    "account_number": "5440"
   },
   {
    "account_name": "5500 Depreciation and Amortization",
    "root_type": "Expense",
    "is_group": 0,
    "parent_account": "5000 Expenses",
    "account_number": "5500"
   },
   {
    "account_name": "5600 Travel and Entertainment",
    "root_type": "Expense",
    "is_group": 1,
    "parent_account": "5000 Expenses"
   },
   {
    "account_name": "5610 Travel Expense",
    "root_type": "Expense",
    "is_group": 0,
    "parent_account": "5600 Travel and Entertainment",
    "account_number": "5610"
   },
   {
    "account_name": "5620 Meals and Entertainment",
    "root_type": "Expense",
    "is_group": 0,
    "parent_account": "5600 Travel and Entertainment",
    "account_number": "5620"
   },
   {
    "account_name": "5700 Marketing and Advertising",
    "root_type": "Expense",
    "is_group": 0,
    "parent_account": "5000 Expenses",
    "account_number": "5700"
   },
   {
    "account_name": "5800 Taxes and Licenses",
    "root_type": "Expense",
    "is_group": 0,
    "parent_account": "5000 Expenses",
    "account_number": "5800"
   },
   {
    "account_name": "5900 Other Expenses",
    "root_type": "Expense",
    "is_group": 1,
    "parent_account": "5000 Expenses"
   },
   {
    "account_name": "5910 Loss on Asset Disposal",
    "root_type": "Expense",
    "is_group": 0,
    "parent_account": "5900 Other Expenses",
    "account_number": "5910"
   },
   {
    "account_name": "5920 Foreign Exchange Loss",
    "root_type": "Expense",
    "is_group": 0,
    "parent_account": "5900 Other Expenses",
    "account_number": "5920"
   },
   {
    "account_name": "5990 Miscellaneous",
    "root_type": "Expense",
    "is_group": 0,
    "parent_account": "5900 Other Expenses",
    "account_number": "5990"
   }
  ]
 },
 "UAE": {
  "title": "UAE",
  "currency": "AED",
  "vat_rate": 5,
  "accounts": [
   {
    "account_name": "1000 Assets",
    "root_type": "Asset",
    "is_group": 1
   },
   {
    "account_name": "1100 Cash and Cash Equivalents",
    "root_type": "Asset",
    "is_group": 1,
    "parent_account": "1000 Assets"
   },
   {
    "account_name": "1110 Cash - Operating",
    "root_type": "Asset",
    "is_group": 0,
    "parent_account": "1100 Cash and Cash Equivalents",
    "account_number": "1110"
   },
   {
    "account_name": "1120 Cash - Payroll",
    "root_type": "Asset",
    "is_group": 0,
    "parent_account": "1100 Cash and Cash Equivalents",
    "account_number": "1120"
   },
   {
    "account_name": "1130 Petty Cash",
    "root_type": "Asset",
    "is_group": 0,
    "parent_account": "1100 Cash and Cash Equivalents",
    "account_number": "1130"
   },
   {
    "account_name": "1140 Checking Account",
    "root_type": "Asset",
    "is_group": 0,
    "parent_account": "1100 Cash and Cash Equivalents",
    "account_number": "1140"
   },
   {
    "account_name": "1150 Savings Account",
    "root_type": "Asset",
    "is_group": 0,
    "parent_account": "1100 Cash and Cash Equivalents",
    "account_number": "1150"
   },
   {
    "account_name": "1200 Accounts Receivable",
    "root_type": "Asset",
    "is_group": 1,
    "parent_account": "1000 Assets"
   },
   {
    "account_name": "1210 Accounts Receivable - Trade",
    "root_type": "Asset",
    "is_group": 0,
    "parent_account": "1200 Accounts Receivable",
    "account_number": "1210"
   },
   {
    "account_name": "1220 Allowance for Doubtful Accounts",
    "root_type": "Asset",
    "is_group": 0,
    "parent_account": "1200 Accounts Receivable",
    "account_number": "1220"
   },
   {
    "account_name": "1230 Employee Receivables",
    "root_type": "Asset",
    "is_group": 0,
    "parent_account": "1200 Accounts Receivable",
    "account_number": "1230"
   },
   {
    "account_name": "1300 Inventory",
    "root_type": "Asset",
    "is_group": 1,
    "parent_account": "1000 Assets"
   },
   {
    "account_name": "1310 Raw Materials",
    "root_type": "Asset",
    "is_group": 0,
    "parent_account": "1300 Inventory",
    "account_number": "1310"
   },
   {
    "account_name": "1320 Work in Progress",
    "root_type": "Asset",
    "is_group": 0,
    "parent_account": "1300 Inventory",
    "account_number": "1320"
   },
   {
    "account_name": "1330 Finished Goods",
    "root_type": "Asset",
    "is_group": 0,
    "parent_account": "1300 Inventory",
    "account_number": "1330"
   },
   {
    "account_name": "1400 Prepaid Expenses",
    "root_type": "Asset",
    "is_group": 1,
    "parent_account": "1000 Assets"
   },
   {
    "account_name": "1410 Prepaid Insurance",
    "root_type": "Asset",
    "is_group": 0,
    "parent_account": "1400 Prepaid Expenses",
    "account_number": "1410"
   },
   {
    "account_name": "1420 Prepaid Rent",
    "root_type": "Asset",
    "is_group": 0,
    "parent_account": "1400 Prepaid Expenses",
    "account_number": "1420"
   },
   {
    "account_name": "1500 Fixed Assets",
    "root_type": "Asset",
    "is_group": 1,
    "parent_account": "1000 Assets"
   },
   {
    "account_name": "1510 Land",
    "root_type": "Asset",
    "is_group": 0,
    "parent_account": "1500 Fixed Assets",
    "account_number": "1510"
   },
   {
    "account_name": "1520 Buildings",
    "root_type": "Asset",
    "is_group": 0,
    "parent_account": "1500 Fixed Assets",
    "account_number": "1520"
   },
   {
    "account_name": "1530 Machinery and Equipment",
    "root_type": "Asset",
    "is_group": 0,
    "parent_account": "1500 Fixed Assets",
    "account_number": "1530"
   },
   {
    "account_name": "1540 Vehicles",
    "root_type": "Asset",
    "is_group": 0,
    "parent_account": "1500 Fixed Assets",
    "account_number": "1540"
   },
   {
    "account_name": "1550 Furniture and Fixtures",
    "root_type": "Asset",
    "is_group": 0,
    "parent_account": "1500 Fixed Assets",
    "account_number": "1550"
   },
   {
    "account_name": "1560 Computers and Software",
    "root_type": "Asset",
    "is_group": 0,
    "parent_account": "1500 Fixed Assets",
    "account_number": "1560"
   },
   {
    "account_name": "1600 Accumulated Depreciation",
    "root_type": "Asset",
    "is_group": 1,
    "parent_account": "1000 Assets"
   },
   {
    "account_name": "1610 Accum Dep - Buildings",
    "root_type": "Asset",
    "is_group": 0,
    "parent_account": "1600 Accumulated Depreciation",
    "account_number": "1610"
   },
   {
    "account_name": "1620 Accum Dep - Equipment",
    "root_type": "Asset",
    "is_group": 0,
    "parent_account": "1600 Accumulated Depreciation",
    "account_number": "1620"
   },
   {
    "account_name": "1630 Accum Dep - Vehicles",
    "root_type": "Asset",
    "is_group": 0,
    "parent_account": "1600 Accumulated Depreciation",
    "account_number": "1630"
   },
   {
    "account_name": "1700 Intangible Assets",
    "root_type": "Asset",
    "is_group": 1,
    "parent_account": "1000 Assets"
   },
   {
    "account_name": "1710 Goodwill",
    "root_type": "Asset",
    "is_group": 0,
    "parent_account": "1700 Intangible Assets",
    "account_number": "1710"
   },
   {
    "account_name": "1720 Patents",
    "root_type": "Asset",
    "is_group": 0,
    "parent_account": "1700 Intangible Assets",
    "account_number": "1720"
   },
   {
    "account_name": "1730 Trademarks",
    "root_type": "Asset",
    "is_group": 0,
    "parent_account": "1700 Intangible Assets",
    "account_number": "1730"
   },
   {
    "account_name": "1800 Other Assets",
    "root_type": "Asset",
    "is_group": 1,
    "parent_account": "1000 Assets"
   },
   {
    "account_name": "1810 Investments",
    "root_type": "Asset",
    "is_group": 0,
    "parent_account": "1800 Other Assets",
    "account_number": "1810"
   },
   {
    "account_name": "1820 Deposits",
    "root_type": "Asset",
    "is_group": 0,
    "parent_account": "1800 Other Assets",
    "account_number": "1820"
   },
   {
    "account_name": "2000 Liabilities",
    "root_type": "Liability",
    "is_group": 1
   },
   {
    "account_name": "2100 Accounts Payable",
    "root_type": "Liability",
    "is_group": 1,
    "parent_account": "2000 Liabilities"
   },
   {
    "account_name": "2110 Accounts Payable - Trade",
    "root_type": "Liability",
    "is_group": 0,
    "parent_account": "2100 Accounts Payable",
    "account_number": "2110"
   },
   {
    "account_name": "2120 Accrued Liabilities",
    "root_type": "Liability",
    "is_group": 0,
    "parent_account": "2100 Accounts Payable",
    "account_number": "2120"
   },
   {
    "account_name": "2200 Tax Payables",
    "root_type": "Liability",
    "is_group": 1,
    "parent_account": "2000 Liabilities"
   },
   {
    "account_name": "2210 VAT/Sales Tax Payable",
    "root_type": "Liability",
    "is_group": 0,
    "parent_account": "2200 Tax Payables",
    "account_number": "2210"
   },
   {
    "account_name": "2220 Income Tax Payable",
    "root_type": "Liability",
    "is_group": 0,
    "parent_account": "2200 Tax Payables",
    "account_number": "2220"
   },
   {
    "account_name": "2230 Payroll Tax Payable",
    "root_type": "Liability",
    "is_group": 0,
    "parent_account": "2200 Tax Payables",
    "account_number": "2230"
   },
   {
    "account_name": "2300 Accrued Expenses",
    "root_type": "Liability",
    "is_group": 1,
    "parent_account": "2000 Liabilities"
   },
   {
    "account_name": "2310 Accrued Salaries",
    "root_type": "Liability",
    "is_group": 0,
    "parent_account": "2300 Accrued Expenses",
    "account_number": "2310"
   },
   {
    "account_name": "2320 Accrued Interest",
    "root_type": "Liability",
    "is_group": 0,
    "parent_account": "2300 Accrued Expenses",
    "account_number": "2320"
   },
   {
    "account_name": "2400 Deferred Revenue",
    "root_type": "Liability",
    "is_group": 1,
    "parent_account": "2000 Liabilities"
   },
   {
    "account_name": "2410 Unearned Revenue",
    "root_type": "Liability",
    "is_group": 0,
    "parent_account": "2400 Deferred Revenue",
    "account_number": "2410"
   },
   {
    "account_name": "2500 Long Term Liabilities",
    "root_type": "Liability",
    "is_group": 1,
    "parent_account": "2000 Liabilities"
   },
   {
    "account_name": "2510 Bank Loans",
    "root_type": "Liability",
    "is_group": 0,
    "parent_account": "2500 Long Term Liabilities",
    "account_number": "2510"
   },
   {
    "account_name": "2520 Notes Payable",
    "root_type": "Liability",
    "is_group": 0,
    "parent_account": "2500 Long Term Liabilities",
    "account_number": "2520"
   },
   {
    "account_name": "2530 Bonds Payable",
    "root_type": "Liability",
    "is_group": 0,
    "parent_account": "2500 Long Term Liabilities",
    "account_number": "2530"
   },
   {
    "account_name": "3000 Equity",
    "root_type": "Equity",
    "is_group": 1
   },
   {
    "account_name": "3100 Common Stock",
    "root_type": "Equity",
    "is_group": 0,
    "parent_account": "3000 Equity",
    "account_number": "3100"
   },
   {
    "account_name": "3200 Additional Paid-in Capital",
    "root_type": "Equity",
    "is_group": 0,
    "parent_account": "3000 Equity",
    "account_number": "3200"
   },
   {
    "account_name": "3300 Retained Earnings",
    "root_type": "Equity",
    "is_group": 0,
    "parent_account": "3000 Equity",
    "account_number": "3300"
   },
   {
    "account_name": "3400 Current Year Earnings",
    "root_type": "Equity",
    "is_group": 0,
    "parent_account": "3000 Equity",
    "account_number": "3400"
   },
   {
    "account_name": "3500 Owner's Draws",
    "root_type": "Equity",
    "is_group": 0,
    "parent_account": "3000 Equity",
    "account_number": "3500"
   },
   {
    "account_name": "4000 Income",
    "root_type": "Income",
    "is_group": 1
   },
   {
    "account_name": "4100 Revenue",
    "root_type": "Income",
    "is_group": 1,
    "parent_account": "4000 Income"
   },
   {
    "account_name": "4110 Product Sales",
    "root_type": "Income",
    "is_group": 0,
    "parent_account": "4100 Revenue",
    "account_number": "4110"
   },
   {
    "account_name": "4120 Service Revenue",
    "root_type": "Income",
    "is_group": 0,
    "parent_account": "4100 Revenue",
    "account_number": "4120"
   },
   {
    "account_name": "4130 Interest Income",
    "root_type": "Income",
    "is_group": 0,
    "parent_account": "4100 Revenue",
    "account_number": "4130"
   },
   {
    "account_name": "4140 Rental Income",
    "root_type": "Income",
    "is_group": 0,
    "parent_account": "4100 Revenue",
    "account_number": "4140"
   },
   {
    "account_name": "4200 Other Income",
    "root_type": "Income",
    "is_group": 1,
    "parent_account": "4000 Income"
   },
   {
    "account_name": "4210 Gain on Sale of Assets",
    "root_type": "Income",
    "is_group": 0,
    "parent_account": "4200 Other Income",
    "account_number": "4210"
   },
   {
    "account_name": "4220 Foreign Exchange Gain",
    "root_type": "Income",
    "is_group": 0,
    "parent_account": "4200 Other Income",
    "account_number": "4220"
   },
   {
    "account_name": "5000 Expenses",
    "root_type": "Expense",
    "is_group": 1
   },
   {
    "account_name": "5100 Cost of Goods Sold",
    "root_type": "Expense",
    "is_group": 1,
    "parent_account": "5000 Expenses"
   },
   {
    "account_name": "5110 COGS - Materials",
    "root_type": "Expense",
    "is_group": 0,
    "parent_account": "5100 Cost of Goods Sold",
    "account_number": "5110"
   },
   {
    "account_name": "5120 COGS - Labor",
    "root_type": "Expense",
    "is_group": 0,
    "parent_account": "5100 Cost of Goods Sold",
    "account_number": "5120"
   },
   {
    "account_name": "5130 COGS - Overhead",
    "root_type": "Expense",
    "is_group": 0,
    "parent_account": "5100 Cost of Goods Sold",
    "account_number": "5130"
   },
   {
    "account_name": "5200 Salaries and Wages",
    "root_type": "Expense",
    "is_group": 0,
    "parent_account": "5000 Expenses",
    "account_number": "5200"
   },
   {
    "account_name": "5300 Rent and Utilities",
    "root_type": "Expense",
    "is_group": 1,
    "parent_account": "5000 Expenses"
   },
   {
    "account_name": "5310 Rent Expense",
    "root_type": "Expense",
    "is_group": 0,
    "parent_account": "5300 Rent and Utilities",
    "account_number": "5310"
   },
   {
    "account_name": "5320 Electricity",
    "root_type": "Expense",
    "is_group": 0,
    "parent_account": "5300 Rent and Utilities",
    "account_number": "5320"
   },
   {
    "account_name": "5330 Water and Gas",
    "root_type": "Expense",
    "is_group": 0,
    "parent_account": "5300 Rent and Utilities",
    "account_number": "5330"
   },
   {
    "account_name": "5340 Internet and Telephone",
    "root_type": "Expense",
    "is_group": 0,
    "parent_account": "5300 Rent and Utilities",
    "account_number": "5340"
   },
   {
    "account_name": "5400 Office and Admin",
    "root_type": "Expense",
    "is_group": 1,
    "parent_account": "5000 Expenses"
   },
   {
    "account_name": "5410 Office Supplies",
    "root_type": "Expense",
    "is_group": 0,
    "parent_account": "5400 Office and Admin",
    "account_number": "5410"
   },
   {
    "account_name": "5420 Insurance",
    "root_type": "Expense",
    "is_group": 0,
    "parent_account": "5400 Office and Admin",
    "account_number": "5420"
   },
   {
    "account_name": "5430 Legal and Professional",
    "root_type": "Expense",
    "is_group": 0,
    "parent_account": "5400 Office and Admin",
    "account_number": "5430"
   },
   {
    "account_name": "5440 Bank Charges",
    "root_type": "Expense",
    "is_group": 0,
    "parent_account": "5400 Office and Admin",
    "account_number": "5440"
   },
   {
    "account_name": "5500 Depreciation and Amortization",
    "root_type": "Expense",
    "is_group": 0,
    "parent_account": "5000 Expenses",
    "account_number": "5500"
   },
   {
    "account_name": "5600 Travel and Entertainment",
    "root_type": "Expense",
    "is_group": 1,
    "parent_account": "5000 Expenses"
   },
   {
    "account_name": "5610 Travel Expense",
    "root_type": "Expense",
    "is_group": 0,
    "parent_account": "5600 Travel and Entertainment",
    "account_number": "5610"
   },
   {
    "account_name": "5620 Meals and Entertainment",
    "root_type": "Expense",
    "is_group": 0,
    "parent_account": "5600 Travel and Entertainment",
    "account_number": "5620"
   },
   {
    "account_name": "5700 Marketing and Advertising",
    "root_type": "Expense",
    "is_group": 0,
    "parent_account": "5000 Expenses",
    "account_number": "5700"
   },
   {
    "account_name": "5800 Taxes and Licenses",
    "root_type": "Expense",
    "is_group": 0,
    "parent_account": "5000 Expenses",
    "account_number": "5800"
   },
   {
    "account_name": "5900 Other Expenses",
    "root_type": "Expense",
    "is_group": 1,
    "parent_account": "5000 Expenses"
   },
   {
    "account_name": "5910 Loss on Asset Disposal",
    "root_type": "Expense",
    "is_group": 0,
    "parent_account": "5900 Other Expenses",
    "account_number": "5910"
   },
   {
    "account_name": "5920 Foreign Exchange Loss",
    "root_type": "Expense",
    "is_group": 0,
    "parent_account": "5900 Other Expenses",
    "account_number": "5920"
   },
   {
    "account_name": "5990 Miscellaneous",
    "root_type": "Expense",
    "is_group": 0,
    "parent_account": "5900 Other Expenses",
    "account_number": "5990"
   }
  ]
 }
}

TEMPLATES_LIST = [
 {
  "key": "GAAP",
  "title": "US GAAP",
  "currency": "USD",
  "vat_rate": 15
 },
 {
  "key": "IFRS",
  "title": "International IFRS",
  "currency": "USD",
  "vat_rate": 15
 },
 {
  "key": "UK",
  "title": "United Kingdom",
  "currency": "GBP",
  "vat_rate": 20
 },
 {
  "key": "SKR03",
  "title": "Germany SKR03",
  "currency": "EUR",
  "vat_rate": 19
 },
 {
  "key": "PCG",
  "title": "France PCG",
  "currency": "EUR",
  "vat_rate": 20
 },
 {
  "key": "KSA",
  "title": "Saudi Arabia (SOCPA)",
  "currency": "SAR",
  "vat_rate": 15
 },
 {
  "key": "NGO",
  "title": "Non-Profit (SFAS 117)",
  "currency": "USD",
  "vat_rate": 0
 },
 {
  "key": "PK",
  "title": "Pakistan",
  "currency": "PKR",
  "vat_rate": 18
 },
 {
  "key": "MY",
  "title": "Malaysia",
  "currency": "MYR",
  "vat_rate": 6
 },
 {
  "key": "UAE",
  "title": "UAE",
  "currency": "AED",
  "vat_rate": 5
 }
]


@frappe.whitelist()
def onboard(template="GAAP"):
    if template not in COA_TEMPLATES:
        frappe.throw(_("Unknown COA template: {0}").format(template))
    config = COA_TEMPLATES[template]

    created = []
    for ac in config["accounts"]:
        existing = frappe.db.exists("Account", {"account_name": ac["account_name"]})
        if existing:
            continue
        doc = frappe.get_doc({
            "doctype": "Account",
            "account_name": ac["account_name"],
            "parent_account": ac.get("parent_account"),
            "root_type": ac["root_type"],
            "is_group": ac.get("is_group", 0),
            "account_number": ac.get("account_number"),
            "account_currency": config["currency"],
            "tax_rate": ac.get("tax_rate", config["vat_rate"]),
        })
        doc.flags.ignore_permissions = True
        doc.insert()
        created.append(ac["account_name"])

    frappe.db.set_value("System Settings", None, "currency", config["currency"])
    frappe.db.set_default("erpmax_coa_template", template)
    frappe.db.set_default("erpmax_currency", config["currency"])
    frappe.db.set_default("erpmax_vat_rate", config["vat_rate"])

    return {"created": created, "template": template, "currency": config["currency"], "total": len(created)}


@frappe.whitelist()
def get_templates():
    return TEMPLATES_LIST


@frappe.whitelist()
def get_chart_of_accounts():
    accounts = frappe.db.get_all(
        "Account",
        fields=["name", "account_name", "account_number", "account_type", "root_type",
                "parent_account", "is_group", "tax_rate", "account_currency"],
        order_by="lft asc",
    )
    tree = _build_tree(accounts)
    return {"flat": accounts, "tree": tree}


def _build_tree(flat):
    by_name = {a["name"]: {**a, "children": []} for a in flat}
    roots = []
    for a in by_name.values():
        parent = a.get("parent_account")
        if parent and parent in by_name:
            by_name[parent]["children"].append(a)
        else:
            roots.append(a)
    return roots
