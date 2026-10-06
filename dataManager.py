import json
import os
from datetime import datetime


DATA_FILE = "meal_history.json"


def load_records():
    if not os.path.exists(DATA_FILE):
        return []

    try:
        with open(DATA_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)

        if isinstance(data, list):
            return data

        return []

    except (json.JSONDecodeError, OSError):
        return []


def generate_id(records):
    if not records:
        return 1

    existing_ids = []

    for record in records:
        record_id = record.get("id")

        if isinstance(record_id, int):
            existing_ids.append(record_id)

    if not existing_ids:
        return 1

    return max(existing_ids) + 1


def save_record(user_input, meal_plan):
    if not isinstance(user_input, (list, tuple)):
        return False

    if len(user_input) < 8:
        return False

    if not isinstance(meal_plan, dict):
        return False

    records = load_records()

    record = meal_plan.copy()

    record["id"] = generate_id(records)
    record["name"] = user_input[0]
    record["budget"] = user_input[1]
    record["pax"] = user_input[2]
    record["date"] = datetime.now().strftime("%Y-%m-%d")

    records.append(record)

    try:
        with open(DATA_FILE, "w", encoding="utf-8") as file:
            json.dump(records, file, indent=4, ensure_ascii=False)

        return True

    except (OSError, TypeError):
        return False
