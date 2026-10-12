import json
import math
DIETARY_RULES_FILE = "dietaryRules.json"


# Default limits for the meal goals
TOLERANCE = 0.10                 # allow dishes 10% leeway on calorie, protein and fat targets
NO_ERROR_VALUES = ("", "none", "null", "n/a", "na", "nil", "no error", "false")
LOW_CALORIE_MAX = 500            # calorie cap for "Low Calorie"
HIGH_PROTEIN_MIN = 30            # protein floor (g) for "High Protein"
HIGH_PROTEIN_MIN_RATIO = 0.25    # protein must supply >= 25% of calories
PROTEIN_KCAL_PER_GRAM = 4        # 1 g of protein = 4 kcal
FAT_KCAL_PER_GRAM = 9            # 1 g of fat = 9 kcal

# Load the restriction keywords from dietaryRules.json.
def load_dietary_rules():
    try:
        with open(DIETARY_RULES_FILE, "r", encoding="utf-8") as file:
            rules = json.load(file)
        return rules["restricted_keywords"], rules["restriction_exceptions"]
    except (OSError, json.JSONDecodeError, KeyError, TypeError):
        return None, None
RESTRICTED_KEYWORDS, RESTRICTION_EXCEPTIONS = load_dietary_rules()

# Read the first number out of a value, e.g. "540 kcal" -> 540.0, "1,200 kcal" -> 1200.0
# Returns None if there is no number in it.
def parse_number(value):
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    if not isinstance(value, str):
        return None

    number = ""
    for char in value.replace(",", ""):
        if char.isdigit():
            number = number + char
        elif char == "." and "." not in number:
            number = number + char
        elif number != "" and number != ".":
            break
        else:
            number = ""               # a lone "." (e.g. "kcal. 500"), throw it away

    if number == "" or number == ".":
        return None
    return float(number)

# Split text into lowercase words, treating anything that is not a letter as a space.
# "Minced Pork, Garlic" -> ["minced", "pork", "garlic"]
def split_into_words(text):
    letters_only = ""
    for char in str(text).lower():
        if char.isalpha():
            letters_only = letters_only + char
        else:
            letters_only = letters_only + " "
    return letters_only.split()

# True if the keyword appears as whole word(s) in the word list, allowing a plural ending.
# "egg" matches ["fresh", "eggs"] but not ["eggplant"]; "soy sauce" matches ["light", "soy", "sauce"].
def contains_keyword(words, keyword):
    keyword_words = keyword.split()
    size = len(keyword_words)

    for start in range(len(words) - size + 1):
        all_match = True
        for i in range(size):
            word = words[start + i]
            target = keyword_words[i]
            if word != target and word != target + "s" and word != target + "es":
                all_match = False
                break
        if all_match:
            return True
    return False

# Reasonability check for Custom Macros targets.
# Protein and fat contain calories, so together they cannot add up to more than the calorie goal.
# Returns (True, "") if the targets are possible, or (False, message) if they are not.
def check_macro_targets(calories, protein, fat):
    calories = parse_number(calories)
    protein = parse_number(protein)
    fat = parse_number(fat)
    if calories is None or protein is None or fat is None:
        return True, ""     # a target is missing, so there is nothing to compare

    macro_calories = protein * PROTEIN_KCAL_PER_GRAM + fat * FAT_KCAL_PER_GRAM
    if macro_calories > calories:
        message = (f"Your protein ({round(protein)}g) and fat ({round(fat)}g) targets add up to "
                   f"{round(macro_calories)} kcal, which is more than your calorie goal of "
                   f"{round(calories)} kcal. Please lower protein or fat, or raise calories.")
        return False, message
    return True, ""

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

# Keep only the items that are dictionaries (skips broken data from the AI)
def only_dishes(ai_dishes):
    dishes = []
    if ai_dishes is None:
        return dishes
    for dish in ai_dishes:
        if isinstance(dish, dict):
            dishes.append(dish)
    return dishes

# Dietary Restrictions Filter
def filter_dishes_by_dietary_rules(ai_dishes, dietary_restrictions):
    dishes = only_dishes(ai_dishes)

    if dietary_restrictions is None:
        dietary_restrictions = ()
    elif isinstance(dietary_restrictions, str):
        dietary_restrictions = (dietary_restrictions,)

    restrictions = []
    for restriction in dietary_restrictions:
        restriction = restriction.strip().lower()
        if restriction != "none":
            restrictions.append(restriction)

    matching = []
    flagged = []
    if len(restrictions) == 0:
        matching = dishes
    elif RESTRICTED_KEYWORDS is None or RESTRICTION_EXCEPTIONS is None:
        # dietaryRules.json could not be loaded, so no dish can be confirmed safe
        for dish in dishes:
            flagged.append({
                "dish_name": dish.get("dish_name"),
                "reason": f"Dietary rules could not be loaded from {DIETARY_RULES_FILE}"
            })
    else:
        for dish in dishes:
            name = dish.get("dish_name")
            # Check the dish name too, e.g. "Pork Bolognese"
            text = str(dish.get("dish_name") or "") + " " + str(dish.get("ingredients") or "")
            text = text.lower()

            found = []
            for restriction in restrictions:
                # Remove safe phrases first, e.g. "coconut milk" is not dairy
                check_text = text
                for safe_phrase in RESTRICTION_EXCEPTIONS.get(restriction, []):
                    check_text = check_text.replace(safe_phrase, " ")
                words = split_into_words(check_text)

                # Unknown restrictions fall back to matching the restriction word itself
                for keyword in RESTRICTED_KEYWORDS.get(restriction, [restriction]):
                    if contains_keyword(words, keyword):
                        found.append(f"{keyword} ({restriction})")

            if len(found) > 0:
                flagged.append({
                    "dish_name": name,
                    "reason": "Dish contains restricted ingredients: " + ", ".join(found)
                })
            else:
                matching.append(dish)

    # If every dish breaks a restriction, NO dish is safe (never fall back to unsafe dishes)
    return {
        "valid_dishes": matching,
        "flagged_dishes": flagged,
    }

# Macro & Nutritional Rules (Multi-Condition Rule)
def filter_dishes_by_nutrition(ai_dishes, meal_goal, target_cal=None,
                               target_protein=None, target_fat=None):
    # Each goal switches on only its own rule (None = rule is off)
    max_cal = None
    min_protein = None
    max_fat = None
    min_ratio = None

    # Accept "Low Calories", ("Low Calories",), "low calorie", etc.
    if isinstance(meal_goal, (tuple, list)):
        if len(meal_goal) > 0:
            meal_goal = meal_goal[0]
        else:
            meal_goal = None
    if meal_goal is None:
        goal = "none"
    else:
        goal = str(meal_goal).strip().lower()

    if goal == "low calorie" or goal == "low calories":
        # Low Calories: calorie limit only
        if target_cal is not None:
            max_cal = target_cal
        else:
            max_cal = LOW_CALORIE_MAX
    elif goal == "high protein":
        # High Protein: protein minimum and protein share of calories only
        if target_protein is not None:
            min_protein = target_protein
        else:
            min_protein = HIGH_PROTEIN_MIN
        min_ratio = HIGH_PROTEIN_MIN_RATIO
    elif goal == "custom macros" or goal == "custom":
        # Custom Macros: the user's own calorie, protein and fat targets
        max_cal = target_cal
        min_protein = target_protein
        max_fat = target_fat
    # "Standard", no goal, or anything else: no nutrition limits

    # 10% leeway: calories and fat may be 10% over, protein 10% under
    if max_cal is not None:
        max_cal = max_cal * (1 + TOLERANCE)
    if min_protein is not None:
        min_protein = min_protein * (1 - TOLERANCE)
    if max_fat is not None:
        max_fat = max_fat * (1 + TOLERANCE)

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

        if len(missing) > 0:
            reasons.append("Missing or unreadable nutrition data: " + ", ".join(missing))
        else:
            # Condition A: calorie cap
            if max_cal is not None and calories > max_cal:
                reasons.append(f"Calories ({round(calories)} kcal) exceed target ({round(max_cal)} kcal)")
            # Condition B: protein floor
            if min_protein is not None and protein < min_protein:
                reasons.append(f"Protein ({round(protein, 1)}g) below target ({round(min_protein, 1)}g)")
            # Condition C: fat cap
            if max_fat is not None and fat > max_fat:
                reasons.append(f"Fat ({round(fat, 1)}g) exceeds target ({round(max_fat, 1)}g)")
            # Condition D: macro balance for the chosen goal
            if min_ratio is not None and calories > 0:
                ratio = (protein * PROTEIN_KCAL_PER_GRAM) / calories
                if ratio < min_ratio:
                    reasons.append(f"Protein provides only {round(ratio * 100)}% of calories "
                                   f"(goal needs {round(min_ratio * 100)}%)")

        if len(reasons) > 0:
            flagged_dishes.append({"dish_name": name, "reason": "; ".join(reasons)})
        else:
            valid_dishes.append(dish)

    return {
        "flagged_dishes": flagged_dishes,
        "valid_dishes": valid_dishes,
    }

# Preference Rules
def filter_dishes_by_cuisine(ai_dishes, preferred_cuisines):
    dishes = only_dishes(ai_dishes)

    if preferred_cuisines is None:
        preferred_cuisines = ()
    elif isinstance(preferred_cuisines, str):
        preferred_cuisines = (preferred_cuisines,)

    preferences = []
    for c in preferred_cuisines:
        preferences.append(c.strip().lower())

    matching = []
    flagged = []
    if len(preferences) == 0 or "anything" in preferences:
        matching = dishes
    else:
        for dish in dishes:
            cuisine = str(dish.get("cuisine")).strip()
            if cuisine.lower() in preferences:
                matching.append(dish)
            else:
                flagged.append({"dish_name": dish.get("dish_name"), "reason": f"Cuisine '{cuisine}' not in preferences"})

    if len(matching) == 0 and len(dishes) > 0:
        return {
            "fallback_used": True,
            "valid_dishes": dishes,
            "flagged_dishes": [],   # these dishes are shown, so don't list them as flagged
        }
    return {
        "fallback_used": False,
        "valid_dishes": matching,
        "flagged_dishes": flagged,
    }

# Turn one word into its singular form: "eggs" -> "egg", "tomatoes" -> "tomato", "berries" -> "berry"
def make_singular(word):
    if word.endswith("ies") and len(word) > 4:
        return word[:-3] + "y"
    if word.endswith("oes") and len(word) > 4:
        return word[:-2]
    if word.endswith("s") and not word.endswith("ss") and len(word) > 3:
        return word[:-1]
    return word

# Turn a name into a list of singular words: "Fresh Eggs" -> ["fresh", "egg"]
def singular_words(text):
    words = []
    for word in split_into_words(text):
        words.append(make_singular(word))
    return words

# True if every word in small_list is also in big_list
def all_words_in(small_list, big_list):
    for word in small_list:
        if word not in big_list:
            return False
    return True

# Grocery list filter: keep only ingredients used by the remaining dishes
def filter_grocery_list(grocery_list, valid_dishes):
    # Collect every ingredient used by the dishes that passed, as lists of words
    used = []
    for dish in valid_dishes:
        for ingredient in str(dish.get("ingredients") or "").split(","):
            ingredient_words = singular_words(ingredient)
            if len(ingredient_words) > 0:
                used.append(ingredient_words)

    if grocery_list is None:
        grocery_list = []

    kept_items = []
    removed_items = []
    for item in grocery_list:
        if not isinstance(item, dict):
            continue
        name_words = singular_words(item.get("ingredient_name", ""))

        # Match either way round, ignoring plurals:
        # "garlic" matches "Garlic and Onion Pack", "Egg" matches "Fresh Eggs",
        # "Chicken Breast Fillet" matches "Chicken Breast"
        is_used = False
        if len(name_words) > 0:
            for ingredient_words in used:
                if all_words_in(ingredient_words, name_words) or all_words_in(name_words, ingredient_words):
                    is_used = True
                    break

        if is_used:
            kept_items.append(item)
        else:
            removed_items.append(item.get("ingredient_name"))

    new_cost = 0.0
    for item in kept_items:
        price = parse_number(item.get("Price_per_ingredient"))
        if price is not None:
            new_cost = new_cost + price

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

    # Custom Macros: make sure the user's targets are actually possible
    macro_ok = True
    macro_error = ""
    if isinstance(user_input, dict):
        goal_name = str(user_input.get("Meal_goal") or "").strip().lower()
        if goal_name == "custom macros" or goal_name == "custom":
            macro_ok, macro_error = check_macro_targets(
                user_input.get("Calorie_count_per_meal_input"),
                user_input.get("Protein_per_meal_input"),
                user_input.get("Fats_per_meal"),
            )

    # The AI's Error field: "None", "N/A", "" etc. mean there is no error
    ai_error = ""
    if isinstance(ai_output, dict) and ai_output.get("Error") is not None:
        ai_error = str(ai_output.get("Error")).strip()

    # Step 3: Check the data, then run the rules
    if not isinstance(ai_output, dict) or not isinstance(user_input, dict):
        plan["Error"] = "Invalid data passed to the logic manager"

    elif not macro_ok:
        plan["Error"] = macro_error

    elif ai_error.lower() not in NO_ERROR_VALUES:
        plan["Error"] = ai_error

    elif not isinstance(ai_output.get("Dishes"), list) or len(ai_output["Dishes"]) == 0:
        plan["Error"] = "The AI returned no dishes"

    else:
        dishes = only_dishes(ai_output["Dishes"])

        # Pax: use the user's number, warn if the AI planned for a different number
        user_pax = parse_number(user_input.get("Pax"))
        ai_pax = parse_number(ai_output.get("pax"))
        if user_pax:
            plan["pax"] = int(user_pax)
        elif ai_pax:
            plan["pax"] = int(ai_pax)
        if user_pax and ai_pax and user_pax != ai_pax:
            plan["warnings"].append(
                f"The AI planned for {round(ai_pax)} pax but you asked for {round(user_pax)}"
            )

        # Filter 1: dietary safety
        diet = filter_dishes_by_dietary_rules(dishes, user_input.get("Dietary_restrictions"))

        # Filter 2: nutrition (multi-condition rule)
        nutrition = filter_dishes_by_nutrition(
            diet["valid_dishes"],
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
        if len(grocery["removed_items"]) > 0:
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

def get_item(user_input, index):
    if index < len(user_input):
        return user_input[index]
    return None

def get_target(user_input, index):
    value = parse_number(get_item(user_input, index))
    if value is None or value <= 0:
        return None
    return value

def build_user_input_dict(user_input):
    goal = get_item(user_input, 4)
    if isinstance(goal, (tuple, list)): # ('Standard',) -> 'Standard'
        if len(goal) > 0:
            goal = goal[0]
        else:
            goal = None

    return {
        "Total_budget": get_item(user_input, 1),
        "Pax": get_item(user_input, 2),
        "Dietary_restrictions": get_item(user_input, 3),
        "Meal_goal": goal,
        "Calorie_count_per_meal_input": get_target(user_input, 5),
        "Protein_per_meal_input": get_target(user_input, 8),
        "Fats_per_meal": get_target(user_input, 9),
        "Cuisine": get_item(user_input, 6),
    }

def get_filtered_plan(ai_output, user_input):
    if isinstance(user_input, (list, tuple)):
        user_input = build_user_input_dict(user_input)

    return process_ai_response(ai_output, user_input)