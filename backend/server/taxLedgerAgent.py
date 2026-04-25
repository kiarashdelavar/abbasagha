from server.anthropicService import AnthropicService


class TaxLedgerAgent:
    def __init__(self):
        self.ai = AnthropicService()

    def create_ledger_entry(self, receipt_text: str, transaction_detail: dict):
        prompt = f"""
You are A1 Financial Copilot.

Feature: Real-time Tax & Ledger Agent.

Transaction detail:
{transaction_detail}

Receipt text:
{receipt_text}

Task:
Extract receipt data and generate a clean personal accounting note.

Use exactly this format:

Title: Receipt F-[random-code]: [Store Name] ([Short Purchase Description])

Text:
Receipt Code: F-[random-code]
Store: [Store Name]
Date: [DD/MM/YYYY]
Total Amount: €[amount]
Payment Method: bunq sandbox account
Items:
- [Item name] ([English translation if needed]): €[price]

VAT:
- VAT detected: Yes/No
- VAT amount: €[amount or unknown]

Category:
[Food / Travel / Software / Office / Education / Other]

Tax note:
[Simple explanation if this might be tax relevant]
"""

        return self.ai.ask(prompt, max_tokens=700)