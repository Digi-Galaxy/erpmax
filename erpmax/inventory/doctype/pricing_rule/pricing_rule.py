import frappe
from frappe.model.document import Document
from frappe.utils import getdate, nowdate


class PricingRule(Document):
    def validate(self):
        self.validate_rule()
        self.validate_date_range()

    def validate_rule(self):
        if not self.price_list:
            frappe.throw("Price List is required")
        if not self.rule_type:
            frappe.throw("Rule Type is required")

    def validate_date_range(self):
        if self.valid_from and self.valid_upto:
            if getdate(self.valid_upto) < getdate(self.valid_from):
                frappe.throw("Valid Upto cannot be before Valid From")

    @frappe.whitelist()
    def apply_rule(self, item_code, qty=1, date=None):
        """Apply pricing rule to get adjusted price"""
        if not date:
            date = frappe.utils.nowdate()

        # Check if rule is active
        if self.valid_from and getdate(date) < getdate(self.valid_from):
            return None

        if self.valid_upto and getdate(date) > getdate(self.valid_upto):
            return None

        # Get base price
        base_price = frappe.db.get_value("Item Price", {
            "item_code": item_code,
            "price_list": self.price_list,
        }, "price_list_rate") or 0

        if not base_price:
            return None

        # Apply discount
        if self.discount_type == "Percentage" and self.discount_percentage:
            adjusted_price = base_price - (base_price * self.discount_percentage / 100)
        elif self.discount_type == "Amount" and self.discount_amount:
            adjusted_price = base_price - self.discount_amount
        else:
            adjusted_price = base_price

        # Apply quantity discount
        if self.qty_based and self.min_qty and qty >= self.min_qty:
            if self.qty_discount_type == "Percentage":
                adjusted_price = adjusted_price - (adjusted_price * self.qty_discount / 100)
            elif self.qty_discount_type == "Amount":
                adjusted_price = adjusted_price - self.qty_discount

        return max(adjusted_price, 0)

    @frappe.whitelist()
    def test_rule(self, item_code, qty=1, amount=100):
        """Test pricing rule with sample data"""
        adjusted = self.apply_rule(item_code, qty)
        if adjusted:
            discount = amount - adjusted
            return {
                "original": amount,
                "adjusted": adjusted,
                "discount": discount,
                "discount_percent": (discount / amount * 100) if amount > 0 else 0,
            }
        return {"original": amount, "adjusted": amount, "discount": 0}
