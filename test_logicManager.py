# Automated tests for logicManager.py - Brandon
# Feeds the hardcoded sample AI response (sampleoutput.json) into the logic layer
# and checks every business rule makes the right decision.
# No live API call, no API key and no .env file needed.
# Run from the project folder with:  python test_logicManager.py
# Exit code is 0 if every test passes, 1 if any test fails.

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
def user(budget=50.0, pax=1, restrictions=("None",), goal=("Standard",),
         calories=650, cuisine=("Anything",), protein=27, fat=20):
    return ["Tester", budget, pax, restrictions, goal, calories, cuisine, "Singapore", protein, fat]


# List of dish names from a list of dishes
def names(dishes):
    result = []
    for dish in dishes:
        result.append(dish["dish_name"])
    return result


# Compare a result with the expected value; explain the difference if they don't match
def check(actual, expected, what):
    if actual != expected:
        raise AssertionError(f"{what}\n        expected: {expected}\n        got:      {actual}")


# Compare the dishes a filter kept, and list why each removed dish was removed
def check_kept(result, expected_names, what):
    kept = names(result["valid_dishes"])
    if kept != expected_names:
        reasons = ""
        for flag in result.get("flagged_dishes", []):
            reasons = reasons + f"\n          - {flag['dish_name']}: {flag['reason']}"
        if reasons == "":
            reasons = " none"
        raise AssertionError(f"{what}\n        expected: {expected_names}\n        got:      {kept}"
                             f"\n        removed dishes and reasons:{reasons}")


# Dish names, read from sampleoutput.json in the order they appear there
ALL_DISHES = names(sample()["Dishes"])
STIR_FRY = ALL_DISHES[0]
BOLOGNESE = ALL_DISHES[1]
CURRY = ALL_DISHES[2]
DONBURI = ALL_DISHES[3]
FRIED_RICE = ALL_DISHES[4]


# ---- Helper and budget rule ----

def test_parse_number():
    check(logicManager.parse_number("540 kcal"), 540.0, 'parse_number("540 kcal")')
    check(logicManager.parse_number("1,200 kcal"), 1200.0, 'parse_number("1,200 kcal")')
    check(logicManager.parse_number("abc"), None, 'parse_number("abc") should be unreadable')


def test_budget_rule():
    cost = sample()["Total_grocery_cost"]       # $42.20 in sampleoutput.json
    check(logicManager.check_budget_compliance(cost, cost)["status"], "ACCEPTED",
          f"Cost ${cost} with a budget of exactly ${cost}")
    check(logicManager.check_budget_compliance(cost, cost - 1)["status"], "REJECTED",
          f"Cost ${cost} with a budget of ${cost - 1:.2f}")
    check(logicManager.check_budget_compliance(cost, float("nan"))["status"], "ERROR",
          "Budget 'nan'")


def test_custom_macros_reasonability_check():
    check(logicManager.check_macro_targets(600, 30, 15)[0], True,
          "600 kcal / 30 g protein / 15 g fat should be possible (255 kcal)")
    check(logicManager.check_macro_targets(350, 60, 30)[0], False,
          "350 kcal / 60 g protein / 30 g fat should be impossible (510 kcal)")


# ---- Dietary filter ----

def test_halal_removes_pork_dish():
    result = logicManager.filter_dishes_by_dietary_rules(sample()["Dishes"], ("Halal",))
    check_kept(result, [STIR_FRY, CURRY, DONBURI, FRIED_RICE], "Halal should remove only the pork dish")


def test_other_restrictions():
    dishes = sample()["Dishes"]
    check_kept(logicManager.filter_dishes_by_dietary_rules(dishes, ("Eggs",)),
               [STIR_FRY, BOLOGNESE, CURRY], "Eggs should remove the two egg dishes")
    check_kept(logicManager.filter_dishes_by_dietary_rules(dishes, ("Dairy",)),
               ALL_DISHES, "Dairy should keep every dish (none contain dairy)")
    check_kept(logicManager.filter_dishes_by_dietary_rules(dishes, ("Wheat",)),
               [CURRY], "Wheat should remove pasta and every dish with soy sauce")


# ---- Nutrition goals (multi-condition rule) ----

def test_standard_goal_has_no_limits():
    result = logicManager.filter_dishes_by_nutrition(sample()["Dishes"], "Standard", 650, 27, 20)
    check_kept(result, ALL_DISHES, "Standard has no limits, so every dish should be kept")


def test_low_calories_checks_calories_only():
    # Cap is 500 + 10% = 550 kcal; the 620 and 580 kcal dishes are removed
    result = logicManager.filter_dishes_by_nutrition(sample()["Dishes"], "Low Calories", 500, 22, 15)
    check_kept(result, [STIR_FRY, DONBURI, FRIED_RICE], "Low Calories (500 kcal + 10% = 550 kcal cap)")


def test_high_protein_checks_amount_and_share():
    # Needs 35 g - 10% = 31.5 g protein and at least 25% of calories from protein
    result = logicManager.filter_dishes_by_nutrition(sample()["Dishes"], "High Protein", 800, 35, 25)
    check_kept(result, [STIR_FRY, CURRY], "High Protein (31.5 g minimum, 25% of calories from protein)")


def test_custom_macros_checks_all_three():
    # Protein at least 27 g, fat at most 16.5 g: fried rice (18 g protein) and pork (18 g fat) fail
    result = logicManager.filter_dishes_by_nutrition(sample()["Dishes"], "Custom Macros", 600, 30, 15)
    check_kept(result, [STIR_FRY, CURRY, DONBURI], "Custom Macros (660 kcal max, 27 g protein min, 16.5 g fat max)")


# ---- Cuisine and grocery list ----

def test_cuisine_match_and_fallback():
    chinese = logicManager.filter_dishes_by_cuisine(sample()["Dishes"], ("Chinese",))
    check_kept(chinese, [STIR_FRY, FRIED_RICE], "Chinese cuisine")
    check(chinese["fallback_used"], False, "Chinese: fallback used?")
    mexican = logicManager.filter_dishes_by_cuisine(sample()["Dishes"], ("Mexican",))
    check_kept(mexican, ALL_DISHES, "Mexican (no match): all dishes shown as fallback")
    check(mexican["fallback_used"], True, "Mexican: fallback used?")


def test_grocery_list_keeps_only_used_items():
    response = sample()
    stir_fry_only = [response["Dishes"][0]]
    result = logicManager.filter_grocery_list(response["Grocery_list"], stir_fry_only)
    kept = []
    for item in result["grocery_list"]:
        kept.append(item["ingredient_name"])
    check(kept, ["Jasmine Rice", "Chicken Breast", "Bok Choy", "Garlic and Onion Pack",
                 "Cooking Oil", "Light Soy Sauce"], "Groceries kept for the stir-fry only")
    check(result["total_cost"], 22.1, "Recalculated grocery cost for the stir-fry only")


# ---- Whole logic layer: final outcome ----

def test_good_plan_is_accepted():
    plan = logicManager.get_filtered_plan(json.dumps(sample()), user())
    check(plan["outcome"], "ACCEPTED", f"Standard plan outcome (rejection reason: {plan['Error'] or 'none'})")
    check(names(plan["Dishes"]), ALL_DISHES, "Standard plan: dishes kept")


def test_plan_with_few_dishes_left_is_flagged():
    plan = logicManager.get_filtered_plan(sample(), user(goal=("High Protein",), calories=800, protein=35, fat=25))
    check(plan["outcome"], "FLAGGED",
          f"High Protein plan with 2 of 5 dishes left (kept: {names(plan['Dishes'])}, "
          f"rejection reason: {plan['Error'] or 'none'})")


def test_bad_plans_are_rejected():
    over_budget = logicManager.get_filtered_plan(sample(), user(budget=20.0))
    check(over_budget["outcome"], "REJECTED",
          f"Plan costing ${over_budget['Total_grocery_cost']:.2f} with a $20 budget")
    not_json = logicManager.get_filtered_plan("this is not JSON", user())
    check(not_json["outcome"], "REJECTED", "AI reply that is not JSON")
    impossible = logicManager.get_filtered_plan(sample(), user(goal=("Custom Macros",), calories=350, protein=60, fat=30))
    check(impossible["outcome"], "REJECTED", "Custom Macros 350 kcal / 60 g / 30 g")


def test_logic_layer_has_no_print_calls():
    # The spec says only the input layer may print, so logicManager.py must not contain print(
    with open("logicManager.py", "r", encoding="utf-8") as file:
        code = file.read()
    check("print(" in code, False, "Does logicManager.py contain print( ? (only inputManager may print)")


# ---- Runner (plain functions, no classes) ----

ALL_TESTS = [
    test_parse_number,
    test_budget_rule,
    test_custom_macros_reasonability_check,
    test_halal_removes_pork_dish,
    test_other_restrictions,
    test_standard_goal_has_no_limits,
    test_low_calories_checks_calories_only,
    test_high_protein_checks_amount_and_share,
    test_custom_macros_checks_all_three,
    test_cuisine_match_and_fallback,
    test_grocery_list_keeps_only_used_items,
    test_good_plan_is_accepted,
    test_plan_with_few_dishes_left_is_flagged,
    test_bad_plans_are_rejected,
    test_logic_layer_has_no_print_calls,
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
    if run_all_tests():
        sys.exit(0)
    else:
        sys.exit(1)