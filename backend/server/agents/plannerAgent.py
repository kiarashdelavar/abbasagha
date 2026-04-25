import json
import re
from server.anthropicService import AnthropicService

class PlannerAgent:
    def __init__(self):
        self.ai = AnthropicService()

    def create_plan(self, user_message: str, conversation_history: list):
        history_text = ""
        for item in conversation_history[-8:]:
            history_text += f"{item.get('role')}: {item.get('message')}\n"

        prompt = f"""
You are the Lead Planner for A1 Financial Copilot.
Your mission is to process the user's request into a structured JSON plan.

CORE FEATURES:
1. midnight_sweeper (Liquidity management)
2. lifestyle_arbitrage (Price comparison & shopping)
3. tax_ledger (Receipts & accounting)
4. habit_enforcer (Reward/Penalty system)

DYNAMIC LANGUAGE RULE:
1. Identify the language used by the user in the "User message".
2. You MUST write the "reply" field in the EXACT same language (Persian, English, Dutch, etc.).
3. DO NOT use a default language. Match the user's tone and tongue.

HACKATHON EXECUTION RULES:
- If prices are requested, SIMULATE them confidently. Provide markdown links like [Store](URL).
- Never explain that you are an AI. Be the copilot.
- Return ONLY valid JSON. No pre-text, no post-text, no notes.

JSON schema:
{{
  "intent": "midnight_sweeper | lifestyle_arbitrage | tax_ledger | habit_enforcer | general_chat",
  "reply": "Your conversational response in the USER'S LANGUAGE. Use markdown for links.",
  "createsTask": true/false,
  "requiresConfirmation": true/false,
  "task": {{
    "agentType": "string",
    "scheduleType": "daily | weekly | once | webhook",
    "runAt": "HH:MM",
    "config": {{}}
  }}
}}

Conversation history:
{history_text}

User message:
{user_message}
"""

        ai_response = self.ai.ask(prompt, max_tokens=800)
        
        match = re.search(r'\{[\s\S]*\}', ai_response)
        
        if match:
            json_str = match.group(0)
            try:
                return json.loads(json_str)
            except json.JSONDecodeError:
                pass
        
        return {
            "intent": "general_chat",
            "reply": ai_response.strip(),
            "createsTask": False,
            "requiresConfirmation": False,
            "task": None
        }