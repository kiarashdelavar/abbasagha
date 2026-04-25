from server.bunqService import BunqService
from server.midnightSweeper import MidnightSweeper
from server.habitEnforcer import HabitEnforcer
from server.automation.actionExecutor import ActionExecutor
from server.storage.memoryStore import save_log


class AutomationScheduler:
    def __init__(self):
        self.bunq = BunqService()
        self.executor = ActionExecutor()

    def run_midnight_sweeper_now(self):
        accounts = self.bunq.get_accounts()
        transactions = self.bunq.get_transactions()

        current_balance = "0.00"
        if accounts:
            current_balance = accounts[0].get("balance", "0.00")

        sweeper = MidnightSweeper()
        ai_result = sweeper.analyze_liquidity(
            transactions=transactions,
            current_balance=current_balance,
        )

        log = save_log("MIDNIGHT_SWEEPER_ANALYSIS", {
            "currentBalance": current_balance,
            "aiResult": ai_result,
        })

        return {
            "message": "Midnight sweeper automation ran",
            "currentBalance": current_balance,
            "aiResult": ai_result,
            "action": "For MVP, sweep decision is logged. Money movement can be executed after confirmation.",
            "log": log,
        }

    def run_habit_enforcer_now(self, goal: str, proof_text: str, amount: str):
        habit = HabitEnforcer()

        ai_result = habit.evaluate_habit(
            goal=goal,
            proof_text=proof_text,
        )

        action_result = None

        if "SUCCESS" in ai_result:
            action_result = self.executor.execute_reward(
                amount=amount,
                description="A1 Copilot habit reward",
            )
        elif "FAILED" in ai_result:
            action_result = self.executor.execute_penalty(
                amount=amount,
                description="A1 Copilot habit penalty",
            )

        log = save_log("HABIT_ENFORCER_AUTOMATION", {
            "goal": goal,
            "proofText": proof_text,
            "amount": amount,
            "aiResult": ai_result,
            "actionResult": action_result,
        })

        return {
            "message": "Habit enforcer automation ran",
            "aiResult": ai_result,
            "actionResult": action_result,
            "log": log,
        }