from server.bunqService import BunqService
from server.storage.memoryStore import save_log


class WebhookHandler:
    def __init__(self):
        self.bunq = BunqService()

    def handle_bunq_webhook(self, payload: dict):
        transactions = self.bunq.get_transactions()

        latest_transaction = None
        if transactions:
            latest_transaction = transactions[0]

        routing_result = self.route_transaction(latest_transaction)

        log = save_log("BUNQ_WEBHOOK_RECEIVED", {
            "payload": payload,
            "latestTransaction": latest_transaction,
            "routingResult": routing_result,
        })

        return {
            "message": "Webhook received and processed",
            "latestTransaction": latest_transaction,
            "routingResult": routing_result,
            "log": log,
        }

    def route_transaction(self, transaction):
        if transaction is None:
            return {
                "selectedAgent": None,
                "reason": "No transaction found",
            }

        description = str(transaction.get("description", "")).lower()

        if "payment" in description or "receipt" in description:
            return {
                "selectedAgent": "TaxLedgerAgent",
                "reason": "Transaction looks like a payment that can be documented.",
            }

        if "subscription" in description or "monthly" in description:
            return {
                "selectedAgent": "MidnightSweeper",
                "reason": "Transaction looks recurring and useful for liquidity planning.",
            }

        return {
            "selectedAgent": "GeneralTransactionMonitor",
            "reason": "No special automation needed.",
        }