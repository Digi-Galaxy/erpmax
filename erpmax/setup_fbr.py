import frappe

def seed():
    # 1. Company
    if not frappe.db.exists("Company", "GLPK"):
        c = frappe.new_doc("Company")
        c.company_name = "Galaxy Labs PK"
        c.abbreviation = "GLPK"
        c.country = "Pakistan"
        c.default_currency = "PKR"
        c.ntn = "1234567-8"
        c.strn = "1234567890123"
        c.fbr_province = "Sindh"
        c.fbr_mode = "Sandbox Testing"
        c.insert()
        frappe.db.commit()
        print("1. Company created")

    # 2. PK Country Profile
    if not frappe.db.exists("EH Country Profile", "PK"):
        p = frappe.new_doc("EH Country Profile")
        p.country_code = "PK"
        p.country_name = "Pakistan"
        p.provider_type = "FBR"
        p.xml_format = "JSON"
        p.signing_algorithm = "RSA-SHA256"
        p.qr_encoding = "Base64"
        p.api_base_url_sandbox = "https://gw.fbr.gov.pk/di_data/v1/di/postinvoicedata_sb"
        p.api_base_url_production = "https://gw.fbr.gov.pk/di_data/v1/di/postinvoicedata"
        p.vat_rate = 0
        p.invoice_retention_years = 5
        p.is_default = 1
        p.insert()
        frappe.db.commit()
        print("2. PK profile created")
    else:
        p = frappe.get_doc("EH Country Profile", "PK")
        p.is_default = 1
        p.save()
        frappe.db.commit()
        print("2. PK profile updated")

    # 3. EH Provider Config
    if not frappe.db.exists("EH Provider Config", "GLPK-FBR"):
        cfg = frappe.new_doc("EH Provider Config")
        cfg.company = "Galaxy Labs PK"
        cfg.country_profile = "PK"
        cfg.environment = "Sandbox"
        cfg.api_base_url_sandbox = "https://gw.fbr.gov.pk/di_data/v1/di/postinvoicedata_sb"
        cfg.api_base_url_production = "https://gw.fbr.gov.pk/di_data/v1/di/postinvoicedata"
        cfg.api_secret = ""
        cfg.is_active = 0
        cfg.insert()
        frappe.db.commit()
        print("3. Provider Config created (inactive - add token)")

    # 4. FBR Sale Types
    scenarios = [
        ("SN001", "Standard Goods", "sn001"),
        ("SN002", "Standard Services", "sn002"),
        ("SN005", "Reduced Rate Goods", "sn005"),
        ("SN008", "Third Schedule Goods", "sn008"),
        ("SN026", "Standard Goods B2C", "sn026"),
        ("SN027", "Third Schedule B2C", "sn027"),
        ("SN028", "Reduced Rate B2C", "sn028"),
    ]
    for sid, desc, _ in scenarios:
        if not frappe.db.exists("FBR Sale Type", sid):
            st = frappe.new_doc("FBR Sale Type")
            st.sale_type = sid
            st.scenario_id = sid
            st.description = desc
            st.insert()
    frappe.db.commit()
    print(f"4. {len(scenarios)} FBR Sale Types created")

    # 5. HS Codes
    codes = [("847130", "Portable computers"), ("620462", "Cotton garments"), ("100630", "Semi-milled rice"), ("271012", "Motor gasoline")]
    for code, desc in codes:
        if not frappe.db.exists("HS Code", code):
            h = frappe.new_doc("HS Code")
            h.hs_code = code
            h.description = desc
            h.insert()
    frappe.db.commit()
    print(f"5. {len(codes)} HS Codes created")

    # 6. Customers
    if not frappe.db.exists("Customer", "Ali Traders"):
        c1 = frappe.new_doc("Customer")
        c1.customer_name = "Ali Traders"
        c1.customer_type = "Company"
        c1.country = "Pakistan"
        c1.ntn = "7654321-1"
        c1.strn = "9876543210987"
        c1.insert()
        frappe.db.commit()
        print("6a. Customer: Ali Traders")

    if not frappe.db.exists("Customer", "Ahmed Khan"):
        c2 = frappe.new_doc("Customer")
        c2.customer_name = "Ahmed Khan"
        c2.customer_type = "Individual"
        c2.country = "Pakistan"
        c2.cnic = "42201-1234567-1"
        c2.insert()
        frappe.db.commit()
        print("6b. Customer: Ahmed Khan")

    # 7. Items
    items = [("Laptop Pro", "847130", "SN001"), ("Office Chair", "620462", "SN001"), ("Basmati Rice 5kg", "100630", "SN008")]
    for name, hsc, st in items:
        if not frappe.db.exists("Item", name):
            i = frappe.new_doc("Item")
            i.item_code = name
            i.item_name = name
            i.hs_code = hsc
            i.fbr_sale_type = st
            i.insert()
    frappe.db.commit()
    print(f"7. {len(items)} Items created")

    print("\n=== SEED COMPLETE ===")
    print("ERPNext site: https://erpmax.celtcoksa.com")
    print("Go to EH Provider Config > GLPK-FBR to add your FBR sandbox token")

seed()
