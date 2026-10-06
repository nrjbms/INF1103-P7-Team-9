import json

# Default limits for the meal goals
LOW_CALORIE_MAX = 500            # calorie cap for "Low Calorie"
HIGH_PROTEIN_MIN = 30            # protein floor (g) for "High Protein"
HIGH_PROTEIN_MIN_RATIO = 0.25    # protein must supply >= 25% of calories


# Test Data
test_dishes = [
    {"dish_name": "Grilled Chicken Salad", "calorie_count_per_meal_output": 350,
     "protein_count_per_meal_output": 30, "fats_count_per_meal": 10, "cuisine": "American"},
    {"dish_name": "Vegetable Stir Fry", "calorie_count_per_meal_output": 400,
     "protein_count_per_meal_output": 15, "fats_count_per_meal": 5, "cuisine": "Asian"},
    {"dish_name": "Beef Tacos", "calorie_count_per_meal_output": 600,
     "protein_count_per_meal_output": 25, "fats_count_per_meal": 20, "cuisine": "Mexican"},
    {"dish_name": "Pasta Primavera", "calorie_count_per_meal_output": 450,
     "protein_count_per_meal_output": 20, "fats_count_per_meal": 15, "cuisine": "Italian"},
    {"dish_name": "Salmon with Quinoa", "calorie_count_per_meal_output": 500,
     "protein_count_per_meal_output": 35, "fats_count_per_meal": 12, "cuisine": "Seafood"},
]

test_user_input = {
    "Meal_goal": "High Protein",
    "Calorie_count_per_meal_input": None,
    "Protein_per_meal_input": None,
    "Fats_per_meal": None,
    "Cuisine": ("Anything",),
}

test_ai_output = {
    "pax": 1,
    "Error": "",
    "Total_grocery_cost": 40.0,
    "Grocery_list": [],
    "Dishes": test_dishes,
}

def parse_number(value):
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return float(value)
    if isinstance(value, str):
        number = ""
        for char in value:
            if char.isdigit():
                number += char
            elif char == "." and number != "" and "." not in number:
                number += char
            elif number != "":
                break
        if number != "":
            return float(number)
    return None


# Macro & Nutritional Rules (Multi-Condition Rule)
def filter_dishes_by_nutrition(ai_dishes, meal_goal, target_cal=None,
                               target_protein=None, target_fat=None):
    # Work out the limits from the meal goal (None = no limit)
    max_cal = target_cal
    min_protein = target_protein
    max_fat = target_fat
    min_ratio = None

    if meal_goal is not None:
        goal = str(meal_goal).strip().lower()
        if goal == "low calorie" and max_cal is None:
            max_cal = LOW_CALORIE_MAX
        elif goal == "high protein":
            if min_protein is None:
                min_protein = HIGH_PROTEIN_MIN
            min_ratio = HIGH_PROTEIN_MIN_RATIO

    valid_dishes = []
    flagged_dishes = []

    if ai_dishes is None:
        ai_dishes = []
    for dish in ai_dishes:
        if not isinstance(dish, dict):
            flagged_dishes.append({"dish_name": "Unknown dish", "reason": "Dish data is malformed"})
            continue

        name = dish.get("dish_name")
        calories = parse_number(dish.get("calorie_count_per_meal_output"))
        protein = parse_number(dish.get("protein_count_per_meal_output"))
        fat = parse_number(dish.get("fats_count_per_meal"))
        reasons = []

        if calories is None or protein is None or fat is None:
            reasons.append("Missing or unreadable nutrition data")
        else:
            # Condition A: calorie cap
            if max_cal is not None and calories > max_cal:
                reasons.append(f"Calories ({calories:g} kcal) exceed target ({max_cal:g} kcal)")
            # Condition B: protein floor
            if min_protein is not None and protein < min_protein:
                reasons.append(f"Protein ({protein:g}g) below target ({min_protein:g}g)")
            # Condition C: fat cap
            if max_fat is not None and fat > max_fat:
                reasons.append(f"Fat ({fat:g}g) exceeds target ({max_fat:g}g)")
            # Condition D: macro balance for the chosen goal
            if min_ratio is not None and calories > 0:
                ratio = (protein * 4) / calories
                if ratio < min_ratio:
                    reasons.append(f"Protein provides only {ratio:.0%} of calories "
                                f"(goal needs {min_ratio:.0%})")

        if reasons:
            flagged_dishes.append({"dish_name": name, "reason": "; ".join(reasons)})
            print(f"Dish '{name}' flagged: {'; '.join(reasons)}")
        else:
            valid_dishes.append(dish)

    return {
        "flagged_dishes": flagged_dishes,
        "valid_dishes": valid_dishes,
        "valid_dish_names": [dish.get("dish_name") for dish in valid_dishes],
    }


# Preference Rules
def filter_dishes_by_cuisine(ai_dishes, preferred_cuisines):
    if ai_dishes is None:
        ai_dishes = []
    dishes = [dish for dish in ai_dishes if isinstance(dish, dict)]

    if preferred_cuisines is None:
        preferred_cuisines = ()
    elif isinstance(preferred_cuisines, str):
        preferred_cuisines = (preferred_cuisines,)

    preferences = []
    for c in preferred_cuisines:
        preferences.append(c.strip().lower())

    matching = []
    flagged = []
    if "anything" in preferences:
        matching = dishes
    else:
        for dish in dishes:
            cuisine = str(dish.get("cuisine")).strip()
            if cuisine.lower() in preferences:
                matching.append(dish)
            else:
                flagged.append({"dish_name": dish.get("dish_name"),"reason": f"Cuisine '{cuisine}' not in preferences"})

    if len(matching) == 0 and len(dishes) > 0:
        return {
            "is_exact_match": False,
            "fallback_used": True,
            "valid_dishes": dishes,
            "valid_dish_names": [dish.get("dish_name") for dish in dishes],
        }
    else:
        return {
            "is_exact_match": True,
            "fallback_used": False,
            "flagged_count": len(flagged),
            "valid_dish_names": [dish.get("dish_name") for dish in matching],
        }

def process_ai_response(ai_output, user_input):
    # Step 1: The AI manager returns JSON as text, so convert it to a dictionary.
    if isinstance(ai_output, str):
        try:
            ai_output = json.loads(ai_output)
        except json.JSONDecodeError:
            ai_output = {"Error": ai_output}
 
    # Step 2: Start with a rejected plan. It only improves if every check passes.
    plan = {
        "pax": 0,
        "Error": "",
        "Total_grocery_cost": 0,
        "Grocery_list": [],
        "Dishes": [],
        "outcome": "REJECTED",
        "score": 0.0,
        "quality_rating": "REJECTED",
        "warnings": [],
        "flagged_dishes": [],
    }
 
    # Step 3: Check the data, then run the rules
    if not isinstance(ai_output, dict) or not isinstance(user_input, dict):
        plan["Error"] = "Invalid data passed to the logic manager"
 
    elif ai_output.get("Error"):
        plan["Error"] = ai_output["Error"]
 
    elif not isinstance(ai_output.get("Dishes"), list) or len(ai_output["Dishes"]) == 0:
        plan["Error"] = "The AI returned no dishes"
 
    else:
        # Copy the AI's details into the plan
        dishes = ai_output["Dishes"]
        total_cost = ai_output.get("Total_grocery_cost")
        plan["pax"] = ai_output.get("pax", 0)
        plan["Total_grocery_cost"] = total_cost
        plan["Grocery_list"] = ai_output.get("Grocery_list", [])
 
        # # Budget rule (Felix)
        # budget_result = check_budget_compliance(total_cost, user_input.get("Total_budget"))
        # plan["budget"] = budget_result
        # if budget_result["status"] == "WARNING":
        #     plan["warnings"].append(budget_result["reason"])
 
        # # Filter 1: dietary safety (Felix)
        # diet = filter_dishes_by_dietary_rules(dishes, user_input.get("Diet_restriction"))
        # safe_dishes = []
        # for dish in dishes:
        #     if isinstance(dish, dict) and dish.get("dish_name") in diet["valid_dish_names"]:
        #         safe_dishes.append(dish)
 
        # Filter 2: nutrition (multi-condition rule)
        nutrition = filter_dishes_by_nutrition(
            dishes,
            user_input.get("Meal_goal"),
            user_input.get("Calorie_count_per_meal_input"),
            user_input.get("Protein_per_meal_input"),
            user_input.get("Fats_per_meal"),
        ) 
        # Filter 3: cuisine preference
        cuisine = filter_dishes_by_cuisine(nutrition["valid_dishes"], user_input.get("Cuisine"))
        if cuisine["fallback_used"]:
            plan["warnings"].append("No dishes matched your preferred cuisine, so other cuisines are shown")
 
        # Keep only the dishes that passed every rule
        valid_dishes = cuisine["valid_dishes"]
        plan["Dishes"] = valid_dishes
        # plan["flagged_dishes"] = diet["flagged_dishes"] + nutrition["flagged_dishes"] + cuisine["flagged_dishes"]
        plan["flagged_dishes"] = nutrition["flagged_dishes"] + cuisine["flagged_dishes"]
 
        # Decide the outcome
        # if budget_result["status"] == "REJECT":
        #     plan["outcome"] = "REJECTED"
        #     plan["Error"] = budget_result["reason"]
        # elif len(valid_dishes) == 0:
        #     plan["outcome"] = "REJECTED"
        #     plan["Error"] = "No dishes passed all the rules"
        # elif budget_result["status"] == "PASS" and len(valid_dishes) / len(dishes) >= 0.8:
        #     plan["outcome"] = "ACCEPTED"
        # else:
        #     plan["outcome"] = "FLAGGED"
        if len(valid_dishes) == 0:
            plan["outcome"] = "REJECTED"
            plan["Error"] = "No dishes passed all the rules"
        else:
            plan["outcome"] = "FLAGGED"
    return plan
if __name__ == "__main__":
    nutrition = filter_dishes_by_nutrition(test_dishes, "High Protein")
    print(nutrition["valid_dish_names"])
    print(nutrition["flagged_dishes"])

    cuisine = filter_dishes_by_cuisine(nutrition["valid_dishes"], ("Anything",))
    print(cuisine["valid_dish_names"])
    print(cuisine["fallback_used"])