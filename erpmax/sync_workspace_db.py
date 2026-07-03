import frappe
import json
import os

def execute():
    base = os.path.expanduser("~/frappe-bench/apps/erpmax")
    
    print("--- Updating workspace content from JSON files ---")
    
    # Find all workspace JSON files
    for root, dirs, files in os.walk(base):
        for f in files:
            if not f.endswith('.json') or 'workspace' not in root:
                continue
            
            filepath = os.path.join(root, f)
            
            try:
                with open(filepath) as fh:
                    data = json.load(fh)
                
                if data.get("doctype") != "Workspace":
                    continue
                
                ws_name = data.get("name") or data.get("label")
                content = data.get("content", "[]")
                links = data.get("links", [])
                
                if not ws_name:
                    continue
                
                # Update content field
                frappe.db.set_value("Workspace", ws_name, "content", content)
                
                # Update links table
                frappe.db.sql("DELETE FROM `tabWorkspace Link` WHERE parent=%s", (ws_name,))
                
                for idx, link in enumerate(links):
                    frappe.db.sql("""
                        INSERT INTO `tabWorkspace Link` 
                        (name, parent, parentfield, parenttype, type, link_to, label, link_type, hidden, onboard, is_query_report, link_count, idx, docstatus, creation, modified, modified_by, owner)
                        VALUES (%s, %s, 'links', 'Workspace', %s, %s, %s, %s, %s, %s, %s, %s, %s, 0, NOW(), NOW(), 'Administrator', 'Administrator')
                    """, (
                        f"WSL-{ws_name}-{idx}",
                        ws_name,
                        link.get("type", "Link"),
                        link.get("link_to", ""),
                        link.get("label", ""),
                        link.get("link_type", "DocType"),
                        link.get("hidden", 0),
                        link.get("onboard", 0),
                        link.get("is_query_report", 0),
                        link.get("link_count", 0),
                        idx + 1,
                    ))
                
                print(f"  {ws_name}: content={len(content)} chars, links={len(links)}")
                
            except Exception as e:
                print(f"  Error: {filepath}: {e}")
    
    frappe.db.commit()
    
    # Verify
    print("\n--- Verification ---")
    ws_list = frappe.get_all("Workspace", fields=["name"], limit_page_length=0)
    for ws in ws_list:
        content_len = len(frappe.db.get_value("Workspace", ws.name, "content") or "")
        link_count = frappe.db.sql("SELECT COUNT(*) FROM `tabWorkspace Link` WHERE parent=%s", (ws.name,), as_dict=True)[0]["COUNT(*)"]
        print(f"  {ws.name}: content={content_len} chars, links={link_count}")
    
    print("\nDone!")
