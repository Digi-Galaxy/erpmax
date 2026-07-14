import frappe
from frappe.contacts.doctype.address.address import Address as CoreAddress


class CustomAddress(CoreAddress):
    def get_display(self):
        if self.country == "Saudi Arabia":
            parts = []
            if self.building_no or self.street_name:
                parts.append(" ".join(filter(None, [self.building_no, self.street_name])))
            if self.district:
                parts.append(self.district)
            city_line = " ".join(filter(None, [self.city, self.zip_code]))
            if city_line:
                parts.append(city_line)
            if self.additional_no:
                parts.append(self.additional_no)
            if self.country:
                parts.append(self.country)
            return "\n".join(parts) if parts else super().get_display()
        return super().get_display()


def create_linked_address(doc):
    if not doc.get("address_line_1") or doc.get("address_created"):
        return
    try:
        addr = frappe.get_doc({
            "doctype": "Address",
            "address_title": doc.get("company_name") or doc.get("customer_name") or doc.get("supplier_name") or doc.get("staff_name") or doc.get("branch_name") or doc.get("bank_name") or doc.name,
            "address_line_1": doc.address_line_1,
            "address_line_2": doc.get("address_line_2"),
            "city": doc.get("city"),
            "state": doc.get("state"),
            "country": doc.get("country"),
            "pincode": doc.get("zip_code"),
            "email_id": doc.get("contact_email"),
            "phone": doc.get("contact_phone"),
            "is_primary_address": 1,
            "links": [{"link_doctype": doc.doctype, "link_name": doc.name}]
        })
        addr.flags.ignore_mandatory = True
        addr.insert(ignore_permissions=True, ignore_links=True)
        frappe.db.set_value(doc.doctype, doc.name, "address_created", 1)
        doc.address_created = 1
        frappe.db.commit()
        return addr.name
    except Exception as e:
        frappe.log_error("create_linked_address {} {}: {}".format(doc.doctype, doc.name, e), "Address Error")


def create_linked_contact(doc):
    email = doc.get("owner_email") or doc.get("contact_email")
    if not email or doc.get("contact_created"):
        return
    try:
        contact = frappe.get_doc({
            "doctype": "Contact",
            "first_name": doc.get("company_name") or doc.get("customer_name") or doc.get("supplier_name") or doc.get("staff_name") or doc.get("branch_name") or doc.get("bank_name") or doc.name,
            "email_id": email,
            "mobile_no": doc.get("contact_mobile"),
            "is_primary_contact": 1,
            "links": [{"link_doctype": doc.doctype, "link_name": doc.name}]
        })
        contact.flags.ignore_mandatory = True
        contact.insert(ignore_permissions=True, ignore_links=True)
        frappe.db.set_value(doc.doctype, doc.name, "contact_created", 1)
        doc.contact_created = 1
        frappe.db.commit()
        return contact.name
    except Exception as e:
        frappe.log_error("create_linked_contact {} {}: {}".format(doc.doctype, doc.name, e), "Contact Error")


def create_owner_user(doc):
    if not doc.get("create_user") or not doc.get("owner_email") or doc.get("user_created"):
        return
    email = doc.owner_email.strip().lower()
    existing = frappe.db.get_value("User", {"email": email})
    if existing:
        frappe.db.set_value(doc.doctype, doc.name, {"linked_user": existing, "user_created": 1})
        doc.user_created = 1
        frappe.db.commit()
        _set_permissions(doc, existing)
        return existing
    try:
        user = frappe.get_doc({
            "doctype": "User",
            "email": email,
            "first_name": doc.get("owner_first_name") or doc.get("company_name") or doc.name,
            "last_name": doc.get("owner_last_name"),
            "mobile_no": doc.get("owner_mobile"),
            "send_welcome_email": False,
            "roles": [{"role": "System Manager"}]
        })
        user.flags.ignore_mandatory = True
        user.insert(ignore_permissions=True)
        frappe.db.set_value(doc.doctype, doc.name, {"linked_user": user.name, "user_created": 1})
        doc.user_created = 1
        frappe.db.commit()
        _set_permissions(doc, user.name)
        return user.name
    except Exception as e:
        frappe.log_error("create_owner_user {} {}: {}".format(doc.doctype, doc.name, e), "User Error")


def _set_permissions(doc, user):
    if not user:
        return
    try:
        has_default = frappe.db.exists("User Permission", {"user": user, "allow": doc.doctype, "is_default": 1})
        perm = frappe.get_doc({
            "doctype": "User Permission",
            "user": user,
            "allow": doc.doctype,
            "for_value": doc.name,
            "is_default": 0 if has_default else 1
        })
        perm.insert(ignore_permissions=True)
    except Exception as e:
        frappe.log_error("_set_permissions {} {}: {}".format(doc.doctype, doc.name, e), "Permission Error")


def after_insert(doc, method=None):
    for fn in [create_linked_address, create_linked_contact, create_owner_user]:
        try:
            fn(doc)
        except Exception as e:
            frappe.log_error("after_insert {} {}: {}".format(doc.doctype, doc.name, e), "after_insert Error")


def on_update(doc, method=None):
    if doc.has_value_changed("address_line_1") and not doc.get("address_created"):
        create_linked_address(doc)
    if doc.has_value_changed("contact_email") and not doc.get("contact_created"):
        create_linked_contact(doc)
    if doc.has_value_changed("create_user") and doc.get("create_user") and doc.get("owner_email") and not doc.get("user_created"):
        create_owner_user(doc)
