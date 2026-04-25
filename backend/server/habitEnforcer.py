from server.anthropicService import AnthropicService


class HabitEnforcer:
    def __init__(self):
        self.ai = AnthropicService()

    def evaluate_habit(self, goal: str, proof_text: str):
        prompt = f"""
You are A1 Financial Copilot.

Feature: Habit Enforcer.

User goal:
{goal}

Proof or activity data:
{proof_text}

Task:
Decide if the user completed the goal.

Return the answer in this structure:

Status: SUCCESS or FAILED
Confidence: Low/Medium/High
Reason:
Recommended bunq action:
- If SUCCESS: move reward money to fun budget
- If FAILED: send penalty money to charity
Suggested amount:
Notification message:
"""

        return self.ai.ask(prompt, max_tokens=500)