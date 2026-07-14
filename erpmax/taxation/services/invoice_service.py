import frappe
from ..providers import get_provider_for_country


class InvoiceService:

    def _get_invoice_currency(self, si, company):
        return si.get('currency') or company.get('default_currency') or 'PKR'

    def _get_invoice_tax_total(self, si):
        return si.get('tax_total') or si.get('total_tax') or 0

    def create_compliance_invoice(self, sales_invoice):
        si = frappe.get_doc('Sales Invoice', sales_invoice)
        company = frappe.get_doc('Company', si.company)

        profile = frappe.db.get_value('Tax Country Profile',
            {'country': frappe.db.get_value('Company', si.company, 'country')}, '*')
        if not profile:
            frappe.throw('No Tax Country Profile found for company country')

        provider = get_provider_for_country(profile.country_code)
        invoice_data = self._prepare_data(si, company, profile)
        validation = provider.validate(invoice_data)

        ci = frappe.get_doc({
            'doctype': 'Tax Compliance Invoice',
            'provider': profile.name,
            'status': 'Draft',
            'erpnext_invoice_type': 'Sales Invoice',
            'erpnext_invoice': si.name,
            'company': si.company,
            'customer': si.customer,
            'posting_date': si.posting_date,
            'currency': self._get_invoice_currency(si, company),
            'grand_total': si.grand_total,
            'total_vat': self._get_invoice_tax_total(si),
        })

        if not validation['valid']:
            ci.status = 'Failed'
            ci.validation_results = '\n'.join(validation['errors'])
            ci.has_warnings = True
            ci.insert()
            return ci

        if validation.get('warnings'):
            ci.has_warnings = True

        xml_content = provider.generate_xml(invoice_data)
        ci.xml_content = xml_content
        ci.status = 'Validated'
        ci.insert()
        return ci

    def _get_seller_address(self, company):
        addr = frappe.db.get_value('Address',
            {'dynamic_link_doctype': 'Company', 'dynamic_link_name': company.name, 'is_primary_address': 1},
            ['address_line1', 'address_line2', 'city', 'state', 'pincode'], as_dict=True)
        if addr:
            parts = [addr.get('address_line1',''), addr.get('address_line2',''), addr.get('city',''), addr.get('state','')]
            return ', '.join(p for p in parts if p)
        return ''

    def _get_buyer_address(self, customer):
        addr = frappe.db.get_value('Address',
            {'dynamic_link_doctype': 'Customer', 'dynamic_link_name': customer.name, 'is_primary_address': 1},
            ['address_line1', 'address_line2', 'city', 'state', 'pincode'], as_dict=True)
        if addr:
            parts = [addr.get('address_line1',''), addr.get('address_line2',''), addr.get('city',''), addr.get('state','')]
            return ', '.join(p for p in parts if p)
        return ''

    def _get_item_hs_code(self, item_code):
        if not item_code:
            return ''
        return frappe.db.get_value('Item', item_code, 'hs_code') or ''

    def _get_item_uom(self, item_code):
        if not item_code:
            return 'Nos'
        return frappe.db.get_value('Item', item_code, 'stock_uom') or 'Nos'

    def _get_item_tax_rate(self, item, tax_rate):
        return item.get('tax_rate') or tax_rate or 0

    def _get_item_sale_type(self, item, tax_rate):
        sale_type = item.get('sale_type') or item.get('fbr_sale_type') or ''
        if sale_type:
            return sale_type
        if tax_rate:
            return 'Goods at standard rate (default)'
        return 'Goods at standard rate (default)'

    def _get_item_amount(self, item):
        return item.get('net_amount') or item.get('amount') or 0

    def _prepare_data(self, si, company, profile):
        customer = frappe.get_doc('Customer', si.customer)
        tax_rate = 0
        if si.taxes:
            tax_rate = si.taxes[0].get('rate', 0)
        tax_total = self._get_invoice_tax_total(si)
        currency = self._get_invoice_currency(si, company)

        lines = []
        for item in si.items:
            item_code = item.get('item_code') or item.get('item_name', '')
            hs_code = self._get_item_hs_code(item_code)
            uom = self._get_item_uom(item_code)
            is_fbr = profile.get('provider') == 'FBR'
            sale_type = ''
            if is_fbr:
                hs_code = item.get('hs_code') or hs_code
                uom = item.get('uom') or uom
                sale_type = self._get_item_sale_type(item, tax_rate)
            item_tax_rate = self._get_item_tax_rate(item, tax_rate)
            item_amount = self._get_item_amount(item)
            lines.append({
                'name': item.item_name,
                'description': item.get('description', '') or item.item_name,
                'hs_code': hs_code,
                'uom': uom,
                'quantity': item.qty,
                'rate': item.rate,
                'net_amount': item_amount,
                'unit': 'EA',
                'unit_price': item.rate,
                'tax_category': item.get('zatca_tax_category', 'S'),
                'tax_rate': item_tax_rate,
                'sale_type': sale_type if is_fbr else '',
                'discount': abs(item.get('discount_amount') or item.get('discount') or 0),
                'tax_withheld': item.get('tax_withheld') or 0,
                'extra_tax': item.get('extra_tax') or 0,
                'further_tax': item.get('further_tax') or 0,
                'retail_price': item.get('retail_price') or item.rate or 0,
                'sro_schedule_no': item.get('sro_schedule_no') or '',
                'fed': item.get('fed') or 0,
            })

        seller_tax_id = (company.get('fbr_registration_number') or
                         company.get('tax_id') or '')
        seller_province = company.get('fbr_province') or ''
        seller_name = company.get('fbr_business_name') or company.company_name

        buyer_tax_id = customer.get('tax_id') or ''
        buyer_province = customer.get('state') or ''

        return {
            'invoice_number': si.name,
            'invoice_ref_no': si.name,
            'uuid': si.name,
            'invoice_type': 'Standard',
            'issue_date': si.posting_date,
            'issue_time': '',
            'currency': currency,
            'is_return': si.get('is_return', 0),
            '_sandbox': profile.get('environment') != 'Production',
            'seller': {
                'name': seller_name,
                'tax_id': seller_tax_id,
                'vat_number': company.get('vat_number', company.get('tax_id', '')),
                'province': seller_province,
                'address': self._get_seller_address(company),
                'country': frappe.db.get_value('Country', company.country, 'code'),
            },
            'buyer': {
                'name': customer.customer_name,
                'tax_id': buyer_tax_id,
                'vat_number': customer.get('vat_number', buyer_tax_id),
                'province': buyer_province,
                'address': self._get_buyer_address(customer),
                'country': frappe.db.get_value('Country', customer.get('country'), 'code') or '',
            },
            'items': lines,
            'lines': lines,
            'net_total': si.total or 0,
            'grand_total': si.grand_total or 0,
            'total_vat': tax_total,
            'payable_amount': si.outstanding_amount or si.grand_total or 0,
            'taxes': [{'amount': tax_total, 'rate': tax_rate, 'category': 'S', 'taxable_amount': si.total or 0}],
            'posting_date': si.posting_date,
        }
