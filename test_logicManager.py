# Automated tests for logicManager.py - Brandon
# Feeds the hardcoded sample AI response (sampleoutput.json) into the logic layer and checks every business rule makes the right decision.
# No live API call, no API key and no .env file needed.

import copy
import io
import json
import os
import sys
from contextlib import redirect_stdout

import logicManager

SAMPLE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sampleoutput.json")
with open(SAMPLE_FILE, "r", encoding="utf-8") as file:
    SAMPLE_AI_RESPONSE = json.load(file)


def sample():
    """Fresh copy of the sample AI response, so tests can't affect each other."""
    return copy.deepcopy(SAMPLE_AI_RESPONSE)


def user(budget=50.0, pax=1, restrictions=("None",), goal=("Standard",),
         calories=650, cuisine=("Anything",), protein=27, fat=20):
    """User input list in the same order inputManager.main_input() builds it."""
    return ["Tester", budget, pax, restrictions, goal, calories, cuisine, "Singapore", protein, fat]


def names(dishes):
    return [dish["dish_name"] for dish in dishes]


# ---- Helper and budget rule ----

def test_parse_number():
    assert logicManager.parse_number("540 kcal") == 540.0
    assert logicManager.parse_number("1,200 kcal") == 1200.0
    assert logicManager.parse_number("abc") is None


def test_budget_rule():
    assert logicManager.check_budget_compliance(50.0, 50.0)["status"] == "ACCEPTED"
    assert logicManager.check_budget_compliance(60.0, 50.0)["status"] == "REJECTED"
    assert logicManager.check_budget_compliance(30.0, float("nan"))["status"] == "ERROR"


def test_custom_macros_reasonability_check():
    assert logicManager.check_macro_targets(600, 30, 15)[0] is True    # 255 kcal fits
    assert logicManager.check_macro_targets(350, 60, 30)[0] is False   # 510 kcal > 350


# ---- Dietary filter ----

def test_halal_removes_pork_dish():
    result = logicManager.filter_dishes_by_dietary_rules(sample()["Dishes"], ("Halal",))
    assert "Minced Pork Bolognese Spaghetti" not in names(result["valid_dishes"])
    assert len(result["valid_dishes"]) == 4


def test_dietary_matches_whole_words_only():
    dishes = [{"dish_name": "Eggplant Stir Fry", "ingredients": "Eggplant"},
              {"dish_name": "Thai Curry", "ingredients": "Chicken, Coconut Milk"}]
    assert len(logicManager.filter_dishes_by_dietary_rules(dishes, ("Eggs",))["valid_dishes"]) == 2
    assert len(logicManager.filter_dishes_by_dietary_rules(dishes, ("Dairy",))["valid_dishes"]) == 2


# ---- Nutrition goals (multi-condition rule) ----

def test_standard_goal_has_no_limits():
    result = logicManager.filter_dishes_by_nutrition(sample()["Dishes"], "Standard", 650, 27, 20)
    assert len(result["valid_dishes"]) == 5


def test_low_calories_checks_calories_only():
    # Cap is 500 + 10% = 550 kcal; the 620 and 580 kcal dishes are removed
    result = logicManager.filter_dishes_by_nutrition(sample()["Dishes"], "Low Calories", 500, 22, 15)
    assert len(result["valid_dishes"]) == 3


def test_high_protein_checks_amount_and_share():
    # Needs 35 g - 10% = 31.5 g protein and at least 25% of calories from protein
    result = logicManager.filter_dishes_by_nutrition(sample()["Dishes"], "High Protein", 800, 35, 25)
    assert names(result["valid_dishes"]) == ["Chicken and Bok Choy Stir-Fry with Rice",
                                             "Braised Chicken and Potato Curry"]


def test_custom_macros_checks_all_three():
    # Protein at least 27 g, fat at most 16.5 g: fried rice (18 g protein) and pork (18 g fat) fail
    result = logicManager.filter_dishes_by_nutrition(sample()["Dishes"], "Custom Macros", 600, 30, 15)
    assert len(result["valid_dishes"]) == 3


# ---- Cuisine and grocery list ----

def test_cuisine_match_and_fallback():
    chinese = logicManager.filter_dishes_by_cuisine(sample()["Dishes"], ("Chinese",))
    assert len(chinese["valid_dishes"]) == 2 and chinese["fallback_used"] is False
    mexican = logicManager.filter_dishes_by_cuisine(sample()["Dishes"], ("Mexican",))
    assert len(mexican["valid_dishes"]) == 5 and mexican["fallback_used"] is True


def test_grocery_list_removes_unused_items():
    grocery = [{"ingredient_name": "Fresh Eggs", "Price_per_ingredient": 3.0},
               {"ingredient_name": "Cabbage", "Price_per_ingredient": 2.0}]
    result = logicManager.filter_grocery_list(grocery, [{"ingredients": "Egg"}])
    assert result["removed_items"] == ["Cabbage"] and result["total_cost"] == 3.0


# ---- Whole logic layer: final outcome ----

def test_good_plan_is_accepted():
    plan = logicManager.get_filtered_plan(json.dumps(sample()), user())
    assert plan["outcome"] == "ACCEPTED" and len(plan["Dishes"]) == 5


def test_plan_with_few_dishes_left_is_flagged():
    plan = logicManager.get_filtered_plan(sample(), user(goal=("High Protein",), calories=800, protein=35, fat=25))
    assert plan["outcome"] == "FLAGGED"


def test_bad_plans_are_rejected():
    over_budget = logicManager.get_filtered_plan(sample(), user(budget=20.0))
    not_json = logicManager.get_filtered_plan("this is not JSON", user())
    impossible = logicManager.get_filtered_plan(sample(), user(goal=("Custom Macros",), calories=350, protein=60, fat=30))
    assert over_budget["outcome"] == not_json["outcome"] == impossible["outcome"] == "REJECTED"


def test_logic_layer_never_prints():
    captured = io.StringIO()
    with redirect_stdout(captured):
        logicManager.get_filtered_plan(sample(), user(restrictions=("Halal",)))
    assert captured.getvalue() == ""


# ---- Runner (plain functions, no classes) ----

def run_all_tests():
    tests = [(name, func) for name, func in globals().items() if name.startswith("test_")]
    failed = 0
    for name, test in tests:
        try:
            test()
            print(f"PASS  {name}")
        except Exception as error:
            failed += 1
            print(f"FAIL  {name}: {type(error).__name__} {error}")
    print(f"\n{len(tests) - failed} of {len(tests)} tests passed")
    return failed == 0


if __name__ == "__main__":
    sys.exit(0 if run_all_tests() else 1)