import frappe
from frappe import _


def get_chrome_pdf(print_format, html, options, output, pdf_generator=None):
	from erpmax.utils.pdf_generator.browser import Browser
	from erpmax.utils.pdf_generator.chrome_pdf_generator import ChromePDFGenerator
	from erpmax.utils.pdf_generator.pdf_merge import PDFTransformer

	if pdf_generator != "chrome":
		return

	generator = ChromePDFGenerator()
	browser = Browser(generator, print_format, html, options)
	transformer = PDFTransformer(browser)

	return transformer.transform_pdf(output=output)


def get_host_url():
	if frappe.request:
		return frappe.request.host_url
	else:
		return frappe.utils.get_url() + "/"
