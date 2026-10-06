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
    "Total_budget": 50,
    "Dietary_restrictions": ("Eggs", "Pasta"),
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
    "Dishes": [
    {
      "dish_name": "Chicken and Bok Choy Stir-Fry with Rice",
      "cuisine": "Chinese",
      "recipe": "1. Dice 200g chicken breast and slice 1 clove garlic. 2. Heat 1 tbsp oil in a pan, fry garlic until fragrant, then cook chicken until lightly browned. 3. Add 125g chopped bok choy and 1 tbsp soy sauce. Stir-fry for 3-4 minutes until cooked through. 4. Serve hot with 1 cup cooked jasmine rice.",
      "calorie_count_per_meal_output": "540 kcal",
      "protein_count_per_meal_output": "42g",
      "fats_count_per_meal": "14g",
      "price_per_meal": 3.1,
      "ingredients": "Chicken Breast, Bok Choy, Garlic, Light Soy Sauce, Cooking Oil, Jasmine Rice"
    },
    {
      "dish_name": "Minced Pork Bolognese Spaghetti",
      "cuisine": "Italian",
      "recipe": "1. Boil 100g spaghetti in salted water until al dente. 2. In a skillet, sauté diced onion and garlic in 1 tbsp oil. 3. Add 150g minced pork and cook until browned. 4. Pour in 200g canned chopped tomatoes, simmer for 10 minutes until sauce thickens, then toss with the spaghetti.",
      "calorie_count_per_meal_output": "620 kcal",
      "protein_count_per_meal_output": "34g",
      "fats_count_per_meal": "18g",
      "price_per_meal": 3.3,
      "ingredients": "Spaghetti Pasta, Minced Pork, Canned Chopped Tomatoes, Onion, Garlic, Cooking Oil"
    },
    {
      "dish_name": "Braised Chicken and Potato Curry",
      "cuisine": "Malay",
      "recipe": "1. Dice 200g chicken breast, 1 potato, and 1/2 carrot. 2. Sauté chopped onion and garlic in 1 tbsp oil, then stir in 1.5 tbsp curry powder with a splash of water to form a paste. 3. Add chicken, potatoes, carrots, and 1.5 cups water. Simmer covered for 20 minutes until potatoes are tender. 4. Serve over steamed jasmine rice.",
      "calorie_count_per_meal_output": "580 kcal",
      "protein_count_per_meal_output": "40g",
      "fats_count_per_meal": "15g",
      "price_per_meal": 3.4,
      "ingredients": "Chicken Breast, Potatoes, Carrots, Curry Powder, Onion, Garlic, Cooking Oil, Jasmine Rice"
    },
    {
      "dish_name": "Tofu and Egg Donburi Bowl",
      "cuisine": "Japanese",
      "recipe": "1. Slice 300g firm tofu and 1/2 onion. 2. In a skillet, simmer sliced onions in 1/2 cup water, 1 tbsp soy sauce, and a pinch of sugar. 3. Add tofu slices and cook for 3 minutes. 4. Beat 2 eggs and pour over the simmering mixture. Cover and cook on low heat until eggs are softly set. 5. Slide over a warm bowl of rice and garnish with spring onions.",
      "calorie_count_per_meal_output": "510 kcal",
      "protein_count_per_meal_output": "28g",
      "fats_count_per_meal": "16g",
      "price_per_meal": 2.2,
      "ingredients": "Firm Tofu, Fresh Eggs, Onion, Spring Onions, Light Soy Sauce, Jasmine Rice"
    },
    {
      "dish_name": "Classic Egg and Vegetable Fried Rice",
      "cuisine": "Chinese",
      "recipe": "1. Heat 1 tbsp oil in a wok. Beat 2 eggs and scramble lightly, then set aside. 2. Sauté minced garlic, 1 diced carrot, and 100g shredded cabbage until crisp-tender. 3. Add 1.5 cups cooled cooked jasmine rice and stir-fry on high heat. 4. Return eggs to wok, season with 1.5 tbsp soy sauce, toss well, and top with chopped spring onions.",
      "calorie_count_per_meal_output": "490 kcal",
      "protein_count_per_meal_output": "18g",
      "fats_count_per_meal": "15g",
      "price_per_meal": 1.9,
      "ingredients": "Jasmine Rice, Fresh Eggs, Carrots, Cabbage, Garlic, Light Soy Sauce, Spring Onions, Cooking Oil"
    }
  ]
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


# Budget Rule
def check_budget_compliance(total_grocery_cost, total_budget):
    total_grocery_cost = parse_number (test_ai_output.get("Total_grocery_cost")) or 0.0
    total_budget = parse_number (test_user_input.get("Total_budget")) or 0.0
    
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
            "fallback_used": True,
            "valid_dishes": dishes,
            "valid_dish_names": [dish.get("dish_name") for dish in dishes],
            "flagged_dishes": flagged
        }
    else:
        return {
            "fallback_used": False,
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
 
        # Budget rule
        budget_result = check_budget_compliance(plan["Total_grocery_cost"], user_input.get("Total_budget"))
        plan["budget"] = budget_result
        if budget_result["status"] == "REJECTED":
            plan["warnings"].append(budget_result["reason"])
 
        # Filter 1: dietary safety
        diet = filter_dishes_by_dietary_rules(dishes, user_input.get("Diet_restriction"))
        safe_dishes = []
        for dish in dishes:
            if isinstance(dish, dict) and dish.get("dish_name") in diet["valid_dish_names"]:
                 safe_dishes.append(dish)
 
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
    while True:
        budget = check_budget_compliance(test_user_input, test_ai_output)
        print(budget["status"])
        print(budget["reason"])

        restrictions = filter_dishes_by_dietary_rules(test_ai_output["Dishes"], test_user_input["Dietary_restrictions"])
        print("Valid dishes list:", restrictions["valid_dish_names"])
        print("Flagged items details:", restrictions["flagged_dishes"])
        
        nutrition = filter_dishes_by_nutrition(test_dishes, "High Protein")
        print(nutrition["valid_dish_names"])
        print(nutrition["flagged_dishes"])

        cuisine = filter_dishes_by_cuisine(nutrition["valid_dishes"], ("Anything",))
        print(cuisine["valid_dish_names"])
        print(cuisine["fallback_used"])
        break