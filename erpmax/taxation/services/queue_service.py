import frappe
import traceback
from frappe.utils import now_datetime, add_to_date
from ..providers import get_provider_for_country


class QueueService:

    def enqueue(self, compliance_invoice, action='Submit', priority=0):
        ci = frappe.get_doc('Tax Compliance Invoice', compliance_invoice)
        profile = frappe.get_doc('Tax Country Profile', ci.provider)
        company = ci.company

        existing = frappe.db.exists('Tax Compliance Queue', {
            'compliance_invoice': compliance_invoice,
            'action': action,
            'status': ('in', ('Pending', 'Processing')),
        })
        if existing:
            return frappe.get_doc('Tax Compliance Queue', existing)

        q = frappe.get_doc({
            'doctype': 'Tax Compliance Queue',
            'compliance_invoice': compliance_invoice,
            'action': action,
            'status': 'Pending',
            'provider': ci.provider,
            'company': company,
            'priority': priority,
            'max_retries': 5,
            'scheduled_at': now_datetime(),
        })
        q.insert(ignore_permissions=True)
        return q

    def process_queue(self, batch_size=20):
        pending = frappe.get_all('Tax Compliance Queue', {
            'status': 'Pending',
            'scheduled_at': ('<=', now_datetime()),
        }, order_by='priority desc, creation asc', limit=batch_size)

        processed = []
        for q_name in pending:
            q = frappe.get_doc('Tax Compliance Queue', q_name)
            try:
                q.set_processing()
                frappe.db.commit()

                result = self._execute(q)
                if result.get('success'):
                    q.set_completed()
                else:
                    self._handle_retry(q, result.get('error', 'Unknown error'))

            except Exception as e:
                self._handle_retry(q, str(e), traceback.format_exc())

            frappe.db.commit()
            processed.append(q.name)

        return processed

    def retry_stuck(self, timeout_minutes=30):
        cutoff = add_to_date(now_datetime(), minutes=-timeout_minutes, as_datetime=True)
        stuck = frappe.get_all('Tax Compliance Queue', {
            'status': 'Processing',
            'started_at': ('<=', cutoff),
        })

        recovered = []
        for q_name in stuck:
            q = frappe.get_doc('Tax Compliance Queue', q_name)
            q.status = 'Pending'
            q.next_retry_at = now_datetime()
            q.last_error = 'Stuck - retrying'
            q.save()
            frappe.db.commit()
            recovered.append(q.name)

        return recovered

    def _execute(self, q):
        ci = frappe.get_doc('Tax Compliance Invoice', q.compliance_invoice)
        profile = frappe.get_doc('Tax Country Profile', ci.provider)
        provider = get_provider_for_country(profile.country_code)

        provider_config = frappe.db.get_value('Tax Provider Config',
            {'company': ci.company}, '*') or {}

        if q.action == 'Submit':
            content = ci.signed_xml or ci.xml_content
            if not content:
                return {'success': False, 'error': 'No XML content to submit'}
            response = provider.submit(content, provider_config)
            ok = getattr(response, 'ok', response.get('success', False))
            if ok:
                ci.submission_id = getattr(response, 'json', lambda: {})().get('submissionId', '')
                ci.submitted_at = now_datetime()
                ci.submitted_by = frappe.session.user
                ci.status = 'Submitted'
            else:
                error = getattr(response, 'text', response.get('error', 'API error'))
                ci.status = 'Failed'
                ci.status_message = str(error)[:280]
            ci.save()

        elif q.action == 'Status Check':
            if not ci.submission_id:
                return {'success': False, 'error': 'No submission ID'}
            response = provider.check_status(ci.submission_id, provider_config)
            ci.last_status_check = now_datetime()
            ci.save()

        return {'success': True}

    def _handle_retry(self, q, error, tb=None):
        retry = q.retry_count or 0
        max_r = q.max_retries or 5
        q.last_error = str(error)[:280]
        q.error_traceback = tb or ''
        q.completed_at = now_datetime()

        if retry >= max_r:
            q.status = 'Failed'
        else:
            q.status = 'Pending'
            backoff_minutes = 2 ** retry
            q.next_retry_at = add_to_date(now_datetime(), minutes=backoff_minutes, as_datetime=True)
        q.save()

    def cleanup(self, days=30):
        cutoff = add_to_date(now_datetime(), days=-days, as_datetime=True)
        frappe.db.delete('Tax Compliance Queue', {
            'status': ('in', ('Completed', 'Failed')),
            'modified': ('<=', cutoff),
        })


# Scheduler entry points
def process_queue():
    qs = QueueService()
    qs.process_queue()


def retry_stuck_queue():
    qs = QueueService()
    qs.retry_stuck()


def cleanup_queue():
    qs = QueueService()
    qs.cleanup()
