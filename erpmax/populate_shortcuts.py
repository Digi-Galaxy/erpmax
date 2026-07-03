import frappe
import json

def execute():
    print("--- Populating workspace shortcuts from content ---")
    
    workspaces = frappe.get_all("Workspace", fields=["name", "content"], limit_page_length=0)
    
    total = 0
    for ws in workspaces:
        if not ws.content or ws.content == "[]":
            continue
        
        try:
            content = json.loads(ws.content)
        except:
            continue
        
        # Extract shortcuts from content
        shortcuts = []
        for item in content:
            if item.get("type") == "shortcut":
                shortcut_name = item.get("data", {}).get("shortcut_name")
                if shortcut_name:
                    shortcuts.append(shortcut_name)
        
        if not shortcuts:
            continue
        
        # Clear existing shortcuts
        frappe.db.sql("DELETE FROM `tabWorkspace Shortcut` WHERE parent=%s", (ws.name,))
        
        # Add shortcuts
        for idx, shortcut_name in enumerate(shortcuts):
            # Check if it's a DocType
            doc_type = frappe.db.get_value("DocType", shortcut_name, "name")
            if doc_type:
                frappe.db.sql("""
                    INSERT INTO `tabWorkspace Shortcut` 
                    (name, parent, parentfield, parenttype, type, link_to, label, icon, idx, docstatus, creation, modified, modified_by, owner)
                    VALUES (%s, %s, 'shortcuts', 'Workspace', 'DocType', %s, %s, 'icon', %s, 0, NOW(), NOW(), 'Administrator', 'Administrator')
                """, (f"WSS-{ws.name}-{idx}", ws.name, shortcut_name, shortcut_name, idx + 1))
                total += 1
        
        print(f"  {ws.name}: {len(shortcuts)} shortcuts")
    
    frappe.db.commit()
    print(f"\nTotal shortcuts created: {total}")
    print("\nDone!")
