import json
import time
import frappe
from ..providers import get_provider_for_country


class SubmissionService:

    def submit_compliance_invoice(self, ci_name):
        ci = frappe.get_doc('Tax Compliance Invoice', ci_name)
        profile = frappe.get_doc('Tax Country Profile', ci.provider)
        provider = get_provider_for_country(profile.country_code)

        if ci.status not in ('Validated', 'Signed'):
            frappe.throw('Compliance invoice must be Validated or Signed')

        provider_config = frappe.db.get_value('Tax Provider Config',
            {'company': ci.company}, '*') or {}

        clearance_required = bool(provider_config.get('clearance_required')) or bool(profile.get('clearance_required'))
        ci.submission_type = 'Clearance' if clearance_required else 'Reporting'
        if clearance_required:
            ci.clearance_status = 'Pending'
        else:
            ci.reporting_status = 'Pending'

        request_payload = ci.signed_xml or ci.xml_content
        started = time.time()
        try:
            response = provider.submit(request_payload, provider_config)
            duration_ms = int((time.time() - started) * 1000)
            response_data = self._normalise_response(response)
            success = response_data.get('success')

            ci.tax_authority_status_code = response_data.get('status_code')
            ci.tax_authority_response = json.dumps(response_data.get('data') or response_data, indent=2, default=str)

            if success:
                ci.submission_id = response_data.get('submission_id') or response_data.get('data', {}).get('submissionId') or response_data.get('data', {}).get('uuid') or ''
                ci.submitted_at = frappe.utils.now_datetime()
                ci.submitted_by = frappe.session.user
                if clearance_required:
                    ci.status = 'Cleared'
                    ci.clearance_status = 'Cleared'
                    ci.cleared_at = frappe.utils.now_datetime()
                else:
                    ci.status = 'Submitted'
                    ci.reporting_status = 'Reported'
                    ci.reported_at = frappe.utils.now_datetime()
                self._log(ci, 'Submit', 'Success', request_data=request_payload, response_data=response_data, duration_ms=duration_ms)
            else:
                ci.status = 'Failed'
                if clearance_required:
                    ci.clearance_status = 'Rejected'
                else:
                    ci.reporting_status = 'Rejected'
                ci.status_message = response_data.get('error') or response_data.get('text') or json.dumps(response_data, default=str)
                self._log(ci, 'Submit', 'Failed', error=ci.status_message, request_data=request_payload, response_data=response_data, duration_ms=duration_ms)

            ci.save()
        except Exception as e:
            duration_ms = int((time.time() - started) * 1000)
            ci.status = 'Failed'
            ci.status_message = str(e)
            ci.save()
            self._log(ci, 'Submit', 'Failed', error=str(e), request_data=request_payload, response_data={'error': str(e)}, duration_ms=duration_ms)

        return ci

    def _normalise_response(self, response):
        if isinstance(response, dict):
            data = response.get('data') or {}
            return {
                'success': bool(response.get('success')),
                'status_code': response.get('status_code'),
                'data': data,
                'error': response.get('error') or '',
                'submission_id': data.get('submissionId') or data.get('uuid') if isinstance(data, dict) else '',
            }

        ok = bool(getattr(response, 'ok', False))
        status_code = getattr(response, 'status_code', None)
        text = getattr(response, 'text', '')
        try:
            data = response.json() if text else {}
        except Exception:
            data = {'text': text}
        return {
            'success': ok,
            'status_code': status_code,
            'data': data,
            'text': text,
            'error': '' if ok else text,
            'submission_id': data.get('submissionId') or data.get('uuid') if isinstance(data, dict) else '',
        }

    def _log(self, ci, action, status, error=None, request_data=None, response_data=None, duration_ms=None):
        log = frappe.get_doc({
            'doctype': 'Tax Submission Log',
            'compliance_invoice': ci.name,
            'action_type': action,
            'status': status,
            'timestamp': frappe.utils.now_datetime(),
            'performed_by': frappe.session.user,
            'request_data': request_data if isinstance(request_data, str) else json.dumps(request_data or {}, default=str),
            'response_data': json.dumps(response_data or {}, indent=2, default=str),
            'duration_ms': duration_ms,
            'error_message': error or '',
        })
        log.insert(ignore_permissions=True)
        return log
