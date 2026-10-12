import json
import os
import tempfile
from datetime import datetime


DATA_FILE = "meal_history.json"


# Load saved meal plans from the JSON file.
# A missing file is treated as an empty history.
# A corrupted or incorrectly structured file raises ValueError,
# allowing callers to avoid overwriting existing data.
def load_records():
    if not os.path.exists(DATA_FILE):
        return []

    try:
        with open(DATA_FILE, "r", encoding="utf-8") as file:
            records = json.load(file)
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise ValueError("Cannot read meal history file.") from error

    if not isinstance(records, list) or not all(isinstance(item, dict) for item in records):
        raise ValueError("Meal history must contain a list of records.")

    return records


# Save all records safely using a temporary file.
# Replacing the file only after writing succeeds helps protect existing data.
def save_records(records):
    if not isinstance(records, list) or not all(isinstance(item, dict) for item in records):
        return False

    temporary_path = None
    directory = os.path.dirname(os.path.abspath(DATA_FILE))

    try:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", dir=directory,
            prefix=".meal_history_", suffix=".tmp", delete=False
        ) as file:
            temporary_path = file.name
            json.dump(records, file, indent=4, ensure_ascii=False, allow_nan=False)

        os.replace(temporary_path, DATA_FILE)
        return True
    except (OSError, TypeError, ValueError, UnicodeError):
        return False
    finally:
        if temporary_path and os.path.exists(temporary_path):
            try:
                os.remove(temporary_path)
            except OSError:
                pass


# Generate the next available ID based on saved records.
# IDs are unique among existing records; a deleted highest ID may be reused.
def generate_id(records):
    existing_ids = [
        record["id"]
        for record in records
        if isinstance(record, dict)
        and type(record.get("id")) is int
        and record["id"] > 0
    ]
    return max(existing_ids, default=0) + 1


# Save an accepted meal plan.
# Felix's user_input order:
# [0] name, [1] budget, [2] pax, [3] dietary restrictions,
# [4] dietary goal, [5] calorie count, [6] cuisine,
# [7] country, [8] protein count, [9] fat count.
def save_record(user_input, meal_plan):
    if not isinstance(user_input, (list, tuple)) or len(user_input) < 10:
        return False

    if not isinstance(meal_plan, dict):
        return False

    name = user_input[0]
    if not isinstance(name, str) or not name.strip():
        return False

    try:
        budget = float(user_input[1])
        pax = int(user_input[2])
    except (ValueError, TypeError, OverflowError):
        return False

    if not (0 <= budget < float("inf")) or pax <= 0:
        return False

    try:
        records = load_records()
    except ValueError:
        return False

    record = meal_plan.copy()
    record["id"] = generate_id(records)
    record["name"] = name.strip()
    record["budget"] = budget
    record["pax"] = pax
    record["dietary_restrictions"] = user_input[3]
    record["dietary_goal"] = user_input[4]
    record["calorie_count"] = user_input[5]
    record["cuisine"] = user_input[6]
    record["country"] = user_input[7]
    record["protein_count"] = user_input[8]
    record["fat_count"] = user_input[9]
    record["date"] = datetime.now().strftime("%Y-%m-%d")

    records.append(record)
    return save_records(records)


# Return all saved meal plans, or an empty list when loading fails.
def get_all_records():
    try:
        return load_records()
    except ValueError:
        return []


# Retrieve one saved plan by its numeric ID.
def get_record_by_id(record_id):
    try:
        record_id = int(record_id)
    except (ValueError, TypeError, OverflowError):
        return None

    for record in get_all_records():
        if record.get("id") == record_id:
            return record
    return None


# Search all saved record fields for a keyword, ignoring case.
def search_records(search_word):
    if search_word is None:
        return []

    keyword = str(search_word).strip().lower()
    if not keyword:
        return []

    results = []
    for record in get_all_records():
        record_text = json.dumps(record, ensure_ascii=False).lower()
        if keyword in record_text:
            results.append(record)
    return results


# Return meal plans with grocery costs at or below the chosen amount.
def filter_by_budget(max_budget):
    try:
        max_budget = float(max_budget)
    except (ValueError, TypeError, OverflowError):
        return []

    if not (0 <= max_budget < float("inf")):
        return []

    results = []
    for record in get_all_records():
        cost = record.get("Total_grocery_cost")
        if isinstance(cost, (int, float)) and not isinstance(cost, bool):
            if 0 <= cost <= max_budget:
                results.append(record)
    return results


# Filter saved plans by an exact name, ignoring case and spaces.
def filter_by_name(name):
    if name is None:
        return []

    name = str(name).strip().lower()
    if not name:
        return []

    return [
        record for record in get_all_records()
        if str(record.get("name", "")).strip().lower() == name
    ]


# Jannah's update and delete functions, refactored to reuse save_records().
# Update only the saved plan's name, not its recipes or preferences.
def update_meal_plan_name(plan_id, new_name):
    if not isinstance(new_name, str) or not new_name.strip():
        return False

    try:
        records = load_records()
    except ValueError:
        return False

    for plan in records:
        if str(plan.get("id")) == str(plan_id):
            plan["name"] = new_name.strip()
            return save_records(records)
    return False


# Delete a saved plan by ID, keeping all other plans unchanged.
def delete_meal_plan(plan_id):
    try:
        records = load_records()
    except ValueError:
        return False

    for index, plan in enumerate(records):
        if str(plan.get("id")) == str(plan_id):
            records.pop(index)
            return save_records(records)
    return False
