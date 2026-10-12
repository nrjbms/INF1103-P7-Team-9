import json
import os
import tempfile
from pathlib import Path

import dataManager


# Test the real Data Manager functions without touching meal_history.json
# The temporary folder is removed automatically when testing finishes

def run_tests():
    original_data_file = dataManager.DATA_FILE
    passed = 0

    with tempfile.TemporaryDirectory() as test_directory:
        dataManager.DATA_FILE = str(Path(test_directory) / "test_meal_history.json")

        try:
            user_input = [
                "Louise", 50.0, 2, ("None",), ("High Protein",),
                600, ("Chinese",), "Singapore", 35, 15
            ]

            meal_plan = {
                "pax": 2,
                "Total_grocery_cost": 35.50,
                "Grocery_list": [
                    {"ingredient_name": "Chicken Breast", "Quantity": "500g", "Price_per_ingredient": 8.50}
                ],
                "Dishes": [
                    {"dish_name": "Chicken Rice", "cuisine": "Chinese", "price_per_meal": 5.50}
                ]
            }

            def check(description, condition):
                nonlocal passed
                assert condition, f"FAIL: {description}"
                passed += 1
                print(f"PASS {passed}: {description}")

            # Test 1: Missing file should be treated as empty history
            check("Missing JSON file", dataManager.load_records() == [])

            # Test 2: Saving should create a real JSON file
            saved = dataManager.save_record(user_input, meal_plan)
            check("Save creates JSON file", saved is True and os.path.isfile(dataManager.DATA_FILE))

            # Test 3: Saved JSON contains expected user and nutrition data
            with open(dataManager.DATA_FILE, "r", encoding="utf-8") as file:
                disk_records = json.load(file)
            check(
                "JSON content and nutrition fields",
                len(disk_records) == 1
                and disk_records[0]["name"] == "Louise"
                and disk_records[0]["protein_count"] == 35
                and disk_records[0]["fat_count"] == 15
            )

            # Test 4: Saving another plan should preserve the first
            second_input = user_input.copy()
            second_input[0] = "Felix"
            second_plan = meal_plan.copy()
            second_plan["Total_grocery_cost"] = 55.0
            second_plan["Dishes"] = [{"dish_name": "Pasta"}]
            second_plan["Grocery_list"] = [{"ingredient_name": "Pasta"}]
            second_saved = dataManager.save_record(second_input, second_plan)
            records = dataManager.load_records()
            check(
                "Second save preserves previous records",
                second_saved is True
                and len(records) == 2
                and records[0]["id"] != records[1]["id"]
            )

            # Test 5: Records can be retrieved by ID
            first_id = records[0]["id"]
            second_id = records[1]["id"]
            check(
                "Retrieve record by ID",
                dataManager.get_record_by_id(first_id)["name"] == "Louise"
                and dataManager.get_record_by_id(99999) is None
            )

            # Test 6: Case-insensitive name filtering
            check(
                "Filter by name",
                len(dataManager.filter_by_name("LOUISE")) == 1
                and dataManager.filter_by_name("LOUISE")[0]["id"] == first_id
            )

            # Test 7: Budget filter uses actual grocery cost
            budget_results = dataManager.filter_by_budget(40)
            check(
                "Filter by grocery budget",
                len(budget_results) == 1 and budget_results[0]["id"] == first_id
            )

            # Test 8: Search finds nested ingredient text
            search_results = dataManager.search_records("chicken")
            check(
                "Search by keyword",
                len(search_results) == 1 and search_results[0]["id"] == first_id
            )

            # Test 9: Rename persists to disk
            renamed = dataManager.update_meal_plan_name(first_id, "Louise Updated")
            check(
                "Rename saved plan",
                renamed is True
                and dataManager.get_record_by_id(first_id)["name"] == "Louise Updated"
            )

            # Test 10: Delete persists to disk
            deleted = dataManager.delete_meal_plan(second_id)
            check(
                "Delete saved plan",
                deleted is True
                and dataManager.get_record_by_id(second_id) is None
                and len(dataManager.load_records()) == 1
            )

            # Test 11: Invalid name is rejected
            bad_input = user_input.copy()
            bad_input[0] = "  "
            check("Reject empty name", dataManager.save_record(bad_input, meal_plan) is False)

            # Test 12: Invalid budget is rejected
            bad_input = user_input.copy()
            bad_input[1] = -10
            check("Reject negative budget", dataManager.save_record(bad_input, meal_plan) is False)

            # Test 13: Invalid pax is rejected
            bad_input = user_input.copy()
            bad_input[2] = 0
            check("Reject zero pax", dataManager.save_record(bad_input, meal_plan) is False)

            # Test 14: Invalid grocery cost is rejected
            bad_plan = meal_plan.copy()
            bad_plan["Total_grocery_cost"] = -5
            check("Reject negative grocery cost", dataManager.save_record(user_input, bad_plan) is False)

            # Test 15: Required grocery list must exist
            bad_plan = meal_plan.copy()
            bad_plan.pop("Grocery_list")
            check("Reject missing grocery list", dataManager.save_record(user_input, bad_plan) is False)

            # Test 16: Required dishes must exist
            bad_plan = meal_plan.copy()
            bad_plan.pop("Dishes")
            check("Reject missing dishes", dataManager.save_record(user_input, bad_plan) is False)

            # Test 17: Invalid budget filter should return no matches
            check(
                "Reject invalid budget filters",
                dataManager.filter_by_budget(-10) == []
                and dataManager.filter_by_budget("abc") == []
            )

            # Test 18: Empty rename is rejected
            check(
                "Reject invalid rename",
                dataManager.update_meal_plan_name(first_id, " ") is False
            )

            # Test 19: A successful save should not leave temporary files
            leftover_temp_files = list(Path(test_directory).glob(".meal_history_*.tmp"))
            check("No leftover temporary files", len(leftover_temp_files) == 0)

            # Test 20: Corrupted JSON should not be overwritten
            with open(dataManager.DATA_FILE, "w", encoding="utf-8") as file:
                file.write("INVALID JSON")

            corrupted_detected = dataManager.load_records() is None
            rejected_save = dataManager.save_record(user_input, meal_plan) is False
            with open(dataManager.DATA_FILE, "r", encoding="utf-8") as file:
                original_content_preserved = file.read() == "INVALID JSON"

            check(
                "Corrupted JSON detected and preserved",
                corrupted_detected and rejected_save and original_content_preserved
            )

            print(f"\nALL {passed} DATA MANAGER TESTS PASSED!")
            print("Your actual meal_history.json was not modified.")

        finally:
            dataManager.DATA_FILE = original_data_file


if __name__ == "__main__":
    run_tests()
