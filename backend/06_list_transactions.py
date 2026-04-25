"""
Tutorial 06 — List Transactions

Retrieves payment history for your account.
Shows transaction id, date, amount, counterparty, and description.

Endpoints used:
  GET /v1/user/{userId}/monetary-account/{accountId}/payment
  GET /v1/user/{userId}/monetary-account/{accountId}/payment/{paymentId}
"""

import os
import json

from dotenv import load_dotenv
from bunq_client import BunqClient

load_dotenv()


def main() -> None:
    api_key = os.getenv("BUNQ_API_KEY", "").strip()

    if not api_key:
        print("No BUNQ_API_KEY found — creating a sandbox user...")
        api_key = BunqClient.create_sandbox_user()
        print(f"  API key: {api_key}\n")

    client = BunqClient(api_key=api_key, sandbox=True)
    client.authenticate()

    account_id = client.get_primary_account_id()
    print(f"Authenticated — user {client.user_id}, account {account_id}\n")

    payments = client.get(
        f"user/{client.user_id}/monetary-account/{account_id}/payment",
        params={"count": 20},
    )

    if not payments:
        print("No transactions yet — run 03_make_payment.py first.")
        return

    print("Recent transactions:")
    print("-" * 110)
    print(f"{'ID':<12} {'Date':<22} {'Amount':>12}  {'Counterparty':<25} {'Description'}")
    print("-" * 110)

    for item in payments:
        p = item.get("Payment", {})

        payment_id = p.get("id", "?")
        date = p.get("created", "")[:19]

        amount = p.get("amount", {})
        amount_str = f"{amount.get('value', '?')} {amount.get('currency', '')}"

        counterparty = p.get("counterparty_alias", {}).get("display_name", "?")
        description = p.get("description", "")

        print(f"{payment_id:<12} {date:<22} {amount_str:>12}  {counterparty:<25} {description}")

    print(f"\nShowing {len(payments)} transaction(s)")

    selected_id = input("\nEnter a payment ID to see full details, or press Enter to exit: ").strip()

    if not selected_id:
        return

    payment_detail = client.get(
        f"user/{client.user_id}/monetary-account/{account_id}/payment/{selected_id}"
    )

    if not payment_detail:
        print("No detail found for this payment ID.")
        return

    p = payment_detail[0].get("Payment", {})

    print("\nPayment details:")
    print("-" * 80)
    print(f"ID: {p.get('id')}")
    print(f"Created: {p.get('created')}")
    print(f"Updated: {p.get('updated')}")

    amount = p.get("amount", {})
    print(f"Amount: {amount.get('value')} {amount.get('currency')}")

    counterparty = p.get("counterparty_alias", {})
    print(f"Counterparty name: {counterparty.get('display_name')}")
    print(f"Counterparty type: {counterparty.get('type')}")
    print(f"Counterparty value: {counterparty.get('value')}")

    print(f"Description: {p.get('description')}")
    print(f"Type: {p.get('type')}")
    print(f"Sub type: {p.get('sub_type')}")
    print(f"Merchant reference: {p.get('merchant_reference')}")

    print("\nRaw JSON:")
    print("-" * 80)
    print(json.dumps(p, indent=2))


if __name__ == "__main__":
    main()