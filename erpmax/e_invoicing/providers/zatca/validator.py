class ZATCAValidator:

    def validate(self, invoice_data):
        errors = []
        warnings = []

        seller = invoice_data.get("seller", {})
        if not seller.get("vat_number"):
            errors.append("Seller VAT number is required")

        if not seller.get("name"):
            errors.append("Seller name is required")

        buyer = invoice_data.get("buyer", {})
        if not buyer.get("name"):
            errors.append("Buyer name is required")

        if not invoice_data.get("invoice_number"):
            errors.append("Invoice number is required")

        if not invoice_data.get("issue_date"):
            errors.append("Issue date is required")

        grand_total = invoice_data.get("grand_total", 0)
        if grand_total <= 0:
            errors.append("Grand total must be greater than zero")

        lines = invoice_data.get("lines", [])
        if not lines:
            errors.append("At least one invoice line is required")

        for idx, line in enumerate(lines, 1):
            if not line.get("name"):
                warnings.append(f"Line {idx}: Item name is missing")
            if line.get("quantity", 0) <= 0:
                errors.append(f"Line {idx}: Quantity must be greater than zero")

        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
        }
