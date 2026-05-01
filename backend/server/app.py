import re
from io import BytesIO

import pytesseract
from PIL import Image
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from server.bunqService import BunqService
from server.midnightSweeper import MidnightSweeper
from server.lifestyleArbitrage import LifestyleArbitrage
from server.taxLedgerAgent import TaxLedgerAgent
from server.habitEnforcer import HabitEnforcer

from server.automation.webhookHandler import WebhookHandler
from server.automation.scheduler import AutomationScheduler
from server.automation.taskStore import get_tasks_for_user, load_tasks
from server.storage.memoryStore import load_logs
from server.chat.chatOrchestrator import ChatOrchestrator

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

app = FastAPI(
    title="A1 Financial Copilot",
    description="Always-on bunq sandbox financial chatbot with Claude AI agents",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class PaymentRequest(BaseModel):
    amount: str
    description: str


class LifestyleRequest(BaseModel):
    productName: str
    priceOptions: str
    targetCurrency: str = "EUR"


class LedgerRequest(BaseModel):
    paymentId: int
    receiptText: str


class HabitRequest(BaseModel):
    goal: str
    proofText: str
    amount: str = "10.00"


class WebhookPayload(BaseModel):
    eventType: str = "bunq_transaction"
    data: dict = {}


class AutomationHabitRequest(BaseModel):
    goal: str
    proofText: str
    amount: str = "10.00"


class ChatMessageRequest(BaseModel):
    userId: str = "demo-user-1"
    message: str


@app.get("/")
def home():
    return {
        "message": "A1 Financial Copilot backend is running",
        "mode": "always-on agentic chatbot backend",
        "features": [
            "bunq transactions",
            "Claude AI planner",
            "chat command endpoint",
            "task creation and activation",
            "webhook receiver",
            "automation logs",
            "Midnight Liquidity Sweeper",
            "Lifestyle Arbitrageur",
            "Tax & Ledger Agent",
            "Habit Enforcer",
        ],
    }


@app.post("/api/chat/message")
def chat_message(request: ChatMessageRequest):
    orchestrator = ChatOrchestrator()
    return orchestrator.handle_message(
        user_id=request.userId,
        message=request.message,
    )


@app.get("/api/chat/tasks/{user_id}")
def chat_tasks(user_id: str):
    return get_tasks_for_user(user_id)


@app.get("/api/automation/tasks")
def automation_tasks():
    return load_tasks()


@app.get("/api/automation/logs")
def get_automation_logs():
    return load_logs()


@app.post("/api/webhooks/bunq")
def bunq_webhook(payload: WebhookPayload):
    handler = WebhookHandler()
    return handler.handle_bunq_webhook(payload.dict())


@app.post("/api/automation/midnight-sweeper/run")
def run_midnight_sweeper_automation():
    scheduler = AutomationScheduler()
    return scheduler.run_midnight_sweeper_now()


@app.post("/api/automation/habit-enforcer/run")
def run_habit_enforcer_automation(request: AutomationHabitRequest):
    scheduler = AutomationScheduler()
    return scheduler.run_habit_enforcer_now(
        goal=request.goal,
        proof_text=request.proofText,
        amount=request.amount,
    )


@app.get("/api/bunq/accounts")
def get_accounts():
    service = BunqService()
    return service.get_accounts()


@app.get("/api/bunq/transactions")
def get_transactions():
    service = BunqService()
    return service.get_transactions()


@app.get("/api/bunq/transactions/{payment_id}")
def get_transaction_detail(payment_id: int):
    try:
        service = BunqService()
        transaction = service.get_transaction_by_id(payment_id)

        if transaction is None:
            raise HTTPException(status_code=404, detail="Transaction not found")

        return transaction

    except Exception as error:
        raise HTTPException(
            status_code=404,
            detail=f"Transaction not found or bunq error: {str(error)}",
        )


@app.post("/api/bunq/request-money")
def request_money(request: PaymentRequest):
    service = BunqService()
    result = service.request_test_money(
        amount=request.amount,
        description=request.description,
    )

    return {
        "message": "Payment request created",
        "result": result,
    }


@app.post("/api/bunq/send-payment")
def send_payment(request: PaymentRequest):
    service = BunqService()
    result = service.send_test_payment(
        amount=request.amount,
        description=request.description,
    )

    return {
        "message": "Payment sent",
        "result": result,
    }


@app.post("/api/bunq/create-savings-account")
def create_savings_account():
    service = BunqService()
    result = service.create_savings_account()

    return {
        "message": "Savings account created",
        "result": result,
    }


@app.get("/api/ai/midnight-sweeper")
def midnight_sweeper():
    service = BunqService()
    transactions = service.get_transactions()

    accounts = service.get_accounts()
    current_balance = "0.00"

    if accounts:
        current_balance = accounts[0].get("balance", "0.00")

    sweeper = MidnightSweeper()
    ai_result = sweeper.analyze_liquidity(
        transactions=transactions,
        current_balance=current_balance,
    )

    return {
        "feature": "Midnight Liquidity Sweeper",
        "currentBalance": current_balance,
        "aiResult": ai_result,
    }


@app.post("/api/ai/lifestyle-arbitrage")
def lifestyle_arbitrage(request: LifestyleRequest):
    arbitrage = LifestyleArbitrage()

    ai_result = arbitrage.analyze_purchase(
        product_name=request.productName,
        user_prices=request.priceOptions,
    )

    virtual_card_demo = arbitrage.build_virtual_card_demo_response(
        target_currency=request.targetCurrency,
    )

    return {
        "feature": "Lifestyle Arbitrageur",
        "aiResult": ai_result,
        "bunqDemoAction": virtual_card_demo,
    }


@app.post("/api/ai/tax-ledger")
def tax_ledger(request: LedgerRequest):
    bunq = BunqService()
    transaction = bunq.get_transaction_by_id(request.paymentId)

    if transaction is None:
        raise HTTPException(status_code=404, detail="Transaction not found")

    agent = TaxLedgerAgent()

    ledger_note = agent.create_ledger_entry(
        receipt_text=request.receiptText,
        transaction_detail=transaction,
    )

    return {
        "feature": "Real-time Tax & Ledger Agent",
        "transaction": transaction,
        "ledgerNote": ledger_note,
    }


@app.post("/api/ai/habit-enforcer")
def habit_enforcer(request: HabitRequest):
    agent = HabitEnforcer()
    ai_result = agent.evaluate_habit(
        goal=request.goal,
        proof_text=request.proofText,
    )

    return {
        "feature": "Habit Enforcer",
        "aiResult": ai_result,
        "sandboxActionOptions": {
            "successAction": "Use POST /api/bunq/request-money as a reward demo",
            "failedAction": "Use POST /api/bunq/send-payment as a charity penalty demo",
            "amount": request.amount,
        },
    }

def extract_text_from_receipt_image(file_bytes: bytes) -> str:
    """
    Extract raw text from a receipt image using OCR.
    """

    try:
        image = Image.open(BytesIO(file_bytes))
        image = image.convert("L")

        text = pytesseract.image_to_string(image, config="--psm 6")

        return text.strip()

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"OCR failed. Make sure Tesseract OCR is installed. Error: {str(error)}",
        )


def normalize_amount(amount_text: str) -> str:
    """
    Convert receipt amount text like 19,96 into 19.96.
    """

    return amount_text.replace(",", ".").strip()


def extract_total_amount(receipt_text: str) -> str:
    """
    Extract the real final receipt total.

    Important:
    - Do NOT choose the biggest number.
    - Do NOT use cash paid as total.
    - Prefer the first amount after the word Total/Totaal.
    - Stop before payment/change/tax sections.
    """

    text = receipt_text.replace("\r", "\n")
    lines = [line.strip() for line in text.splitlines() if line.strip()]

    stop_words = [
        "dinheiro",
        "dinh",
        "cash",
        "troco",
        "troc",
        "change",
        "taxa",
        "tax",
        "iva",
        "vat",
        "base",
        "imp",
        "val.total",
        "val.iva",
    ]

    def is_date_part(amount: str, source_text: str) -> bool:
        return bool(re.search(rf"\b{re.escape(amount)}[./-]\d{{2,4}}\b", source_text))

    def is_unit_price(amount: str, source_text: str) -> bool:
        return bool(re.search(rf"[xX]\s*{re.escape(amount)}", source_text))

    def clean_amount(amount: str) -> str:
        return normalize_amount(amount)

    # 1. Best case: line contains "Total" and amount on same line.
    for line in lines:
        lower_line = line.lower()

        if re.match(r"^total\b", lower_line) or re.match(r"^totaal\b", lower_line):
            amounts = re.findall(r"\d+[,.]\d{2}", line)

            for amount in amounts:
                if is_date_part(amount, text) or is_unit_price(amount, text):
                    continue

                try:
                    value = float(clean_amount(amount))
                    if 0.01 <= value <= 10000:
                        return f"{value:.2f}"
                except ValueError:
                    continue

    # 2. Common OCR case: "Total" is on one line and amount is on a nearby next line.
    for index, line in enumerate(lines):
        lower_line = line.lower()

        if not (re.match(r"^total\b", lower_line) or re.match(r"^totaal\b", lower_line)):
            continue

        nearby_lines = []

        for next_line in lines[index + 1 : index + 6]:
            lower_next_line = next_line.lower()

            if any(stop_word in lower_next_line for stop_word in stop_words):
                break

            nearby_lines.append(next_line)

        nearby_text = " ".join(nearby_lines)
        amounts = re.findall(r"\d+[,.]\d{2}", nearby_text)

        for amount in amounts:
            if is_date_part(amount, text) or is_unit_price(amount, text):
                continue

            try:
                value = float(clean_amount(amount))
                if 0.01 <= value <= 10000:
                    return f"{value:.2f}"
            except ValueError:
                continue

    # 3. Strong fallback: search a short text window after the word Total.
    total_match = re.search(r"\b(total|totaal)\b", text, flags=re.IGNORECASE)

    if total_match:
        after_total = text[total_match.end() : total_match.end() + 120]

        stop_positions = []

        for stop_word in stop_words:
            match = re.search(stop_word, after_total, flags=re.IGNORECASE)
            if match:
                stop_positions.append(match.start())

        if stop_positions:
            after_total = after_total[: min(stop_positions)]

        amounts = re.findall(r"\d+[,.]\d{2}", after_total)

        for amount in amounts:
            if is_date_part(amount, text) or is_unit_price(amount, text):
                continue

            try:
                value = float(clean_amount(amount))
                if 0.01 <= value <= 10000:
                    return f"{value:.2f}"
            except ValueError:
                continue

    # 4. Last fallback: use the largest amount before payment/tax section.
    cleaned_lines = []

    for line in lines:
        lower_line = line.lower()

        if any(stop_word in lower_line for stop_word in stop_words):
            break

        cleaned_lines.append(line)

    cleaned_text = "\n".join(cleaned_lines)
    amounts = re.findall(r"\d+[,.]\d{2}", cleaned_text)

    values = []

    for amount in amounts:
        if is_date_part(amount, text) or is_unit_price(amount, text):
            continue

        try:
            value = float(clean_amount(amount))
            if 0.01 <= value <= 10000:
                values.append(value)
        except ValueError:
            continue

    if values:
        return f"{max(values):.2f}"

    return "Not detected yet"


def extract_receipt_date(receipt_text: str) -> str:
    """
    Try to find a date from receipt text.
    Supports formats like 17.08.10, 17/08/2010, 2026-05-01.
    """

    date_patterns = [
        r"\b\d{1,2}[./-]\d{1,2}[./-]\d{2,4}\b",
        r"\b\d{4}[./-]\d{1,2}[./-]\d{1,2}\b",
    ]

    for pattern in date_patterns:
        match = re.search(pattern, receipt_text)

        if match:
            return match.group(0)

    return "Not detected yet"


def extract_merchant(receipt_text: str, filename: str) -> str:
    """
    Try to detect the merchant name.
    Some OCR results are imperfect, for example LIDL can become LoDL.
    """

    upper_text = receipt_text.upper()

    known_merchants = {
        "LIDL": ["LIDL", "LDL", "LODL", "L1DL", "L DL"],
        "ALDI": ["ALDI"],
        "JUMBO": ["JUMBO"],
        "ALBERT HEIJN": ["ALBERT HEIJN", "AH"],
        "PLUS": ["PLUS"],
        "SPAR": ["SPAR"],
        "KFC": ["KFC"],
        "MCDONALD": ["MCDONALD", "MCDONALDS"],
        "BURGER KING": ["BURGER KING"],
        "STARBUCKS": ["STARBUCKS"],
        "SUPERMARKET": ["SUPERMARKET"],
    }

    for merchant, variants in known_merchants.items():
        for variant in variants:
            if variant in upper_text:
                return merchant

    lines = [line.strip() for line in receipt_text.splitlines() if line.strip()]

    for line in lines[:8]:
        clean_line = re.sub(r"[^A-Za-z0-9 &.-]", "", line).strip()

        if len(clean_line) >= 3:
            return clean_line

    return filename

def detect_category(text_source: str) -> str:
    """
    Detect a simple expense category from receipt text, note, or file name.
    Groceries are checked first because supermarket receipts often contain many random OCR words.
    """

    lower_text = text_source.lower()

    if any(
        word in lower_text
        for word in [
            "lidl",
            "lodl",
            "aldi",
            "jumbo",
            "albert",
            "supermarket",
            "grocery",
            "market",
            "tomate",
            "abacaxi",
            "batata",
            "mozzarella",
            "queijo",
            "agua",
            "cornichons",
        ]
    ):
        return "Groceries"

    if any(
        word in lower_text
        for word in [
            "food",
            "restaurant",
            "cafe",
            "coffee",
            "lunch",
            "dinner",
            "mcdonald",
            "kfc",
            "burger",
        ]
    ):
        return "Food & Drinks"

    if any(
        word in lower_text
        for word in [
            "train",
            "bus",
            "uber",
            "taxi",
            "transport",
        ]
    ):
        return "Transport"

    if any(
        word in lower_text
        for word in [
            "amazon",
            "shop",
            "store",
            "clothes",
            "zara",
            "h&m",
            "nike",
        ]
    ):
        return "Shopping"

    return "Other"

@app.post("/api/ai/receipt-analysis")
async def receipt_analysis(
    file: UploadFile = File(...),
    note: str = Form(default=""),
):
    """
    Analyze an uploaded receipt file.

    This version uses OCR for image receipts and extracts basic financial data.
    """

    allowed_types = ["image/png", "image/jpeg", "image/jpg"]

    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail="Only PNG, JPG, or JPEG receipt images are supported for OCR.",
        )

    file_bytes = await file.read()
    file_size_kb = round(len(file_bytes) / 1024, 2)

    filename = file.filename or "receipt"

    receipt_text = extract_text_from_receipt_image(file_bytes)

    merchant = extract_merchant(receipt_text, filename)
    total_amount = extract_total_amount(receipt_text)
    receipt_date = extract_receipt_date(receipt_text)

    category_source = f"{filename} {note} {receipt_text}"
    category = detect_category(category_source)

    if total_amount != "Not detected yet":
        summary = (
            f"Receipt analyzed successfully. This looks like a {category} expense "
            f"from {merchant}, with a detected total of €{total_amount}."
        )
    else:
        summary = (
            f"Receipt analyzed successfully. This looks like a {category} expense "
            f"from {merchant}, but the total amount could not be detected clearly."
        )

    return {
        "feature": "Receipt Analysis",
        "status": "success",
        "fileName": filename,
        "fileType": file.content_type,
        "fileSizeKb": file_size_kb,
        "category": category,
        "summary": summary,
        "extractedData": {
            "merchant": merchant,
            "date": receipt_date,
            "totalAmount": total_amount,
            "currency": "EUR",
            "category": category,
        },
        "rawTextPreview": receipt_text[:1000],
        "nextStep": "Improve extraction with a multimodal AI model for better merchant, item, and total detection.",
    }

@app.get("/api/demo/overview")
def demo_overview():
    bunq = BunqService()

    accounts = bunq.get_accounts()
    transactions = bunq.get_transactions()

    current_balance = "0.00"
    if accounts:
        current_balance = accounts[0].get("balance", "0.00")

    sweeper = MidnightSweeper()
    sweeper_result = sweeper.analyze_liquidity(
        transactions=transactions,
        current_balance=current_balance,
    )

    habit = HabitEnforcer()
    habit_result = habit.evaluate_habit(
        goal="Make at least 3 GitHub commits today",
        proof_text="The user made 4 commits today in the Hackathon-KKM repository.",
    )

    return {
        "app": "A1 Financial Copilot",
        "status": "Backend demo is working",
        "accounts": accounts,
        "transactions": transactions,
        "tasks": load_tasks(),
        "logs": load_logs(),
        "aiFeatures": {
            "midnightSweeper": sweeper_result,
            "habitEnforcer": habit_result,
        },
    }