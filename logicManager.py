import json
import math
import re
from dietaryRules import RESTRICTED_KEYWORDS, RESTRICTION_EXCEPTIONS

# Default limits for the meal goals
CALORIE_TOLERANCE = 0.10         # allow dishes to be up to 10% over the per-meal target
NO_ERROR_VALUES = ("", "none", "null", "n/a", "na", "nil", "no error", "false")
LOW_CALORIE_MAX = 500            # calorie cap for "Low Calorie"
HIGH_PROTEIN_MIN = 30            # protein floor (g) for "High Protein"
HIGH_PROTEIN_MIN_RATIO = 0.25    # protein must supply >= 25% of calories

def parse_number(value):
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return float(value)
    if isinstance(value, str):
        number = ""
        for char in value.replace(",", ""):       # "1,200 kcal" -> "1200 kcal"
            if char.isdigit():
                number += char
            elif char == "." and "." not in number:  # allows ".5"
                number += char
            elif number.strip(".") != "":            # a number has been read, stop
                break
            else:                                    # a lone "." (e.g. "kcal. 500"), discard it
                number = ""
        if number.strip(".") != "":
            return float(number)
    return None
    
# Budget Rule
def check_budget_compliance(total_grocery_cost, total_budget):
    total_grocery_cost = parse_number(total_grocery_cost)
    total_budget = parse_number(total_budget)
    
    if total_budget is None or math.isnan(total_budget) or math.isinf(total_budget):
        return {"status": "ERROR", "reason": "Budget is not a valid number."}

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
    if not restrictions:
        matching = dishes
    else:
        for dish in dishes:
            name = dish.get("dish_name")
            # Check the dish name too, e.g. "Pork Bolognese"
            text = f"{dish.get('dish_name') or ''} {dish.get('ingredients') or ''}".lower()

            found = []
            for restriction in restrictions:
                check_text = text
                for safe_phrase in RESTRICTION_EXCEPTIONS.get(restriction, []):
                    check_text = check_text.replace(safe_phrase, " ")
                # Unknown restrictions fall back to matching the restriction word itself
                for keyword in RESTRICTED_KEYWORDS.get(restriction, [restriction]):
                    # whole word, with optional plural: "egg" matches "eggs" but not "eggplant"
                    if re.search(r"\b" + re.escape(keyword) + r"(e?s)?\b", check_text):
                        found.append(f"{keyword} ({restriction})")

            if found:
                flagged.append({
                    "dish_name": name,
                    "reason": f"Dish contains restricted ingredients: {', '.join(found)}"
                })
            else:
                matching.append(dish)

    # If every dish breaks a restriction, NO dish is safe (never fall back to unsafe dishes)
    return {
        "valid_dishes": matching,
        "valid_dish_names": [dish.get("dish_name") for dish in matching],
        "flagged_dishes": flagged,
    }

# Macro & Nutritional Rules (Multi-Condition Rule)
def filter_dishes_by_nutrition(ai_dishes, meal_goal, target_cal=None,
                               target_protein=None, target_fat=None):
    # target_cal is the per-meal calorie target from the user    
    max_cal = None
    min_protein = target_protein
    max_fat = target_fat
    min_ratio = None

    # Accept "Low Calorie", ("Low Calorie",), "low calories", etc.
    if isinstance(meal_goal, (tuple, list)):
        meal_goal = meal_goal[0] if meal_goal else None
    goal = str(meal_goal).strip().lower() if meal_goal is not None else "none"

    if goal in ("low calorie", "low calories"):
        cap = target_cal if target_cal is not None else LOW_CALORIE_MAX
        max_cal = cap * (1 + CALORIE_TOLERANCE)
    elif goal == "high protein":
        if min_protein is None:
            min_protein = HIGH_PROTEIN_MIN
        min_ratio = HIGH_PROTEIN_MIN_RATIO
    elif target_cal is not None:
        # "Standard" or "Custom": don't go over the per-meal target
        max_cal = target_cal * (1 + CALORIE_TOLERANCE)

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

        # Only require the values a rule actually uses (calories are always needed)
        missing = []
        if calories is None:
            missing.append("calories")
        if protein is None and (min_protein is not None or min_ratio is not None):
            missing.append("protein")
        if fat is None and max_fat is not None:
            missing.append("fat")

        if missing:
            reasons.append("Missing or unreadable nutrition data: " + ", ".join(missing))
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
    if not preferences or "anything" in preferences:
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
            "fallback_used": True,
            "valid_dishes": dishes,
            "valid_dish_names": [d.get("dish_name") for d in dishes],
            "flagged_dishes": [],   # these dishes are shown, so don't list them as flagged
        }
    return {
        "fallback_used": False,
        "valid_dishes": matching,
        "valid_dish_names": [d.get("dish_name") for d in matching],
        "flagged_dishes": flagged,
    }

# Turn a name into a set of singular words: "Fresh Eggs" -> {"fresh", "egg"}
def singular_words(text):
    words = set()
    for word in re.findall(r"[a-z]+", str(text).lower()):
        if word.endswith("ies") and len(word) > 4:
            word = word[:-3] + "y"           # berries -> berry
        elif word.endswith("oes") and len(word) > 4:
            word = word[:-2]                 # tomatoes -> tomato
        elif word.endswith("s") and not word.endswith("ss") and len(word) > 3:
            word = word[:-1]                 # eggs -> egg, onions -> onion
        words.add(word)
    return words

# Grocery list filter: keep only ingredients used by the remaining dishes
def filter_grocery_list(grocery_list, valid_dishes):
    # Collect every ingredient used by the dishes that passed, as word sets
    used = []
    for dish in valid_dishes:
        for ing in str(dish.get("ingredients") or "").split(","):
            ing_words = singular_words(ing)
            if ing_words:
                used.append(ing_words)

    kept_items = []
    removed_items = []
    for item in grocery_list or []:
        if not isinstance(item, dict):
            continue
        name_words = singular_words(item.get("ingredient_name", ""))

        # Match either way round, ignoring plurals:
        # "garlic" matches "Garlic and Onion Pack", "Egg" matches "Fresh Eggs",
        # "Chicken Breast Fillet" matches "Chicken Breast"
        is_used = False
        for ing_words in used:
            if name_words and (ing_words <= name_words or name_words <= ing_words):
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
        "warnings": [],
        "flagged_dishes": [],
    }
 
    # Step 3: Check the data, then run the rules
    if not isinstance(ai_output, dict) or not isinstance(user_input, dict):
        plan["Error"] = "Invalid data passed to the logic manager"
 
    elif str(ai_output.get("Error") or "").strip().lower() not in NO_ERROR_VALUES:
        plan["Error"] = str(ai_output["Error"]).strip()
 
    elif not isinstance(ai_output.get("Dishes"), list) or len(ai_output["Dishes"]) == 0:
        plan["Error"] = "The AI returned no dishes"
 
    else:
        dishes = [dish for dish in ai_output["Dishes"] if isinstance(dish, dict)]

        # Pax: use the user's number, warn if the AI planned for a different number
        user_pax = parse_number(user_input.get("Pax"))
        ai_pax = parse_number(ai_output.get("pax"))
        plan["pax"] = int(user_pax) if user_pax else (int(ai_pax) if ai_pax else 0)
        if user_pax and ai_pax and user_pax != ai_pax:
            plan["warnings"].append(
                f"The AI planned for {ai_pax:g} pax but you asked for {user_pax:g}"
            )

        # Filter 1: dietary safety (uses the dish objects directly, not names)
        diet = filter_dishes_by_dietary_rules(dishes, user_input.get("Dietary_restrictions"))
        safe_dishes = diet["valid_dishes"]

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

        # Decide the outcome
        if budget_result["status"] == "REJECTED" or budget_result["status"] == "ERROR":
            plan["outcome"] = "REJECTED"
            plan["Error"] = budget_result["reason"]
        elif len(dishes) == 0 or len(valid_dishes) == 0:
            plan["outcome"] = "REJECTED"
            plan["Error"] = "No dishes passed all the rules"
        elif len(valid_dishes) / len(dishes) >= 0.5:
            plan["outcome"] = "ACCEPTED"
        else:
            plan["outcome"] = "FLAGGED"
            plan["warnings"].append(
                f"Only {len(valid_dishes)} of {len(dishes)} suggested dishes met your "
                "requirements. You may want to regenerate for more options"
            )
    return plan

def build_user_input_dict(user_input):
    # Safe lookup: returns None instead of crashing if the list is too short
    def get(index):
        return user_input[index] if len(user_input) > index else None

    goal = get(4)
    if isinstance(goal, (tuple, list)):        # ('Standard',) → 'Standard'
        goal = goal[0] if goal else None

    per_meal_cal = parse_number(get(5))
    if per_meal_cal is not None and per_meal_cal <= 0:
        per_meal_cal = None

    return {
        "Total_budget": get(1),
        "Pax": get(2),
        "Dietary_restrictions": get(3),
        "Meal_goal": goal,
        "Calorie_count_per_meal_input": per_meal_cal,
        "Protein_per_meal_input": parse_number(get(8)),
        "Fats_per_meal": parse_number(get(9)),
        "Cuisine": get(6),
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