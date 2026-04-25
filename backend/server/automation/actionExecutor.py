from server.bunqService import BunqService
from server.automation.safetyGuard import SafetyGuard
from server.storage.memoryStore import save_log


class ActionExecutor:
    def __init__(self):
        self.bunq = BunqService()

    def execute_reward(self, amount: str, description: str):
        safety = SafetyGuard.validate_sandbox_payment(amount)

        if not safety["allowed"]:
            return {
                "executed": False,
                "reason": safety["reason"],
            }

        result = self.bunq.request_test_money(
            amount=amount,
            description=description,
        )

        log = save_log("REWARD_EXECUTED", {
            "amount": amount,
            "description": description,
            "result": result,
        })

        return {
            "executed": True,
            "type": "reward",
            "log": log,
        }

    def execute_penalty(self, amount: str, description: str):
        safety = SafetyGuard.validate_sandbox_payment(amount)

        if not safety["allowed"]:
            return {
                "executed": False,
                "reason": safety["reason"],
            }

        result = self.bunq.send_test_payment(
            amount=amount,
            description=description,
        )

        log = save_log("PENALTY_EXECUTED", {
            "amount": amount,
            "description": description,
            "result": result,
        })

        return {
            "executed": True,
            "type": "penalty",
            "log": log,
        }

    def execute_savings_account_creation(self):
        result = self.bunq.create_savings_account("A1 AI Savings Account")

        log = save_log("SAVINGS_ACCOUNT_CREATED", {
            "result": result,
        })

        return {
            "executed": True,
            "type": "create_savings_account",
            "log": log,
        }