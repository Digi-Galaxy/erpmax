import frappe
from frappe.model.document import Document


class BankConnection(Document):
    def validate(self):
        self.validate_credentials()

    def validate_credentials(self):
        if self.provider == "Plaid" and not self.access_token:
            frappe.throw("Access token is required for Plaid connection")
        if self.provider == "Stripe" and not self.secret_key:
            frappe.throw("Secret key is required for Stripe connection")

    @frappe.whitelist()
    def connect_bank(self):
        if self.provider == "Plaid":
            return self.connect_plaid()
        elif self.provider == "Stripe":
            return self.connect_stripe()
        elif self.provider == "GoCardless":
            return self.connect_gocardless()
        else:
            frappe.throw(f"Provider {self.provider} not supported yet")

    def connect_plaid(self):
        try:
            import plaid
            from plaid.api import plaid_api
            from plaid.model import CreateLinkTokenRequest

            configuration = plaid.Configuration(
                host=plaid.Environment.Production,
                api_key={
                    'clientId': self.client_id,
                    'secret': self.access_token,
                }
            )

            api_client = plaid.ApiClient(configuration)
            plaid_client = plaid_api.PlaidApi(api_client)

            create_link_token_request = CreateLinkTokenRequest(
                user={"client_user_id": self.name},
                client_name="ERPMax",
                products=["transactions"],
                country_codes=["US", "GB", "FR", "DE", "ES", "NL"],
                language="en",
            )

            response = plaid_client.link_token_create(create_link_token_request)
            return {"link_token": response['link_token']}

        except ImportError:
            frappe.throw("Plaid SDK not installed. Run: pip install plaid-python")
        except Exception as e:
            frappe.throw(f"Plaid connection failed: {str(e)}")

    def connect_stripe(self):
        try:
            import stripe
            stripe.api_key = self.secret_key

            balance = stripe.Balance.retrieve()
            return {
                "connected": True,
                "available": balance.available[0].amount / 100,
                "currency": balance.available[0].currency,
            }

        except ImportError:
            frappe.throw("Stripe SDK not installed. Run: pip install stripe")
        except Exception as e:
            frappe.throw(f"Stripe connection failed: {str(e)}")

    def connect_gocardless(self):
        try:
            import requests

            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json",
            }

            response = requests.get(
                "https://bankaccountdata.gocardless.com/api/v2/accounts/",
                headers=headers,
            )

            if response.status_code == 200:
                accounts = response.json().get("results", [])
                return {"connected": True, "accounts": len(accounts)}
            else:
                frappe.throw(f"GoCardless connection failed: {response.text}")

        except ImportError:
            frappe.throw("Requests library not installed")
        except Exception as e:
            frappe.throw(f"GoCardless connection failed: {str(e)}")

    @frappe.whitelist()
    def sync_transactions(self):
        if self.provider == "Plaid":
            return self.sync_plaid_transactions()
        elif self.provider == "Stripe":
            return self.sync_stripe_transactions()
        elif self.provider == "GoCardless":
            return self.sync_gocardless_transactions()
        else:
            frappe.throw(f"Provider {self.provider} not supported yet")

    def sync_plaid_transactions(self):
        try:
            import plaid
            from plaid.api import plaid_api
            from plaid.model import TransactionsGetRequest

            configuration = plaid.Configuration(
                host=plaid.Environment.Production,
                api_key={
                    'clientId': self.client_id,
                    'secret': self.access_token,
                }
            )

            api_client = plaid.ApiClient(configuration)
            plaid_client = plaid_api.PlaidApi(api_client)

            start_date = frappe.utils.add_days(frappe.utils.nowdate(), -30)
            end_date = frappe.utils.nowdate()

            transactions_request = TransactionsGetRequest(
                access_token=self.access_token,
                start_date=start_date,
                end_date=end_date,
            )

            response = plaid_client.transactions_get(transactions_request)
            transactions = response['transactions']

            created = 0
            for txn in transactions:
                self.create_bank_transaction(txn)
                created += 1

            self.last_sync = frappe.utils.nowdate()
            self.db_update()

            return {"synced": created, "total": len(transactions)}

        except Exception as e:
            frappe.throw(f"Transaction sync failed: {str(e)}")

    def sync_stripe_transactions(self):
        try:
            import stripe
            stripe.api_key = self.secret_key

            charges = stripe.BalanceTransaction.list(limit=100)
            created = 0

            for charge in charges.data:
                self.create_bank_transaction({
                    "id": charge.id,
                    "date": charge.created,
                    "amount": charge.amount / 100,
                    "description": charge.description or charge.id,
                    "type": "deposit" if charge.amount > 0 else "withdrawal",
                })
                created += 1

            self.last_sync = frappe.utils.nowdate()
            self.db_update()

            return {"synced": created, "total": len(charges.data)}

        except Exception as e:
            frappe.throw(f"Stripe sync failed: {str(e)}")

    def sync_gocardless_transactions(self):
        try:
            import requests

            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json",
            }

            response = requests.get(
                "https://bankaccountdata.gocardless.com/api/v2/transactions/",
                headers=headers,
            )

            if response.status_code == 200:
                transactions = response.json().get("results", [])
                created = 0

                for txn in transactions:
                    self.create_bank_transaction(txn)
                    created += 1

                self.last_sync = frappe.utils.nowdate()
                self.db_update()

                return {"synced": created, "total": len(transactions)}
            else:
                frappe.throw(f"GoCardless sync failed: {response.text}")

        except Exception as e:
            frappe.throw(f"GoCardless sync failed: {str(e)}")

    def create_bank_transaction(self, txn_data):
        try:
            amount = abs(txn_data.get("amount", 0))
            transaction_type = "Credit" if txn_data.get("amount", 0) > 0 else "Debit"

            bt = frappe.get_doc({
                "doctype": "Bank Transaction",
                "bank_account": self.linked_bank_account,
                "transaction_id": txn_data.get("id", ""),
                "posting_date": txn_data.get("date", frappe.utils.nowdate()),
                "description": txn_data.get("description", ""),
                "transaction_type": transaction_type,
                "amount": amount,
                "currency": txn_data.get("currency", "USD"),
                "status": "Pending",
                "provider": self.provider,
            })
            bt.flags.ignore_permissions = True
            bt.insert()
            return bt.name

        except Exception as e:
            frappe.log_error(f"Failed to create bank transaction: {str(e)}")
            return None


@frappe.whitelist()
def sync_all_connected_banks():
    connections = frappe.get_all(
        "Bank Connection",
        filters={"status": "Connected", "auto_sync": 1},
        fields=["name"],
    )
    results = []
    for conn in connections:
        try:
            bank_conn = frappe.get_doc("Bank Connection", conn.name)
            results.append({"connection": conn.name, "result": bank_conn.sync_transactions()})
        except Exception as e:
            frappe.log_error(f"Failed to sync bank connection {conn.name}: {str(e)}")
            results.append({"connection": conn.name, "error": str(e)})
    return results
