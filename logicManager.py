import json

# Default limits for the meal goals
LOW_CALORIE_MAX = 500            # calorie cap for "Low Calorie"
HIGH_PROTEIN_MIN = 30            # protein floor (g) for "High Protein"
HIGH_PROTEIN_MIN_RATIO = 0.25    # protein must supply >= 25% of calories

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
    
# Budget Rule
def check_budget_compliance(total_grocery_cost, total_budget):
    total_grocery_cost = parse_number(total_grocery_cost)
    total_budget = parse_number(total_budget)
    
    if total_budget is None:
        return {"status": "ERROR", "reason": "Budget not found."}

    elif total_grocery_cost is None:
        return {"status": "ERROR", "reason": "Grocery cost not found."}
    
    elif total_grocery_cost > total_budget:
        return {
            "status": "REJECTED", 
            "reason": f"Total grocery cost (${total_grocery_cost:.2f}) exceeds total budget (${total_budget:.2f})"
        }
    return {
        "status": "ACCEPTED", 
        "reason": f"Total grocery cost (${total_grocery_cost:.2f}) is within total budget (${total_budget:.2f})"
    }

# Dietary Restrictions Filter
def filter_dishes_by_dietary_rules(ai_dishes, dietary_restrictions):
    if ai_dishes is None:
        ai_dishes = []
    dishes = [dish for dish in ai_dishes if isinstance(dish, dict)]

    if dietary_restrictions is None:
        dietary_restrictions = ()
    elif isinstance(dietary_restrictions, str):
        dietary_restrictions = (dietary_restrictions,)

    restrictions = [r.strip().lower() for r in dietary_restrictions if r.strip().lower() != "none"]

    matching = []
    flagged = []
    if "None" in restrictions or not restrictions:
        matching = dishes
    else:
        for dish in dishes:
            dish_dietary = str(dish.get("Dietary_restrictions", "")).strip().lower()
            ingredients = str(dish.get("ingredients")).strip().lower()
            name = dish.get("dish_name")
            
            restricted_ingredients = []
            for i in restrictions:
                if i in ingredients or i in dish_dietary:
                    restricted_ingredients.append(i)
            
            if restricted_ingredients:
                flagged.append({
                    "dish_name": name,
                    "reason": f"Dish contains restricted ingredients: {', '.join(restricted_ingredients)}"
                })
            else:
                matching.append(dish)

    if len(matching) == 0 and len(dishes) > 0:
        return {
            "valid_dishes": dishes,
            "valid_dish_names": [dish.get("dish_name") for dish in dishes],
            "flagged_dishes": flagged
        }
    else:
        return {
            "flagged_count": len(flagged),
            "valid_dish_names": [dish.get("dish_name") for dish in matching],
            "flagged_dishes": flagged
        }

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
            "valid_dish_names": [d.get("dish_name") for d in dishes],
            "flagged_dishes": flagged,
        }
    return {
        "is_exact_match": True,
        "fallback_used": False,
        "valid_dishes": matching,
        "valid_dish_names": [d.get("dish_name") for d in matching],
        "flagged_dishes": flagged,
    }

# Grocery list filter: keep only ingredients used by the remaining dishes
def filter_grocery_list(grocery_list, valid_dishes):
    # Collect every ingredient name used by the dishes that passed
    used = []
    for dish in valid_dishes:
        for ing in str(dish.get("ingredients", "")).split(","):
            ing = ing.strip().lower()
            if ing:
                used.append(ing)

    kept_items = []
    removed_items = []
    for item in grocery_list or []:
        if not isinstance(item, dict):
            continue
        name = str(item.get("ingredient_name", "")).strip().lower()
        name_words = set(name.split())

        # Exact match, or every word of a dish ingredient appears in the item
        # e.g. "garlic" matches "garlic and onion pack"
        is_used = False
        for ing in used:
            if ing == name or set(ing.split()) <= name_words:
                is_used = True
                break

        if is_used:
            kept_items.append(item)
        else:
            removed_items.append(item.get("ingredient_name"))

    new_cost = 0.0
    for item in kept_items:
        new_cost += parse_number(item.get("Price_per_ingredient")) or 0.0

    return {
        "grocery_list": kept_items,
        "removed_items": removed_items,
        "total_cost": round(new_cost, 2),
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
        dishes = ai_output["Dishes"]
        plan["pax"] = ai_output.get("pax", 0)

        # Filter 1: dietary safety
        diet = filter_dishes_by_dietary_rules(dishes, user_input.get("Dietary_restrictions"))
        safe_dishes = []
        for dish in dishes:
            if isinstance(dish, dict) and dish.get("dish_name") in diet["valid_dish_names"]:
                safe_dishes.append(dish)

        # Filter 2: nutrition (multi-condition rule)
        nutrition = filter_dishes_by_nutrition(
            safe_dishes,
            user_input.get("Meal_goal"),
            user_input.get("Calorie_count_per_meal_input"),
            user_input.get("Protein_per_meal_input"),
            user_input.get("Fats_per_meal"),
        )

        # Filter 3: cuisine preference
        cuisine = filter_dishes_by_cuisine(nutrition["valid_dishes"], user_input.get("Cuisine"))
        if cuisine["fallback_used"]:
            plan["warnings"].append("No dishes matched your preferred cuisine, so other cuisines are shown")

        valid_dishes = cuisine["valid_dishes"]
        plan["Dishes"] = valid_dishes
        plan["flagged_dishes"] = diet["flagged_dishes"] + nutrition["flagged_dishes"] + cuisine["flagged_dishes"]

        # Filter 4: grocery list, only ingredients for the remaining dishes
        grocery = filter_grocery_list(ai_output.get("Grocery_list", []), valid_dishes)
        plan["Grocery_list"] = grocery["grocery_list"]
        plan["Total_grocery_cost"] = grocery["total_cost"]
        if grocery["removed_items"]:
            plan["warnings"].append("Removed unused groceries: " + ", ".join(grocery["removed_items"]))

        # Budget rule, checked on the NEW cost
        budget_result = check_budget_compliance(plan["Total_grocery_cost"], user_input.get("Total_budget"))
        if budget_result["status"] == "REJECTED" or budget_result["status"] == "ERROR":
            plan["warnings"].append(budget_result["reason"])

        # Decide the outcome
        if budget_result["status"] == "REJECTED" or budget_result["status"] == "ERROR":
            plan["outcome"] = "REJECTED"
            plan["Error"] = budget_result["reason"]
        elif len(valid_dishes) == 0:
            plan["outcome"] = "REJECTED"
            plan["Error"] = "No dishes passed all the rules"
        elif len(valid_dishes) / len(dishes) >= 0.5:
            plan["outcome"] = "ACCEPTED"
        else:
            plan["outcome"] = "FLAGGED"
    return plan

def build_user_input_dict(user_input):
    goal = user_input[4]
    if isinstance(goal, (tuple, list)):        # ('Standard',) → 'Standard'
        goal = goal[0] if goal else None

    return {
        "Total_budget": user_input[1],
        "Dietary_restrictions": user_input[3],
        "Meal_goal": goal,
        "Calorie_count_per_meal_input": None,   # see note below
        "Protein_per_meal_input": None,
        "Fats_per_meal": None,
        "Cuisine": user_input[6],
    }


def get_filtered_plan(ai_output, user_input):
    if isinstance(user_input, (list, tuple)):
        user_input = build_user_input_dict(user_input)

    plan = process_ai_response(ai_output, user_input)

    if plan["outcome"] == "REJECTED":
        print("Plan rejected:", plan["Error"])
        return None

    for w in plan["warnings"]:
        print("Warning:", w)

    return plan