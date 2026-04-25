from server.agents.plannerAgent import PlannerAgent
from server.chat.conversationStore import save_message, get_conversation
from server.automation.taskStore import save_task, update_task_status, get_tasks_for_user

class ChatOrchestrator:
    def __init__(self):
        self.planner = PlannerAgent()

    def handle_message(self, user_id: str, message: str):
        save_message(user_id, "user", message)
        conversation = get_conversation(user_id)

        lowered = message.lower().strip()
        if lowered in ["yes", "confirm", "تایید", "بله"]:
            tasks = get_tasks_for_user(user_id)
            draft_tasks = [t for t in tasks if t["status"] == "draft"]
            if draft_tasks:
                latest = draft_tasks[-1]
                update_task_status(latest["id"], "active")
                reply = "ایول سید! اتوماسیون با موفقیت فعال شد. از این به بعد حواسم هست. ✅"
                save_message(user_id, "assistant", reply)
                return {"reply": reply, "activatedTask": latest}

        plan = self.planner.create_plan(message, conversation)
        
        draft_task = None
        if plan.get("createsTask"):
            status = "draft" if plan.get("requiresConfirmation") else "active"
            draft_task = save_task(user_id, plan.get("task", {}), status)
            
            if status == "draft":
                plan["reply"] += "\n\nسید، اگه اوکی هستی بگو 'تایید' تا این اتوماسیون رو برات فعال کنم. 🚀"

        save_message(user_id, "assistant", plan.get("reply"))

        return {
            "reply": plan.get("reply"),
            "intent": plan.get("intent"),
            "draftTask": draft_task
        }