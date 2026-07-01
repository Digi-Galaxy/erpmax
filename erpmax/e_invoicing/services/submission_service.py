import frappe
import json
from ..providers import get_provider_for_country


class SubmissionService:

    def submit_einvoice(self, einvoice_name):
        einvoice = frappe.get_doc("EH E-Invoice", einvoice_name)
        provider_config = frappe.get_doc("EH Provider Config", einvoice.provider_config)
        profile = frappe.get_doc("EH Country Profile", einvoice.country_profile)

        provider = get_provider_for_country(profile.country_code)

        if einvoice.status not in ("Validated", "Signed"):
            frappe.throw(
                "E-Invoice must be in Validated or Signed status before submission. "
                "Current status: {0}".format(einvoice.status)
            )

        try:
            response = provider.submit(einvoice.signed_xml, provider_config)

            if response.status_code in (200, 201, 202):
                response_data = response.json()
                einvoice.submission_id = response_data.get("submissionId", "")
                einvoice.submitted_at = frappe.utils.now_datetime()
                einvoice.submitted_by = frappe.session.user
                einvoice.status = "Submitted"

                log = self._create_submission_log(
                    einvoice, "Submit", "Success", response_data=response.text
                )

                einvoice.save()
                return einvoice

            else:
                einvoice.status = "Failed"
                einvoice.status_message = "HTTP {0}: {1}".format(
                    response.status_code, response.text
                )

                log = self._create_submission_log(
                    einvoice, "Submit", "Failed",
                    error=response.text,
                    response_data=response.text,
                )

                error_log = frappe.get_doc({
                    "doctype": "EH Error Log",
                    "error_type": "Submission",
                    "severity": "High",
                    "einvoice": einvoice.name,
                    "error_message": response.text,
                    "suggested_fix": "Check API credentials and network connectivity",
                })
                error_log.insert()
                einvoice.error_log = error_log.name

                einvoice.save()
                return einvoice

        except Exception as e:
            einvoice.status = "Failed"
            einvoice.status_message = str(e)
            einvoice.save()

            error_log = frappe.get_doc({
                "doctype": "EH Error Log",
                "error_type": "Connection",
                "severity": "Critical",
                "einvoice": einvoice.name,
                "error_message": str(e),
                "traceback": frappe.get_traceback(),
            })
            error_log.insert()
            einvoice.error_log = error_log.name
            einvoice.save()

            return einvoice

    def check_status(self, einvoice_name):
        einvoice = frappe.get_doc("EH E-Invoice", einvoice_name)
        provider_config = frappe.get_doc("EH Provider Config", einvoice.provider_config)
        profile = frappe.get_doc("EH Country Profile", einvoice.country_profile)

        provider = get_provider_for_country(profile.country_code)

        if not einvoice.submission_id:
            frappe.throw("No submission ID found for this e-invoice")

        try:
            response = provider.check_status(einvoice.submission_id, provider_config)

            einvoice.last_status_check = frappe.utils.now_datetime()

            if response.status_code == 200:
                data = response.json()
                einvoice.status = data.get("status", einvoice.status)
                einvoice.status_message = data.get("message", "")
            else:
                einvoice.status_message = "Status check failed: HTTP {0}".format(
                    response.status_code
                )

            einvoice.save()
            return einvoice

        except Exception as e:
            einvoice.status_message = "Status check error: {0}".format(str(e))
            einvoice.save()
            return einvoice

    def _create_submission_log(self, einvoice, action, status, error=None, response_data=None):
        log = frappe.get_doc({
            "doctype": "EH Submission Log",
            "einvoice": einvoice.name,
            "action_type": action,
            "status": status,
            "timestamp": frappe.utils.now_datetime(),
            "performed_by": frappe.session.user,
            "error_message": error or "",
            "response_data": response_data or "",
        })
        log.insert(ignore_permissions=True)
        return log
