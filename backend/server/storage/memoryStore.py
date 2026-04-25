import json
import os
from datetime import datetime

LOG_FILE = os.path.join(os.path.dirname(__file__), "logs.json")


def load_logs():
    if not os.path.exists(LOG_FILE):
        return []

    with open(LOG_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def save_log(action_type, data):
    logs = load_logs()

    log_item = {
        "timestamp": datetime.utcnow().isoformat(),
        "actionType": action_type,
        "data": data,
    }

    logs.append(log_item)

    with open(LOG_FILE, "w", encoding="utf-8") as file:
        json.dump(logs, file, indent=2)

    return log_item