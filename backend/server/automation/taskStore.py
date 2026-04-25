import json
import os
import uuid
from datetime import datetime

TASK_FILE = os.path.join(os.path.dirname(__file__), "tasks.json")


def load_tasks():
    if not os.path.exists(TASK_FILE):
        return []

    with open(TASK_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def save_task(user_id: str, task_data: dict, status: str = "draft"):
    tasks = load_tasks()

    task = {
        "id": str(uuid.uuid4()),
        "userId": user_id,
        "status": status,
        "createdAt": datetime.utcnow().isoformat(),
        "task": task_data,
    }

    tasks.append(task)

    with open(TASK_FILE, "w", encoding="utf-8") as file:
        json.dump(tasks, file, indent=2)

    return task


def update_task_status(task_id: str, status: str):
    tasks = load_tasks()
    updated_task = None

    for task in tasks:
        if task["id"] == task_id:
            task["status"] = status
            task["updatedAt"] = datetime.utcnow().isoformat()
            updated_task = task

    with open(TASK_FILE, "w", encoding="utf-8") as file:
        json.dump(tasks, file, indent=2)

    return updated_task


def get_tasks_for_user(user_id: str):
    return [task for task in load_tasks() if task["userId"] == user_id]