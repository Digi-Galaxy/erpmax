"""Auto-detect and reconcile bank transactions"""
import frappe
from frappe import _
from frappe.utils import getdate, add_days, cint, flt
import re
from datetime import datetime


class AutoReconciler:
    """Auto-detect and reconcile bank transactions"""
    
    def __init__(self, bank_account, company=None):
        self.bank_account = bank_account
        self.company = company
        self.match_rules = self._load_match_rules()
    
    def _load_match_rules(self):
        """Load reconciliation rules from database"""
        rules = frappe.get_all(
            "Reconciliation Rule",
            filters={"disabled": 0},
            fields=["name", "match_field", "match_type", "match_value", 
                    "action_type", "action_account", "priority"],
            order_by="priority desc"
        )
        return rules
    
    def auto_reconcile_transaction(self, transaction_name):
        """
        Auto-reconcile a single bank transaction.
        
        Returns:
            dict with reconciliation result
        """
        txn = frappe.get_doc("Bank Transaction", transaction_name)
        
        if txn.status == "Reconciled":
            return {"status": "already_reconciled"}
        
        # Step 1: Try rule-based matching
        rule_match = self._match_by_rules(txn)
        if rule_match:
            return self._apply_rule_match(txn, rule_match)
        
        # Step 2: Try Payment Entry matching
        payment_match = self._match_payment_entry(txn)
        if payment_match:
            return self._apply_payment_match(txn, payment_match)
        
        # Step 3: Try Journal Entry matching
        journal_match = self._match_journal_entry(txn)
        if journal_match:
            return self._apply_journal_match(txn, journal_match)
        
        # Step 4: Try customer/vendor matching
        party_match = self._match_party(txn)
        if party_match:
            return {"status": "party_matched", "party": party_match}
        
        return {"status": "unmatched"}
    
    def _match_by_rules(self, txn):
        """Match transaction using configured rules"""
        for rule in self.match_rules:
            if self._rule_matches(rule, txn):
                return rule
        return None
    
    def _rule_matches(self, rule, txn):
        """Check if a rule matches the transaction"""
        # Get the field value to match against
        if rule.match_field == "Description":
            match_text = txn.description or ""
        elif rule.match_field == "Amount":
            match_text = str(txn.amount)
        elif rule.match_field == "Reference":
            match_text = txn.transaction_id or ""
        elif rule.match_field == "All":
            match_text = f"{txn.description} {txn.amount} {txn.transaction_id}"
        elif rule.match_field == "IBAN":
            # Extract IBAN from description
            import re
            iban_pattern = r'\b[A-Z]{2}\d{2}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{0,4}\b'
            ibans = re.findall(iban_pattern, (txn.description or "").upper())
            match_text = ibans[0] if ibans else ""
        elif rule.match_field == "Account Number":
            # Extract account number from description
            import re
            acc_pattern = r'\b\d{8,18}\b'
            accounts = re.findall(acc_pattern, txn.description or "")
            match_text = accounts[0] if accounts else ""
        elif rule.match_field == "SWIFT Code":
            # Extract SWIFT from description
            import re
            swift_pattern = r'\b[A-Z]{6}[A-Z2-9][A-NP-Z0-9]([A-Z0-9]{3})?\b'
            swifts = re.findall(swift_pattern, (txn.description or "").upper())
            match_text = swifts[0] if swifts else ""
        elif rule.match_field == "Bank Name":
            # Try to extract bank name from description
            match_text = txn.description or ""
        elif rule.match_field == "Party Name":
            # Try to match party name from description
            match_text = txn.description or ""
        else:
            return False
        
        # Apply match type
        if rule.match_type == "Contains":
            return rule.match_value.lower() in match_text.lower()
        elif rule.match_type == "Starts With":
            return match_text.lower().startswith(rule.match_value.lower())
        elif rule.match_type == "Ends With":
            return match_text.lower().endswith(rule.match_value.lower())
        elif rule.match_type == "Exact":
            return match_text.lower() == rule.match_value.lower()
        elif rule.match_type == "Regex":
            try:
                return bool(re.search(rule.match_value, match_text, re.IGNORECASE))
            except re.error:
                return False
        
        return False
    
    def _apply_rule_match(self, txn, rule):
        """Apply rule-based match"""
        if rule.action_type == "Payment Entry":
            # Create or link Payment Entry
            return {"status": "rule_matched", "action": "payment_entry", "rule": rule.name}
        elif rule.action_type == "Journal Entry":
            return {"status": "rule_matched", "action": "journal_entry", "rule": rule.name}
        elif rule.action_type == "Bank Entry":
            return {"status": "rule_matched", "action": "bank_entry", "rule": rule.name}
        
        return {"status": "rule_matched", "action": "none"}
    
    def _match_payment_entry(self, txn):
        """Match transaction to existing Payment Entry"""
        from frappe.utils import add_days
        
        # Calculate date range (7 days tolerance)
        start_date = add_days(txn.posting_date, -7)
        end_date = add_days(txn.posting_date, 7)
        
        # Calculate amount range (5% tolerance)
        amount_tolerance = txn.amount * 0.05
        min_amount = txn.amount - amount_tolerance
        max_amount = txn.amount + amount_tolerance
        
        # Determine party type based on transaction type
        party_type = "Customer" if txn.transaction_type == "Credit" else "Supplier"
        
        # Search for matching payments
        filters = {
            "docstatus": 1,
            "posting_date": ["between", [start_date, end_date]],
            "paid_amount": ["between", [min_amount, max_amount]],
            "party_type": party_type,
        }
        
        if self.company:
            filters["company"] = self.company
        
        payments = frappe.get_all(
            "Payment Entry",
            filters=filters,
            fields=["name", "party", "paid_amount", "posting_date"],
            order_by="abs(paid_amount - {0}) asc".format(txn.amount)
        )
        
        if payments:
            return payments[0]
        
        return None
    
    def _apply_payment_match(self, txn, payment):
        """Apply Payment Entry match"""
        frappe.db.set_value("Bank Transaction", txn.name, {
            "payment_entry": payment.name,
            "voucher_type": "Payment Entry",
            "voucher_no": payment.name,
            "status": "Reconciled",
            "reconciled_date": getdate(nowdate())
        })
        
        # Update Payment Entry cleared date
        frappe.db.set_value("Payment Entry", payment.name, "cleared_date", txn.posting_date)
        
        return {"status": "reconciled", "payment_entry": payment.name}
    
    def _match_journal_entry(self, txn):
        """Match transaction to existing Journal Entry"""
        from frappe.utils import add_days
        
        start_date = add_days(txn.posting_date, -7)
        end_date = add_days(txn.posting_date, 7)
        
        amount_tolerance = txn.amount * 0.05
        min_amount = txn.amount - amount_tolerance
        max_amount = txn.amount + amount_tolerance
        
        filters = {
            "docstatus": 1,
            "posting_date": ["between", [start_date, end_date]],
        }
        
        if self.company:
            filters["company"] = self.company
        
        journals = frappe.get_all(
            "Journal Entry",
            filters=filters,
            fields=["name", "total_debit", "total_credit", "posting_date"]
        )
        
        for je in journals:
            if abs(je.total_debit - txn.amount) <= amount_tolerance or \
               abs(je.total_credit - txn.amount) <= amount_tolerance:
                return je
        
        return None
    
    def _apply_journal_match(self, txn, journal):
        """Apply Journal Entry match"""
        frappe.db.set_value("Bank Transaction", txn.name, {
            "journal_entry": journal.name,
            "voucher_type": "Journal Entry",
            "voucher_no": journal.name,
            "status": "Reconciled",
            "reconciled_date": getdate(nowdate())
        })
        
        return {"status": "reconciled", "journal_entry": journal.name}
    
    def _match_party(self, txn):
        """Match transaction to customer/vendor by name"""
        from erpmax.utils.fuzzy_matching import fuzzy_match_customer, fuzzy_match_vendor
        
        if txn.transaction_type == "Credit":
            match = fuzzy_match_customer(txn.description, self.company)
            if match:
                return {"type": "Customer", "name": match["customer"], "score": match["score"]}
        else:
            match = fuzzy_match_vendor(txn.description, self.company)
            if match:
                return {"type": "Supplier", "name": match["supplier"], "score": match["score"]}
        
        return None
    
    def batch_auto_reconcile(self, bank_statement_name):
        """
        Auto-reconcile all transactions in a bank statement.
        
        Returns:
            dict with reconciliation summary
        """
        statement = frappe.get_doc("Bank Statement", bank_statement_name)
        
        results = {
            "total": 0,
            "reconciled": 0,
            "unmatched": 0,
            "details": []
        }
        
        for line in statement.lines:
            results["total"] += 1
            
            # Create or find Bank Transaction for this line
            txn_name = self._get_or_create_transaction(line, statement)
            
            if txn_name:
                result = self.auto_reconcile_transaction(txn_name)
                result["line_idx"] = line.idx
                result["description"] = line.description
                result["amount"] = line.amount
                
                if result["status"] == "reconciled":
                    results["reconciled"] += 1
                else:
                    results["unmatched"] += 1
                
                results["details"].append(result)
        
        return results
    
    def _get_or_create_transaction(self, line, statement):
        """Get or create Bank Transaction for a statement line"""
        # Check if transaction already exists
        existing = frappe.db.get_value(
            "Bank Transaction",
            {
                "bank_account": self.bank_account,
                "posting_date": line.date,
                "amount": line.amount,
                "description": line.description
            },
            "name"
        )
        
        if existing:
            return existing
        
        # Create new transaction
        txn = frappe.get_doc({
            "doctype": "Bank Transaction",
            "bank_account": self.bank_account,
            "posting_date": line.date,
            "company": statement.company,
            "description": line.description,
            "transaction_type": line.transaction_type,
            "amount": line.amount,
            "status": "Pending"
        })
        
        txn.insert(ignore_permissions=True)
        return txn.name


@frappe.whitelist()
def auto_reconcile_statement(bank_statement_name):
    """API endpoint to auto-reconcile a bank statement"""
    statement = frappe.get_doc("Bank Statement", bank_statement_name)
    reconciler = AutoReconciler(statement.bank_account, statement.company)
    return reconciler.batch_auto_reconcile(bank_statement_name)


@frappe.whitelist()
def auto_reconcile_single(transaction_name):
    """API endpoint to auto-reconcile a single transaction"""
    txn = frappe.get_doc("Bank Transaction", transaction_name)
    reconciler = AutoReconciler(txn.bank_account, txn.company)
    return reconciler.auto_reconcile_transaction(transaction_name)


def nowdate():
    """Get current date"""
    return getdate()
