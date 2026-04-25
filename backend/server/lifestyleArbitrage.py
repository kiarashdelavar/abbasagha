from server.anthropicService import AnthropicService


class LifestyleArbitrage:
    def __init__(self):
        self.ai = AnthropicService()

    def analyze_purchase(self, product_name: str, user_prices: str):
        prompt = f"""
You are A1 Financial Copilot.

Feature: Lifestyle Arbitrageur.

The user wants to buy:
{product_name}

The user provided these price options:
{user_prices}

Task:
1. Compare prices.
2. Find the cheapest option.
3. Explain if buying in another currency is useful.
4. Suggest a safe payment strategy.
5. Return the answer in this structure:

Best option:
Estimated saving:
Recommended currency:
Recommended bunq action:
Risk:
Short explanation:
"""

        return self.ai.ask(prompt, max_tokens=500)

    def build_virtual_card_demo_response(self, target_currency: str):
        return {
            "message": "Sandbox demo only",
            "targetCurrency": target_currency,
            "bunqAction": "Create a sub-account for the selected currency",
            "virtualCardStatus": "Virtual card creation is represented as a demo step in this MVP.",
            "note": "For the hackathon demo, we show the planned bunq flow without exposing real card details."
        }