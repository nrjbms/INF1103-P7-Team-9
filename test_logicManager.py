# Automated tests for logicManager.py - Brandon
# Every test runs the logic manager on the sample AI response in sampleoutput.json
# Checks that each decision follows the business rule
# No live API call, no API key and no .env file needed.

import json
import sys

import logicManager

SAMPLE_FILE = "sampleoutput.json"

# Load a fresh copy of the sample AI response, so one test can't change another test's data
def sample():
    try:
        with open(SAMPLE_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    except (OSError, json.JSONDecodeError) as error:
        print(f"Cannot load {SAMPLE_FILE}. Run this test from the project folder,")
        print(f"and make sure {SAMPLE_FILE} is valid JSON. ({error})")
        sys.exit(1)

# User input list in the same order inputManager.main_input() builds it
def user(budget=50.0, 
         pax=1, 
         restrictions=("None",), 
         goal=("Standard",),
         calories=650, 
         cuisine=("Anything",), 
         protein=27, 
         fat=20):
    return ["Tester", budget, pax, restrictions, goal, calories, cuisine, "Singapore", protein, fat]

# Nutrition values of a dish as numbers, e.g. "540 kcal" -> 540.0
def calories_of(dish):
    return logicManager.parse_number(dish["calorie_count_per_meal_output"])

def protein_of(dish):
    return logicManager.parse_number(dish["protein_count_per_meal_output"])

def fat_of(dish):
    return logicManager.parse_number(dish["fats_count_per_meal"])

# The dishes a filter removed (the sample dishes that are not in its kept list)
def removed_dishes(all_dishes, result):
    kept_names = []
    for dish in result["valid_dishes"]:
        kept_names.append(dish["dish_name"])

    removed = []
    for dish in all_dishes:
        if dish["dish_name"] not in kept_names:
            removed.append(dish)
    return removed

# Fail with a clear message if a condition is not true
def check(condition, message):
    if not condition:
        raise AssertionError(message)

# ---- Reading numbers and the budget rule ----
def test_parse_number_reads_every_dish():
    for dish in sample()["Dishes"]:
        text = dish["calorie_count_per_meal_output"]          # e.g. "540 kcal"
        expected = float(text.replace("kcal", "").strip())
        check(logicManager.parse_number(text) == expected,
              f"parse_number({text!r}) gave {logicManager.parse_number(text)}, expected {expected}")

def test_budget_rule():
    cost = sample()["Total_grocery_cost"]
    status = logicManager.check_budget_compliance(cost, cost)["status"]
    check(status == "ACCEPTED", f"Cost ${cost} with a budget of exactly ${cost} gave {status}")
    status = logicManager.check_budget_compliance(cost, cost - 1)["status"]
    check(status == "REJECTED", f"Cost ${cost} with a budget of ${cost - 1:.2f} gave {status}")
    status = logicManager.check_budget_compliance(cost, float("nan"))["status"]
    check(status == "ERROR", f"Budget 'nan' gave {status}")

def test_custom_macros_reasonability_check():
    ok, message = logicManager.check_macro_targets(600, 30, 15)   # 120 + 135 = 255 kcal
    check(ok, "600 kcal / 30 g protein / 15 g fat should be possible")
    ok, message = logicManager.check_macro_targets(350, 60, 30)   # 240 + 270 = 510 kcal
    check(not ok, "350 kcal / 60 g protein / 30 g fat should be impossible")


# ---- Dietary filter ----
def test_halal_rule():
    dishes = sample()["Dishes"]
    result = logicManager.filter_dishes_by_dietary_rules(dishes, ("Halal",))
    for dish in result["valid_dishes"]:
        text = (dish["dish_name"] + " " + dish["ingredients"]).lower()
        check("pork" not in text, f"Halal kept '{dish['dish_name']}', which contains pork")
    for dish in removed_dishes(dishes, result):
        text = (dish["dish_name"] + " " + dish["ingredients"]).lower()
        check("pork" in text, f"Halal removed '{dish['dish_name']}', which has no pork")

def test_eggs_rule():
    dishes = sample()["Dishes"]
    result = logicManager.filter_dishes_by_dietary_rules(dishes, ("Eggs",))
    for dish in result["valid_dishes"]:
        words = logicManager.split_into_words(dish["dish_name"] + " " + dish["ingredients"])
        check("egg" not in words and "eggs" not in words,
              f"Eggs kept '{dish['dish_name']}', which contains egg")
    for dish in removed_dishes(dishes, result):
        words = logicManager.split_into_words(dish["dish_name"] + " " + dish["ingredients"])
        check("egg" in words or "eggs" in words, f"Eggs removed '{dish['dish_name']}', which has no egg")

def test_every_removed_dish_has_a_reason():
    dishes = sample()["Dishes"]
    result = logicManager.filter_dishes_by_dietary_rules(dishes, ("Halal", "Eggs", "Wheat"))
    check(len(result["flagged_dishes"]) == len(removed_dishes(dishes, result)),
          f"{len(removed_dishes(dishes, result))} dishes removed but "
          f"{len(result['flagged_dishes'])} reasons given")

# ---- Nutrition goals (multi-condition rule) ----
def test_standard_goal_keeps_every_dish():
    dishes = sample()["Dishes"]
    result = logicManager.filter_dishes_by_nutrition(dishes, "Standard", 650, 27, 20)
    check(len(result["valid_dishes"]) == len(dishes),
          f"Standard kept {len(result['valid_dishes'])} of {len(dishes)} dishes; it has no limits")

def test_low_calories_rule():
    dishes = sample()["Dishes"]
    cap = 500 * 1.1 # 500 kcal + 10% leeway
    result = logicManager.filter_dishes_by_nutrition(dishes, "Low Calories", 500, 22, 15)
    for dish in result["valid_dishes"]:
        check(calories_of(dish) <= cap, f"Low Calories kept '{dish['dish_name']}' at {calories_of(dish)} kcal (cap {cap:.0f})")
    for dish in removed_dishes(dishes, result):
        check(calories_of(dish) > cap, f"Low Calories removed '{dish['dish_name']}' at {calories_of(dish)} kcal (cap {cap:.0f})")

def test_high_protein_rule():
    dishes = sample()["Dishes"]
    minimum = 35 * 0.9 # 35 g - 10% leeway
    result = logicManager.filter_dishes_by_nutrition(dishes, "High Protein", 800, 35, 25)
    for dish in result["valid_dishes"]:
        share = protein_of(dish) * 4 / calories_of(dish)
        check(protein_of(dish) >= minimum and share >= 0.25,
              f"High Protein kept '{dish['dish_name']}' ({protein_of(dish)} g, {share:.0%} of calories)")
    for dish in removed_dishes(dishes, result):
        share = protein_of(dish) * 4 / calories_of(dish)
        check(protein_of(dish) < minimum or share < 0.25,
              f"High Protein removed '{dish['dish_name']}' ({protein_of(dish)} g, {share:.0%} of calories)")

def test_custom_macros_rule():
    dishes = sample()["Dishes"]
    max_cal, min_protein, max_fat = 600 * 1.1, 30 * 0.9, 15 * 1.1
    result = logicManager.filter_dishes_by_nutrition(dishes, "Custom Macros", 600, 30, 15)
    for dish in result["valid_dishes"]:
        check(calories_of(dish) <= max_cal and protein_of(dish) >= min_protein and fat_of(dish) <= max_fat,
              f"Custom Macros kept '{dish['dish_name']}', which misses a target")
    for dish in removed_dishes(dishes, result):
        check(calories_of(dish) > max_cal or protein_of(dish) < min_protein or fat_of(dish) > max_fat,
              f"Custom Macros removed '{dish['dish_name']}', which meets every target")

# ---- Cuisine and grocery list ----
def test_cuisine_rule():
    dishes = sample()["Dishes"]
    cuisine = dishes[0]["cuisine"]  # a cuisine that exists in the sample
    result = logicManager.filter_dishes_by_cuisine(dishes, (cuisine,))
    for dish in result["valid_dishes"]:
        check(dish["cuisine"] == cuisine, f"Picked {cuisine} but kept '{dish['dish_name']}' ({dish['cuisine']})")
    for dish in removed_dishes(dishes, result):
        check(dish["cuisine"] != cuisine, f"Picked {cuisine} but removed '{dish['dish_name']}' ({dish['cuisine']})")

def test_grocery_list_cost_matches_kept_items():
    response = sample()
    result = logicManager.filter_grocery_list(response["Grocery_list"], [response["Dishes"][0]])
    total = 0.0
    for item in result["grocery_list"]:
        total = total + item["Price_per_ingredient"]
    check(result["total_cost"] == round(total, 2),
          f"Grocery cost is {result['total_cost']} but the kept items add up to {round(total, 2)}")
    check(len(result["grocery_list"]) + len(result["removed_items"]) == len(response["Grocery_list"]),
          "Every grocery item should be either kept or removed")

# ---- Whole logic layer: final outcome ----
def test_good_plan_is_accepted():
    response = sample()
    plan = logicManager.get_filtered_plan(json.dumps(response), user())
    check(plan["outcome"] == "ACCEPTED", f"Standard plan was {plan['outcome']} ({plan['Error']})")
    check(len(plan["Dishes"]) == len(response["Dishes"]), "Standard plan should keep every dish")

def test_outcome_follows_number_of_dishes_kept():
    response = sample()
    plan = logicManager.get_filtered_plan(response, user(goal=("High Protein",), calories=800, protein=35, fat=25))
    kept = len(plan["Dishes"])
    total = len(response["Dishes"])
    if kept == 0:
        expected = "REJECTED"
    elif kept / total >= 0.5:
        expected = "ACCEPTED"
    else:
        expected = "FLAGGED"
    check(plan["outcome"] == expected, f"{kept} of {total} dishes kept, so expected {expected}, got {plan['outcome']}")

def test_bad_plans_are_rejected():
    response = sample()
    over_budget = logicManager.get_filtered_plan(response, user(budget=response["Total_grocery_cost"] / 10))
    check(over_budget["outcome"] == "REJECTED", "A plan far over budget should be rejected")
    broken_json = json.dumps(response)[:-10]                   # the sample reply, cut off part-way
    check(logicManager.get_filtered_plan(broken_json, user())["outcome"] == "REJECTED",
          "A cut-off AI reply (invalid JSON) should be rejected")
    impossible = logicManager.get_filtered_plan(response, user(goal=("Custom Macros",), calories=350, protein=60, fat=30))
    check(impossible["outcome"] == "REJECTED", "Impossible Custom Macros targets should be rejected")

# ---- Runner (plain functions, no classes) ----
ALL_TESTS = [
    test_parse_number_reads_every_dish,
    test_budget_rule,
    test_custom_macros_reasonability_check,
    test_halal_rule,
    test_eggs_rule,
    test_every_removed_dish_has_a_reason,
    test_standard_goal_keeps_every_dish,
    test_low_calories_rule,
    test_high_protein_rule,
    test_custom_macros_rule,
    test_cuisine_rule,
    test_grocery_list_cost_matches_kept_items,
    test_good_plan_is_accepted,
    test_outcome_follows_number_of_dishes_kept,
    test_bad_plans_are_rejected,
]

def run_all_tests():
    failed = 0
    for test in ALL_TESTS:
        try:
            test()
            print(f"PASS  {test.__name__}")
        except AssertionError as error:
            failed = failed + 1
            print(f"FAIL  {test.__name__}\n        {error}")
        except Exception as error:
            failed = failed + 1
            print(f"ERROR {test.__name__}\n        {type(error).__name__}: {error}")
    print(f"\n{len(ALL_TESTS) - failed} of {len(ALL_TESTS)} tests passed")
    return failed == 0

if __name__ == "__main__":
    run_all_tests()