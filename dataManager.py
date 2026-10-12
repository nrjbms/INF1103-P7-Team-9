
import json
import os
import math
import tempfile
from datetime import datetime


DATA_FILE = "meal_history.json"


# Load saved meal plans from JSON
# Return [] if the file does not exist
# Return None if the file is corrupted or unreadable
def load_records():

    if not os.path.exists(DATA_FILE):
        return []

    try:
        with open(DATA_FILE, "r", encoding="utf-8") as file:
            records = json.load(file)

        if not isinstance(records, list):
            return None

        # Check that all saved records are dictionaries
        for record in records:
            if not isinstance(record, dict):
                return None

        return records

    except (json.JSONDecodeError, OSError, UnicodeError):
        return None


# Save all records safely to JSON
# Write to a temporary file before replacing the original
def save_records(records):

    if not isinstance(records, list):
        return False

    for record in records:
        if not isinstance(record, dict):
            return False

    temp_path = None

    try:
        # Check that all data can be converted to JSON
        json.dumps(records, allow_nan=False)

        # Save temporary file in the same directory
        directory = os.path.dirname(
            os.path.abspath(DATA_FILE)
        )

        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=directory,
            prefix=".meal_history_",
            suffix=".tmp",
            delete=False
        ) as file:

            temp_path = file.name

            json.dump(
                records,
                file,
                indent=4,
                ensure_ascii=False,
                allow_nan=False
            )

        # Replace the original only after writing succeeds
        os.replace(temp_path, DATA_FILE)

        return True

    except (OSError, TypeError, ValueError):
        return False

    finally:
        # Remove temporary file if saving failed
        if temp_path is not None and os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except OSError:
                pass


# Generate a unique ID based on existing saved records
def generate_id(records):

    existing_ids = []

    for record in records:

        if not isinstance(record, dict):
            continue

        record_id = record.get("id")

        if type(record_id) is int and record_id > 0:
            existing_ids.append(record_id)

    if not existing_ids:
        return 1

    return max(existing_ids) + 1


# Validate numeric values such as budgets and grocery costs
def is_valid_amount(value):

    if isinstance(value, bool):
        return False

    try:
        amount = float(value)

    except (TypeError, ValueError, OverflowError):
        return False

    return math.isfinite(amount) and amount >= 0


# Save an accepted meal plan into meal_history.json
# Felix's user_input structure:
# [0] name
# [1] budget
# [2] pax
# [3] dietary restrictions
# [4] dietary goal
# [5] calorie count
# [6] cuisine
# [7] country
# [8] protein count
# [9] fat count
def save_record(user_input, meal_plan):

    # Validate input structure
    if not isinstance(user_input, (list, tuple)):
        return False

    if len(user_input) < 10:
        return False

    if not isinstance(meal_plan, dict):
        return False

    # Validate user name
    name = user_input[0]

    if not isinstance(name, str) or not name.strip():
        return False

    # Validate user budget
    if not is_valid_amount(user_input[1]):
        return False

    # Validate number of people
    pax = user_input[2]

    if type(pax) is not int or pax <= 0:
        return False

    # Validate total grocery cost
    grocery_cost = meal_plan.get("Total_grocery_cost")

    if not is_valid_amount(grocery_cost):
        return False

    # Validate grocery list and dishes
    grocery_list = meal_plan.get("Grocery_list")
    dishes = meal_plan.get("Dishes")

    if not isinstance(grocery_list, list):
        return False

    if not isinstance(dishes, list):
        return False

    # Check that JSON file is safe to read
    records = load_records()

    if records is None:
        return False

    # Copy the meal plan to avoid modifying original data
    record = meal_plan.copy()

    # Add unique ID and user information
    record["id"] = generate_id(records)
    record["name"] = name.strip()
    record["budget"] = float(user_input[1])
    record["pax"] = pax
    record["dietary_restrictions"] = user_input[3]
    record["dietary_goal"] = user_input[4]
    record["calorie_count"] = user_input[5]
    record["cuisine"] = user_input[6]
    record["country"] = user_input[7]
    record["protein_count"] = user_input[8]
    record["fat_count"] = user_input[9]
    record["date"] = datetime.now().strftime("%Y-%m-%d")

    # Add the new meal plan
    records.append(record)

    # Save all records safely
    return save_records(records)


# Return all saved meal plans
# Return [] if the file cannot be loaded
def get_all_records():

    records = load_records()

    if records is None:
        return []

    return records


# Retrieve a saved meal plan using its ID
# Return None if the ID does not exist
def get_record_by_id(record_id):

    records = load_records()

    if records is None:
        return None

    for record in records:

        if str(record.get("id")) == str(record_id):
            return record

    return None


# Search saved meal plans using a keyword
# Search across all saved record information
def search_records(search_word):

    records = load_records()

    if records is None:
        return []

    if search_word is None:
        return []

    search_word = str(search_word).strip().lower()

    if not search_word:
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


# Filter saved meal plans by maximum grocery cost
# Return plans with a total cost within the given budget
def filter_by_budget(max_budget):

    records = load_records()

    if records is None:
        return []

    if not is_valid_amount(max_budget):
        return []

    max_budget = float(max_budget)

    results = []

    for record in records:

        cost = record.get("Total_grocery_cost")

        if is_valid_amount(cost):

            if float(cost) <= max_budget:
                results.append(record)

    return results


# Filter saved meal plans by user name
# Matching is case-insensitive
def filter_by_name(name):

    records = load_records()

    if records is None:
        return []

    if name is None:
        return []

    name = str(name).strip().lower()

    if not name:
        return []

    results = []

    for record in records:

        saved_name = str(
            record.get("name", "")
        ).strip().lower()

        if saved_name == name:
            results.append(record)

    return results


# Nur Jannah's Update and Delete Functions
# Refactored to use the shared save_records function


# Update the name of a saved meal plan using its ID
def update_meal_plan_name(plan_id, new_name):

    # Validate new name
    if not isinstance(new_name, str):
        return False

    if not new_name.strip():
        return False

    # Load existing records
    records = load_records()

    if records is None:
        return False

    # Find and update matching record
    for plan in records:

        if str(plan.get("id")) == str(plan_id):

            plan["name"] = new_name.strip()

            return save_records(records)

    return False


# Delete a saved meal plan using its ID
def delete_meal_plan(plan_id):

    # Load existing records
    records = load_records()

    if records is None:
        return False

    # Find and delete matching record
    for plan in records:

        if str(plan.get("id")) == str(plan_id):

            records.remove(plan)

            return save_records(records)

    return False
