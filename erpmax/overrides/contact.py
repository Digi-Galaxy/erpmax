import frappe
from frappe.contacts.doctype.contact.contact import Contact as CoreContact

class CustomContact(CoreContact):
    def validate(self):
        super().validate()

def create_contact_from_party(doc, method=None):
    email = doc.get("contact_email") or doc.get("email_id")
    if not email:
        return
    if frappe.db.exists("Contact", {"email_id": email}):
        return
    try:
        contact = frappe.get_doc({
            "doctype": "Contact",
            "first_name": doc.get("customer_name") or doc.get("supplier_name") or doc.get("company_name") or doc.name,
            "email_id": email,
            "mobile_no": doc.get("contact_mobile") or doc.get("mobile_no"),
            "is_primary_contact": 1,
            "links": [{"link_doctype": doc.doctype, "link_name": doc.name}]
        })
        contact.flags.ignore_mandatory = True
        contact.insert(ignore_permissions=True, ignore_links=True)
    except Exception as e:
        frappe.log_error("create_contact_from_party {} {}: {}".format(doc.doctype, doc.name, e), "Contact Error")
