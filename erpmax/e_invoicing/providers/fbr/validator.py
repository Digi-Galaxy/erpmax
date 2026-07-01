class FBRValidator:

    def validate(self, invoice_data):
        errors = []
        warnings = []

        seller = invoice_data.get("seller", {})
        if not seller.get("tax_id"):
            errors.append("Seller NTN/CNIC is required")

        if not seller.get("name"):
            errors.append("Seller business name is required")

        if not seller.get("province"):
            warnings.append("Seller province is not set")

        buyer = invoice_data.get("buyer", {})
        if not buyer.get("name"):
            errors.append("Buyer name is required")

        if not invoice_data.get("posting_date"):
            errors.append("Invoice date is required")

        items = invoice_data.get("items", [])
        if not items:
            errors.append("At least one item line is required")

        for idx, item in enumerate(items, 1):
            if not item.get("hs_code"):
                warnings.append(f"Item {idx}: HS Code is missing")
            if item.get("quantity", 0) <= 0:
                errors.append(f"Item {idx}: Quantity must be greater than zero")
            if item.get("net_amount", 0) <= 0:
                errors.append(f"Item {idx}: Value must be greater than zero")

        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
        }
