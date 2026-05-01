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

@app.post("/api/ai/receipt-analysis")
async def receipt_analysis(
    file: UploadFile = File(...),
    note: str = Form(default=""),
):
    """
    Analyze an uploaded receipt file.

    This is the first MVP version for the multimodal receipt feature.
    Later this can be connected to a real vision model/OCR service.
    """

    allowed_types = ["image/png", "image/jpeg", "image/jpg", "application/pdf"]

    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail="Only PNG, JPG, JPEG, or PDF receipts are supported.",
        )

    file_bytes = await file.read()
    file_size_kb = round(len(file_bytes) / 1024, 2)

    filename = file.filename or "receipt"

    lower_name = filename.lower()
    lower_note = note.lower()

    category = "Other"

    if any(word in lower_name or word in lower_note for word in ["food", "restaurant", "cafe", "coffee", "lunch", "dinner"]):
        category = "Food & Drinks"
    elif any(word in lower_name or word in lower_note for word in ["train", "bus", "uber", "taxi", "transport"]):
        category = "Transport"
    elif any(word in lower_name or word in lower_note for word in ["market", "grocery", "albert", "jumbo", "aldi", "lidl"]):
        category = "Groceries"
    elif any(word in lower_name or word in lower_note for word in ["amazon", "shop", "store", "clothes"]):
        category = "Shopping"

    return {
        "feature": "Receipt Analysis",
        "status": "success",
        "fileName": filename,
        "fileType": file.content_type,
        "fileSizeKb": file_size_kb,
        "category": category,
        "summary": f"Receipt uploaded successfully. Based on the file name and note, this looks like a {category} expense.",
        "extractedData": {
            "merchant": "Not detected yet",
            "date": "Not detected yet",
            "totalAmount": "Not detected yet",
            "currency": "EUR",
            "category": category,
        },
        "nextStep": "Connect this endpoint to OCR or a multimodal AI model to extract merchant, date, and total amount from the image.",
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