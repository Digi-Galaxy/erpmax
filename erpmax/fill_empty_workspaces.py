import frappe
import json

def execute():
    print("--- Creating workspace content for empty workspaces ---")
    
    workspace_content = {
        "Business Setup": [
            {"id": "hdr1", "type": "header", "data": {"text": "<span class=\"h4\"><b>Business Configuration</b></span>", "col": 12}},
            {"id": "s1", "type": "shortcut", "data": {"shortcut_name": "Distributor", "col": 3}},
            {"id": "s2", "type": "shortcut", "data": {"shortcut_name": "Distributor Commission", "col": 3}},
            {"id": "s3", "type": "shortcut", "data": {"shortcut_name": "Region", "col": 3}},
            {"id": "s4", "type": "shortcut", "data": {"shortcut_name": "State", "col": 3}},
            {"id": "s5", "type": "shortcut", "data": {"shortcut_name": "City", "col": 3}},
        ],
        "Commerce": [
            {"id": "hdr1", "type": "header", "data": {"text": "<span class=\"h4\"><b>Commerce</b></span>", "col": 12}},
            {"id": "s1", "type": "shortcut", "data": {"shortcut_name": "Customer", "col": 3}},
            {"id": "s2", "type": "shortcut", "data": {"shortcut_name": "Address", "col": 3}},
            {"id": "s3", "type": "shortcut", "data": {"shortcut_name": "Contact", "col": 3}},
            {"id": "s4", "type": "shortcut", "data": {"shortcut_name": "VAT Process", "col": 3}},
        ],
        "ERPMax": [
            {"id": "hdr1", "type": "header", "data": {"text": "<span class=\"h4\"><b>ERPMax</b></span>", "col": 12}},
            {"id": "s1", "type": "shortcut", "data": {"shortcut_name": "Company", "col": 3}},
            {"id": "s2", "type": "shortcut", "data": {"shortcut_name": "Company Industry", "col": 3}},
            {"id": "s3", "type": "shortcut", "data": {"shortcut_name": "Transaction Deletion Record", "col": 3}},
        ],
        "Inventory": [
            {"id": "hdr1", "type": "header", "data": {"text": "<span class=\"h4\"><b>Inventory</b></span>", "col": 12}},
            {"id": "s1", "type": "shortcut", "data": {"shortcut_name": "Item", "col": 3}},
            {"id": "s2", "type": "shortcut", "data": {"shortcut_name": "Item Category", "col": 3}},
            {"id": "s3", "type": "shortcut", "data": {"shortcut_name": "Warehouse", "col": 3}},
            {"id": "s4", "type": "shortcut", "data": {"shortcut_name": "Warehouse Type", "col": 3}},
            {"id": "s5", "type": "shortcut", "data": {"shortcut_name": "UOM", "col": 3}},
        ],
        "Printings": [
            {"id": "hdr1", "type": "header", "data": {"text": "<span class=\"h4\"><b>Printings</b></span>", "col": 12}},
            {"id": "s1", "type": "shortcut", "data": {"shortcut_name": "PDF Settings", "col": 3}},
        ],
        "Purchase": [
            {"id": "hdr1", "type": "header", "data": {"text": "<span class=\"h4\"><b>Purchase</b></span>", "col": 12}},
            {"id": "s1", "type": "shortcut", "data": {"shortcut_name": "Purchase Order", "col": 3}},
            {"id": "s2", "type": "shortcut", "data": {"shortcut_name": "Purchase Receipt", "col": 3}},
            {"id": "s3", "type": "shortcut", "data": {"shortcut_name": "Purchase Invoice", "col": 3}},
            {"id": "s4", "type": "shortcut", "data": {"shortcut_name": "Supplier", "col": 3}},
        ],
        "Taxation & Compliance": [
            {"id": "hdr1", "type": "header", "data": {"text": "<span class=\"h4\"><b>Tax Templates</b></span>", "col": 12}},
            {"id": "s1", "type": "shortcut", "data": {"shortcut_name": "Country Tax Profile", "col": 3}},
            {"id": "s2", "type": "shortcut", "data": {"shortcut_name": "Tax Template", "col": 3}},
            {"id": "s3", "type": "shortcut", "data": {"shortcut_name": "Tax Rate", "col": 3}},
            {"id": "s4", "type": "shortcut", "data": {"shortcut_name": "Tax Category", "col": 3}},
            {"id": "s5", "type": "shortcut", "data": {"shortcut_name": "HS Code", "col": 3}},
            {"id": "hdr6", "type": "header", "data": {"text": "<span class=\"h4\"><b>ZATCA (Saudi Arabia)</b></span>", "col": 12}},
            {"id": "s7", "type": "shortcut", "data": {"shortcut_name": "ZATCA CSR Settings", "col": 3}},
            {"id": "s8", "type": "shortcut", "data": {"shortcut_name": "ZATCA Environment", "col": 3}},
            {"id": "s9", "type": "shortcut", "data": {"shortcut_name": "ZATCA Transactions", "col": 3}},
            {"id": "s10", "type": "shortcut", "data": {"shortcut_name": "ZATCA CSID", "col": 3}},
            {"id": "hdr11", "type": "header", "data": {"text": "<span class=\"h4\"><b>FBR (Pakistan)</b></span>", "col": 12}},
            {"id": "s12", "type": "shortcut", "data": {"shortcut_name": "FBR Settings", "col": 3}},
            {"id": "s13", "type": "shortcut", "data": {"shortcut_name": "FBR Invoice", "col": 3}},
            {"id": "s14", "type": "shortcut", "data": {"shortcut_name": "FBR Sale Type", "col": 3}},
            {"id": "hdr15", "type": "header", "data": {"text": "<span class=\"h4\"><b>Compliance</b></span>", "col": 12}},
            {"id": "s16", "type": "shortcut", "data": {"shortcut_name": "Compliance Log", "col": 3}},
        ],
    }
    
    for ws_name, content_list in workspace_content.items():
        content = json.dumps(content_list)
        frappe.db.sql("UPDATE tabWorkspace SET content=%s WHERE name=%s", (content, ws_name))
        print(f"  {ws_name}: {len(content)} chars")
    
    frappe.db.commit()
    
    # Verify
    print("\n--- Final Verification ---")
    result = frappe.db.sql("SELECT name, LENGTH(content) as content_len FROM tabWorkspace ORDER BY name", as_dict=True)
    for ws in result:
        status = "OK" if ws.content_len > 2 else "EMPTY"
        print(f"  {ws.name}: {ws.content_len} chars | {status}")
    
    print("\nDone!")
