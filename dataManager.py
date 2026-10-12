
import json
import os
from datetime import datetime


DATA_FILE = "meal_history.json"


# Load all saved meal plans from meal_history.json
# Return an empty list if the file does not exist,
# is empty, corrupted, or does not contain a list
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


# Generate a unique ID for each new meal plan
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


# Save an accepted meal plan into meal_history.json
# Felix's updated user_input list:
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

    # Validate user input and meal plan
    if not isinstance(user_input, (list, tuple)):
        return False

    if len(user_input) < 10:
        return False

    if not isinstance(meal_plan, dict):
        return False

    records = load_records()

    # Copy the accepted meal plan
    record = meal_plan.copy()

    # Add user information and nutritional targets
    record["id"] = generate_id(records)
    record["name"] = user_input[0]
    record["budget"] = user_input[1]
    record["pax"] = user_input[2]
    record["dietary_restrictions"] = user_input[3]
    record["dietary_goal"] = user_input[4]
    record["calorie_count"] = user_input[5]
    record["cuisine"] = user_input[6]
    record["country"] = user_input[7]
    record["protein_count"] = user_input[8]
    record["fat_count"] = user_input[9]
    record["date"] = datetime.now().strftime("%Y-%m-%d")

    records.append(record)

    # Save all records to JSON
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


# Return all saved meal plans
def get_all_records():

    return load_records()


# Retrieve a saved meal plan using its ID
# Return None if the ID does not exist
def get_record_by_id(record_id):

    records = load_records()

    for record in records:
        if record.get("id") == record_id:
            return record

    return None


# Search saved meal plans using a keyword
# Search includes names, cuisines, ingredients,
# dish names, and other saved information
def search_records(search_word):

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


# Filter saved meal plans by maximum grocery cost
# Return plans with a total cost within the given budget
def filter_by_budget(max_budget):

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


# Filter saved meal plans by user name
# Name matching is not case-sensitive
def filter_by_name(name):

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


# Nur Jannah's Code for Update and Delete Functions

# Update the name of a saved meal plan using its ID
def update_meal_plan_name(plan_id, new_name):

    records = load_records()

    for plan in records:
        if str(plan.get("id")) == str(plan_id):
            plan["name"] = new_name

            with open(DATA_FILE, "w") as file:
                json.dump(records, file, indent=4)

            print("Meal plan name updated successfully!")
            return True

    print("Meal plan not found.")
    return False


# Delete a saved meal plan using its ID
def delete_meal_plan(plan_id):

    records = load_records()

    for plan in records:
        if str(plan.get("id")) == str(plan_id):
            records.remove(plan)

            with open(DATA_FILE, "w") as file:
                json.dump(records, file, indent=4)

            print("\nMeal plan deleted successfully!")
            return True

    print("\nMeal plan not found.")
    return False
