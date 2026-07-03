import frappe
import json
import os
import shutil

def execute():
    base = os.path.expanduser("~/frappe-bench/apps/erpmax")
    
    # 1. Delete workspace files in wrong locations
    print("--- 1. Deleting wrong workspace files ---")
    wrong_dirs = []
    for root, dirs, files in os.walk(os.path.join(base, "erpmax")):
        if "workspace" in root and "erpmax/workspace" not in root:
            for f in files:
                if f.endswith('.json'):
                    filepath = os.path.join(root, f)
                    os.remove(filepath)
                    wrong_dirs.append(filepath)
    
    # Remove empty workspace directories
    for root, dirs, files in os.walk(os.path.join(base, "erpmax"), topdown=False):
        if "workspace" in root and "erpmax/workspace" not in root:
            if not os.listdir(root):
                os.rmdir(root)
    
    print(f"  Deleted {len(wrong_dirs)} wrong workspace files")
    
    # 2. Update DB from correct files in erpmax/erpmax/workspace/
    print("\n--- 2. Updating DB from correct workspace files ---")
    ws_dir = os.path.join(base, "erpmax/erpmax/workspace")
    
    for module_dir in os.listdir(ws_dir):
        module_path = os.path.join(ws_dir, module_dir)
        if not os.path.isdir(module_path):
            continue
        
        for ws_file in os.listdir(module_path):
            if not ws_file.endswith('.json'):
                continue
            
            filepath = os.path.join(module_path, ws_file)
            
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
                frappe.db.sql("UPDATE tabWorkspace SET content=%s WHERE name=%s", (content, ws_name))
                
                # Update links
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
    
    # 3. Create missing workspaces for new modules
    print("\n--- 3. Creating workspaces for new modules ---")
    new_workspaces = {
        "Inventory": {"module": "Inventory", "icon": "box", "content": "[]"},
        "Commerce": {"module": "Commerce", "icon": "store", "content": "[]"},
        "Taxation & Compliance": {"module": "Taxation", "icon": "shield-check", "content": "[]"},
        "Printings": {"module": "Printings", "icon": "print", "content": "[]"},
    }
    
    for ws_name, config in new_workspaces.items():
        if not frappe.db.exists("Workspace", ws_name):
            frappe.db.sql("""
                INSERT INTO tabWorkspace 
                (name, label, title, module, icon, is_hidden, public, content, sequence_id, creation, modified, modified_by, owner, docstatus)
                VALUES (%s, %s, %s, %s, %s, 0, 1, %s, 100, NOW(), NOW(), 'Administrator', 'Administrator', 0)
            """, (ws_name, ws_name, ws_name, config["module"], config["icon"], config["content"]))
            print(f"  Created: {ws_name}")
        else:
            frappe.db.sql("UPDATE tabWorkspace SET public=1, is_hidden=0 WHERE name=%s", (ws_name,))
    
    frappe.db.commit()
    
    # 4. Final verification
    print("\n--- 4. Final Verification ---")
    result = frappe.db.sql("SELECT name, module, LENGTH(content) as content_len FROM tabWorkspace ORDER BY name", as_dict=True)
    for ws in result:
        status = "OK" if ws.content_len > 2 else "EMPTY"
        print(f"  {ws.name} | {ws.module} | {ws.content_len} chars | {status}")
    
    print("\nDone!")
