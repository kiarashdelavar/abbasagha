from server.anthropicService import AnthropicService


class MidnightSweeper:
    def __init__(self):
        self.ai = AnthropicService()

    def analyze_liquidity(self, transactions, current_balance: str):
        transaction_text = ""

        for transaction in transactions:
            transaction_text += (
                f"- {transaction.get('created')} | "
                f"{transaction.get('amount')} {transaction.get('currency')} | "
                f"{transaction.get('counterparty')} | "
                f"{transaction.get('description')}\n"
            )

        prompt = f"""
You are A1 Financial Copilot.

Feature: Midnight Liquidity Sweeper.

The user has this current balance:
{current_balance} EUR

Recent transactions:
{transaction_text}

Task:
1. Estimate how much money the user should keep in the main account for tomorrow.
2. Estimate how much money can be moved to savings overnight.
3. Explain the reason in simple English.
4. Return the answer in this structure:

Keep in main account:
Move to savings:
Reason:
Risk level:
Notification message:
"""

        return self.ai.ask(prompt, max_tokens=500)