import frappe
from frappe import _
from frappe.utils import get_link_to_form
from frappe.model.document import Document
from frappe.utils.nestedset import NestedSet


def _make_abbreviation(company_name: str) -> str:
    parts = [part for part in (company_name or "").split() if part]
    abbr = "".join(part[0] for part in parts)
    return abbr[:10].upper()


def _as_text(value) -> str:
    return (value or "").strip() if isinstance(value, str) else value or ""


class Company(NestedSet):
    nsm_parent_field = "parent_company"

    def before_validate(self):
        if self.is_new() and not self.status:
            self.status = "Draft"

        if self.company_name and not self.address_title:
            self.address_title = self.company_name

        if self.company_name and not self.abbreviation:
            self.abbreviation = _make_abbreviation(self.company_name)

        self._apply_feature_tier()

    def validate(self):
        self._apply_country_defaults()
        self._suggest_coa_template()

    def after_insert(self):
        self.create_linked_address()
        self.create_linked_contact()
        if self.create_user and self.owner_email:
            self.create_owner_user()
        self.setup_company_accounts()
    
    def setup_company_accounts(self):
        """Setup all standard accounts for this company"""
        try:
            from erpmax.accounts.doctype.company_account_setup.company_account_setup import setup_company_accounts
            setup_company_accounts(self.name)
        except Exception as e:
            frappe.log_error(f"Failed to setup company accounts: {str(e)}")

    def on_update(self):
        if self.has_value_changed("status") and self.status == "Active":
            self.enable_company_access()

        if self.has_value_changed("linked_user") and self.linked_user:
            self.set_user_permissions()

        if self.has_value_changed("create_user") and self.create_user and self.owner_email:
            self.create_owner_user()

        self._update_linked_user_on_data_change()
        self._handle_coa_creation()

    COA_COUNTRY_MAP = {
        "Saudi Arabia": "KSA",
        "United States": "GAAP",
        "United Kingdom": "UK",
        "Germany": "SKR03",
        "France": "PCG",
        "Pakistan": "PK",
        "Malaysia": "MY",
        "United Arab Emirates": "UAE",
    }
    FALLBACK_COA = "IFRS"

    def _apply_country_defaults(self):
        if not self.country:
            return

        try:
            country = frappe.get_doc("Country", self.country)
        except Exception:
            return

        if not self.country_alpha_2:
            self.country_alpha_2 = _as_text(
                country.get("code") or country.get("alpha_2") or country.get("country_code")
            )

        if not self.country_language:
            self.country_language = _as_text(country.get("language") or country.get("default_language"))

        if not self.default_currency:
            self.default_currency = _as_text(
                country.get("currency") or country.get("currency_code") or country.get("default_currency")
            )

        if not self.date_format:
            self.date_format = _as_text(country.get("date_format"))

        if not self.timezone:
            timezone = country.get("timezone") or country.get("default_timezone")
            if isinstance(timezone, str):
                self.timezone = timezone

    def _suggest_coa_template(self):
        if self.coa_template:
            return
        if self.country in self.COA_COUNTRY_MAP:
            self.coa_template = self.COA_COUNTRY_MAP[self.country]
        if not self.coa_template:
            self.coa_template = self.FALLBACK_COA

    def _handle_coa_creation(self):
        coa_triggered = self.get("__coa_triggered")
        if coa_triggered:
            return
        if not self.has_value_changed("coa_template"):
            return
        if not self.coa_template:
            return
        self.__coa_triggered = True
        self._create_chart_of_accounts()

    def _create_chart_of_accounts(self):
        if not self.coa_template:
            return
        from erpmax.accounting.api.coa import onboard
        onboard(template=self.coa_template)
        self._populate_company_accounts()

    def _populate_company_accounts(self):
        config = frappe.db.get_value("Company", self.name, "coa_template")
        if not config:
            config = self.coa_template
        from erpmax.accounting.api.coa import get_template_config
        tmpl = get_template_config(config)
        if not tmpl:
            return
        currency = tmpl["currency"]
        accounts = frappe.db.sql("""
            SELECT name, account_name, account_currency, root_type
            FROM `tabAccount`
            WHERE account_currency = %s
            ORDER BY name
        """, currency, as_dict=1)
        for ac in accounts:
            existing = frappe.db.get_value("Company Account", {
                "parent": self.name, "account": ac.name
            })
            if existing:
                continue
            ac_type = self._map_root_to_account_type(ac.root_type)
            row = frappe.get_doc({
                "doctype": "Company Account",
                "parent": self.name,
                "parentfield": "company_accounts",
                "parenttype": "Company",
                "account": ac.name,
                "account_name": ac.account_name,
                "account_type": ac_type,
                "is_active": 1,
                "account_currency": ac.account_currency or self.default_currency,
            })
            row.flags.ignore_permissions = True
            row.insert()

    def _map_root_to_account_type(self, root_type):
        mapping = {
            "Asset": "Bank", "Liability": "Payable",
            "Income": "Income", "Expense": "Expense", "Equity": "Equity",
        }
        return mapping.get(root_type, "Other")

    def _update_linked_user_on_data_change(self):
        if not self.linked_user:
            return

        changed = False
        fields_to_update = {}

        first_name = self.owner_first_name or self.company_name

        if self.has_value_changed("owner_first_name") or self.has_value_changed("company_name"):
            fields_to_update["first_name"] = first_name
            changed = True

        if self.has_value_changed("owner_last_name"):
            fields_to_update["last_name"] = self.owner_last_name or ""
            changed = True

        if self.has_value_changed("owner_mobile"):
            fields_to_update["mobile_no"] = self.owner_mobile or ""
            changed = True

        if self.has_value_changed("owner_email") and self.owner_email:
            fields_to_update["email"] = self.owner_email.strip().lower()
            changed = True

        if changed:
            frappe.db.set_value("User", self.linked_user, fields_to_update, update_modified=False)

    def create_linked_address(self):
        if not self.address_line_1:
            return

        # Check if Address doctype exists
        if not frappe.db.table_exists("Address"):
            return

        try:
            existing = frappe.get_all(
                "Address",
                filters={"address_title": self.company_name, "address_type": "Office"},
                limit=1,
            )
            if existing:
                return

            address = frappe.get_doc(
                {
                    "doctype": "Address",
                    "address_title": self.company_name,
                    "address_type": "Office",
                    "address_line1": self.address_line_1 or "",
                    "address_line2": self.address_line_2 or "",
                    "city": self.city or "",
                    "state": self.state or "",
                    "country": self.country or "",
                    "pincode": self.zip_code or "",
                    "email_id": self.contact_email or self.owner_email,
                    "phone": self.contact_phone or "",
                    "links": [{"link_doctype": "Company", "link_name": self.name}],
                }
            )
            address.flags.ignore_permissions = True
            address.flags.ignore_mandatory = True
            address.insert()
            frappe.db.set_value("Company", self.name, "address_created", 1, update_modified=False)
        except Exception:
            frappe.log_error("Failed to create linked address for Company", "Company Address Creation")

    def create_linked_contact(self):
        owner_email = self.owner_email or self.contact_email
        if not owner_email:
            return

        # Check if Contact doctype exists
        if not frappe.db.table_exists("Contact"):
            return

        try:
            existing = frappe.get_all("Contact", filters={"email_id": owner_email}, limit=1)
            if existing:
                return

            contact = frappe.get_doc(
                {
                    "doctype": "Contact",
                    "first_name": self.company_name,
                    "is_primary_contact": 1,
                    "email_ids": [{"email_id": owner_email, "is_primary": 1}],
                    "phone_nos": [{"phone": self.contact_phone or self.owner_mobile or "", "is_primary_phone": 1}],
                    "links": [{"link_doctype": "Company", "link_name": self.name}],
                }
            )
            contact.flags.ignore_permissions = True
            contact.flags.ignore_mandatory = True
            contact.insert()
            frappe.db.set_value("Company", self.name, "contact_created", 1, update_modified=False)
        except Exception:
            frappe.log_error("Failed to create linked contact for Company", "Company Contact Creation")

    def create_owner_user(self):
        email = self.owner_email.strip().lower()
        existing_user = frappe.db.get_value("User", {"email": email})

        if existing_user:
            frappe.db.set_value(
                "Company",
                self.name,
                {"linked_user": existing_user, "user_created": 1},
                update_modified=False,
            )
            self.linked_user = existing_user
            self.set_user_permissions()
            return

        user = frappe.get_doc(
            {
                "doctype": "User",
                "email": email,
                "first_name": self.owner_first_name or self.company_name,
                "last_name": self.owner_last_name or "",
                "mobile_no": self.owner_mobile or "",
                "send_welcome_email": 1,
                "user_type": "Website User",
            }
        )
        user.flags.ignore_permissions = True
        user.insert(ignore_permissions=True)

        if frappe.db.exists("Role", "Company Admin"):
            user.add_roles("Company Admin")

        frappe.db.set_value(
            "Company",
            self.name,
            {"linked_user": user.name, "user_created": 1},
            update_modified=False,
        )
        self.linked_user = user.name
        self.set_user_permissions()

    def set_user_permissions(self):
        if not self.linked_user:
            return

        existing = frappe.get_all(
            "User Permission",
            filters={"user": self.linked_user, "allow": "Company", "for_value": self.name},
            limit=1,
        )
        if existing:
            return

        perm = frappe.get_doc(
            {
                "doctype": "User Permission",
                "user": self.linked_user,
                "allow": "Company",
                "for_value": self.name,
                "is_default": 1,
                "apply_to_all_doctypes": 1,
            }
        )
        perm.flags.ignore_permissions = True
        perm.insert(ignore_permissions=True)

    def enable_company_access(self):
        if self.linked_user:
            self.set_user_permissions()

    def _apply_feature_tier(self):
        tier = self.feature_tier or "Small Company"

        if tier == "Advanced Enterprise":
            self.enable_advanced_features = 1
            self.enable_multi_branch = 1
            self.max_users = self.max_users or 999
            self.max_branches = self.max_branches or 99
        elif tier == "Medium Company":
            self.enable_advanced_features = 0
            self.enable_multi_branch = 1
            self.max_users = self.max_users or 25
            self.max_branches = self.max_branches or 5
        else:
            self.enable_advanced_features = 0
            self.enable_multi_branch = 0
            self.max_users = self.max_users or 5
            self.max_branches = self.max_branches or 1


def get_permission_query_conditions(user=None):
    user = user or frappe.session.user
    if "System Manager" in frappe.get_roles(user):
        return ""

    user_sql = frappe.db.escape(user)
    return f"(`tabCompany`.owner = {user_sql} OR `tabCompany`.linked_user = {user_sql})"


def has_permission(doc, user=None, permission_type=None):
    user = user or frappe.session.user
    if "System Manager" in frappe.get_roles(user):
        return True

    return doc.owner == user or doc.linked_user == user


@frappe.whitelist()
def create_transaction_deletion_request(company):
    frappe.only_for("System Manager")

    from erpmax.utilities.doctype.transaction_deletion_record.transaction_deletion_record import (
        is_deletion_doc_running,
    )

    is_deletion_doc_running(company)

    tdr = frappe.get_doc({"doctype": "Transaction Deletion Record", "company": company})
    tdr.submit()

    frappe.msgprint(
        _(
            "A Transaction Deletion Record: {0} has been triggered for {1}"
        ).format(get_link_to_form("Transaction Deletion Record", tdr.name), frappe.bold(company))
    )


@frappe.whitelist()
def apply_feature_profile(company, feature_tier):
    frappe.only_for("System Manager")

    doc = frappe.get_doc("Company", company)
    doc.feature_tier = feature_tier
    doc._apply_feature_tier()
    doc.save(ignore_permissions=True)
    return doc.as_dict()


@frappe.whitelist()
def get_children(parent=None, company=None, **kwargs):
    root = parent or company or ""
    filters = {"parent_company": root}
    companies = frappe.get_all(
        "Company",
        filters=filters,
        fields=["name", "company_name", "is_group"],
        order_by="company_name asc",
    )
    return [
        {
            "value": row.name,
            "title": row.company_name or row.name,
            "expandable": 1 if row.is_group else 0,
        }
        for row in companies
    ]


@frappe.whitelist()
def add_node(parent=None, label=None, **kwargs):
    label = (label or "").strip()
    if not label:
        frappe.throw(_("Company Name is required"))

    doc = frappe.get_doc(
        {
            "doctype": "Company",
            "company_name": label,
            "abbreviation": _make_abbreviation(label),
            "parent_company": parent or None,
            "is_group": 1,
        }
    )
    doc.insert(ignore_permissions=True)
    return doc.as_dict()
