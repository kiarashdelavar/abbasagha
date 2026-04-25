import json
import os
from datetime import datetime

CONVERSATION_FILE = os.path.join(os.path.dirname(__file__), "conversations.json")


def load_conversations():
    if not os.path.exists(CONVERSATION_FILE):
        return {}

    with open(CONVERSATION_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def save_message(user_id: str, role: str, message: str):
    conversations = load_conversations()

    if user_id not in conversations:
        conversations[user_id] = []

    item = {
        "timestamp": datetime.utcnow().isoformat(),
        "role": role,
        "message": message,
    }

    conversations[user_id].append(item)

    with open(CONVERSATION_FILE, "w", encoding="utf-8") as file:
        json.dump(conversations, file, indent=2)

    return item


def get_conversation(user_id: str):
    conversations = load_conversations()
    return conversations.get(user_id, [])