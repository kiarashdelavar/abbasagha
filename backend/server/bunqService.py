import os
from dotenv import load_dotenv
from bunq_client import BunqClient

load_dotenv()


class BunqService:
    def __init__(self):
        api_key = os.getenv("BUNQ_API_KEY", "").strip()

        if not api_key:
            raise ValueError("BUNQ_API_KEY is missing in .env file")

        self.client = BunqClient(api_key=api_key, sandbox=True)
        self.client.authenticate()
        self.user_id = self.client.user_id
        self.account_id = self.client.get_primary_account_id()

    def get_accounts(self):
        accounts = self.client.get(
            f"user/{self.user_id}/monetary-account-bank"
        )

        result = []

        for item in accounts:
            account = item.get("MonetaryAccountBank", {})

            balance = account.get("balance", {})

            result.append({
                "id": account.get("id"),
                "description": account.get("description"),
                "status": account.get("status"),
                "currency": balance.get("currency"),
                "balance": balance.get("value"),
                "iban": account.get("alias", [{}])[0].get("value")
                if account.get("alias") else None,
            })

        return result

    def get_transactions(self):
        payments = self.client.get(
            f"user/{self.user_id}/monetary-account/{self.account_id}/payment",
            params={"count": 50},
        )

        transactions = []

        for item in payments:
            payment = item.get("Payment", {})
            amount = payment.get("amount", {})
            counterparty = payment.get("counterparty_alias", {})
            balance_after = payment.get("balance_after_mutation", {})

            transactions.append({
                "id": payment.get("id"),
                "created": payment.get("created"),
                "updated": payment.get("updated"),
                "amount": amount.get("value"),
                "currency": amount.get("currency"),
                "counterparty": counterparty.get("display_name"),
                "counterpartyIban": counterparty.get("iban"),
                "description": payment.get("description"),
                "type": payment.get("type"),
                "subType": payment.get("sub_type"),
                "status": payment.get("payment_arrival_expected", {}).get("status"),
                "balanceAfter": balance_after.get("value"),
                "balanceCurrency": balance_after.get("currency"),
            })

        return transactions

    def get_transaction_by_id(self, payment_id: int):
        payment_detail = self.client.get(
            f"user/{self.user_id}/monetary-account/{self.account_id}/payment/{payment_id}"
        )

        if not payment_detail:
            return None

        payment = payment_detail[0].get("Payment", {})
        amount = payment.get("amount", {})
        counterparty = payment.get("counterparty_alias", {})
        balance_after = payment.get("balance_after_mutation", {})

        return {
            "id": payment.get("id"),
            "created": payment.get("created"),
            "updated": payment.get("updated"),
            "amount": amount.get("value"),
            "currency": amount.get("currency"),
            "counterparty": counterparty.get("display_name"),
            "counterpartyIban": counterparty.get("iban"),
            "description": payment.get("description"),
            "type": payment.get("type"),
            "subType": payment.get("sub_type"),
            "status": payment.get("payment_arrival_expected", {}).get("status"),
            "balanceAfter": balance_after.get("value"),
            "balanceCurrency": balance_after.get("currency"),
            "raw": payment,
        }

    def request_test_money(self, amount: str, description: str):
        return self.client.post(
            f"user/{self.user_id}/monetary-account/{self.account_id}/request-inquiry",
            {
                "amount_inquired": {
                    "value": amount,
                    "currency": "EUR",
                },
                "counterparty_alias": {
                    "type": "EMAIL",
                    "value": "sugardaddy@bunq.com",
                    "name": "Sugar Daddy",
                },
                "description": description,
                "allow_bunqme": False,
            },
        )

    def send_test_payment(self, amount: str, description: str):
        return self.client.post(
            f"user/{self.user_id}/monetary-account/{self.account_id}/payment",
            {
                "amount": {
                    "value": amount,
                    "currency": "EUR",
                },
                "counterparty_alias": {
                    "type": "EMAIL",
                    "value": "sugardaddy@bunq.com",
                    "name": "Sugar Daddy",
                },
                "description": description,
            },
        )

    def create_savings_account(self, description: str = "AI Savings Account"):
        return self.client.post(
            f"user/{self.user_id}/monetary-account-bank",
            {
                "currency": "EUR",
                "description": description,
            },
        )