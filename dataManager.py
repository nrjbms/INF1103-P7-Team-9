import json
import os
from datetime import datetime


DATA_FILE = "meal_history.json"


def load_records():
    """
    Load all saved meal plans from meal_history.json.

    Returns an empty list if:
    - the file does not exist
    - the file is empty
    - the JSON is corrupted
    - the stored data is not a list
    """

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
    """
    Generate a unique ID for a new meal plan.
    """

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
    """
    Save an accepted meal plan.

    Felix's user_input list:
    [0] name
    [1] budget
    [2] pax
    [3] dietary restrictions
    [4] dietary goal
    [5] calorie count
    [6] cuisine
    [7] country
    """

    # Basic validation
    if not isinstance(user_input, (list, tuple)):
        return False

    if len(user_input) < 8:
        return False

    if not isinstance(meal_plan, dict):
        return False

    records = load_records()

    # Copy meal plan so original data is not modified
    record = meal_plan.copy()

    # Add Data Manager fields
    record["id"] = generate_id(records)
    record["name"] = user_input[0]
    record["budget"] = user_input[1]
    record["pax"] = user_input[2]
    record["date"] = datetime.now().strftime("%Y-%m-%d")

    records.append(record)

    try:
        with open(DATA_FILE, "w", encoding="utf-8") as file:
            json.dump(
                records,
                file,
                indent=4,
                ensure_ascii=False
            )

        return True

    except (OSError, TypeError):
        return False


def get_all_records():
    """
    Return all saved meal plans.
    """

    return load_records()


def get_record_by_id(record_id):
    """
    Find one saved meal plan using its ID.
    """

    records = load_records()

    for record in records:
        if record.get("id") == record_id:
            return record

    return None


def search_records(search_word):
    """
    Search saved meal plans using a keyword.

    Can match:
    - name
    - cuisine
    - ingredients
    - dish names
    - other saved information
    """

    records = load_records()

    search_word = str(search_word).strip().lower()

    if search_word == "":
        return []

    results = []

    for record in records:
        record_text = json.dumps(
            record,
            ensure_ascii=False
        ).lower()

        if search_word in record_text:
            results.append(record)

    return results


def filter_by_budget(max_budget):
    """
    Return meal plans where the total grocery cost
    is within the given budget.
    """

    records = load_records()
    results = []

    try:
        max_budget = float(max_budget)
    except (ValueError, TypeError):
        return []

    for record in records:
        cost = record.get("Total_grocery_cost")

        if isinstance(cost, (int, float)):
            if cost <= max_budget:
                results.append(record)

    return results


def filter_by_name(name):
    """
    Return all meal plans saved under a user's name.
    """

    records = load_records()
    results = []

    name = str(name).strip().lower()

    if name == "":
        return []

    for record in records:
        saved_name = str(record.get("name", "")).strip().lower()

        if saved_name == name:
            results.append(record)

    return results
