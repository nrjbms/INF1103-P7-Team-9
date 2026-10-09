import pycountry
import json
import re
import dataManager


def welcome_msg():
    print("=" *50)
    print("Welcome to JustEat!")
    print("Budget Meal Planner")
    print("=" *50)

def get_name_input(name_input):
    name_input = input(name_input)
    if name_input.lower() == "quit":
        return "quit"
    else:
        return name_input

# budget,
def get_budget_input(budget_input):
    budget_input = input(budget_input)
    try:
        budget_input = float(budget_input)
        if budget_input <= 9.9:
            print("It will be difficult to suggest meal plans with such a small budge. Please allocate more budget and try again.")
            return
        else:
            return budget_input
    except:
        print("Error. Please enter a valid number")
        return

# pax per,
def get_pax_input(pax_input):
    pax_input = input(pax_input)
    if pax_input.isdigit():
        if int(pax_input) <= 0:
            print("Error. Please enter a valid number.")
        else:
            return int(pax_input)
    else:
        print("Error. Please enter a valid number.")

# dietary restrictions,
def open_restrictions_menu():
    selected = prompt_menu("Dietary Restrictions Menu", RESTRICTIONS, multiple=True)
    if selected is None:
        print("No dietary restriction selected.")
        return ('None',)
    print("Selected Dietary Restrictions: ", selected)
    return selected

# meal goal,
def open_goal_menu():
    selected = prompt_menu("Dietary Goal Menu", GOALS, multiple=False)
    if selected is None:
        return ('None',)
    print("Selected Dietary Goals: ", selected)
    return selected


def get_calorie_count(selected_goals): 

    match selected_goals:
            case('Standard',):
                calorie_count = 650
                protein_count = 27
                fat_count = 20
                print("Calorie Count: ", calorie_count)
                print("Protein Count: ", protein_count)
                print("Fat_Count: ", fat_count)                
            case('Low Calories',):
                calorie_count = 400
                protein_count = 22
                fat_count = 15
                print("Calorie Count: ", calorie_count)
                print("Protein Count: ", protein_count)
                print("Fat_Count: ", fat_count)                
            case('High Protein',):
                calorie_count = 800
                protein_count = 35
                fat_count = 25
                print("Calorie Count: ", calorie_count)
                print("Protein Count: ", protein_count)
                print("Fat_Count: ", fat_count)
            case('Custom Macros',):
                calorie_count = input("Please enter your desired calories(kcal): ")
                protein_count = input("Please enter your desired protein(g):")
                fat_count = input("Please enter your desired fats(g): ")

                if calorie_count.isdigit() and protein_count.isdigit() and fat_count.isdigit:
                    calorie_count = int(calorie_count)
                    protein_count = int(protein_count)
                    fat_count = int(fat_count)
                    print(f"Your selected goals are: ", {calorie_count}, {protein_count}, {fat_count})
                else:
                    print("Goal not defined. Standard will be chosen")
                    calorie_count = 550
                    protein_count = 27
                    fat_count = 20
            case('None',):
                print("Since you have not selected a calorie goal, Standard will be chosen")
                calorie_count = 550    
                protein_count = 27
                fat_count = 20          
            case _:
                print("Goal not defined. Standard will be chosen")
                calorie_count = 550
                protein_count = 27
                fat_count = 20
    return calorie_count, protein_count, fat_count

#Cuisine
def open_cuisine_menu():
    selected = prompt_menu("Cuisine Menu", CUISINE, multiple=True)
    if selected is None:
        print("No cuisine selected. Anything will be chosen")
        return ('Anything',)
    print("Selected Cuisine: ", selected)
    return selected


# Selection Menu
RESTRICTIONS = ("Seafood", "Nuts", "Dairy", "Wheat", "Eggs", "Halal")
GOALS = ("Standard", "Low Calories", "High Protein", "Custom Macros")
CUISINE = ("Anything", "Chinese", "Malay", "Indian", "Japanese", "Thai",
           "Korean", "Vietnamese", "Italian", "Mexican", "Western")

def prompt_menu(title, options, multiple):
    print(f"\n------[{title}]------")
    for i, item in enumerate(options, 1):
        print(f"{i}. {item}")

    if multiple:
        prompt = "Enter number(s) separated by commas (or press Enter to skip): "
    else:
        prompt = "Enter a number (or press Enter to skip): "

    while True:
        raw = input(prompt).strip()

        if raw == "":
            return None

        parts = [p.strip() for p in raw.split(",") if p.strip()]

        valid = bool(parts) and all(
            p.isdigit() and 1 <= int(p) <= len(options) for p in parts
        )
        if not valid:
            print(f"Error. Please enter number(s) between 1 and {len(options)}.")
            continue

        if not multiple and len(parts) > 1:
            print("Error. Please choose only one option.")
            continue

        indexes = sorted(set(int(p) - 1 for p in parts))
        return tuple(options[i] for i in indexes)

# country/currency,
def get_country_input(country_input):
    country_input = input(country_input)
    if country_input.isdigit():
        print("Error, invalid. Please enter a valid country.")
        return "country_error"
    else:
        try:
            country_validation =  (pycountry.countries.get(name=country_input)
                                    or pycountry.countries.get(official_name=country_input)
                                    or pycountry.countries.get(alpha_2=country_input.upper())
                                    or pycountry.countries.get(alpha_3=country_input.upper()))
            if country_validation:
                return country_validation.name
            else:
                print("Error, invalid. Please enter a valid country.")
                return "country_error"
        except LookupError:
            print("Error, country not found. Please enter a valid country.")
            return "country_error"

def main_input():
    while True:
        
        name_input = get_name_input("Enter name (Enter 'quit' to quit): ")
        if name_input == "quit":
            break
        else:
            print("Welcome: ", name_input)

        while True:
            budget_input = get_budget_input("Enter Budget (Min $10.0): ")
            if isinstance(budget_input, float):
                print("Your budget is:", budget_input)
                break

        while True:
            pax_input = get_pax_input("Enter Pax: ")
            if isinstance(pax_input, int):
                print("Number of pax: ", pax_input)
                break

        selected_restrictions = open_restrictions_menu()
        
        selected_cuisine = open_cuisine_menu()

        selected_goals = open_goal_menu()

        calorie_count, protein_count, fat_count = get_calorie_count(selected_goals)

        while True:
            country_input = get_country_input("\nEnter country: ")
            if not country_input == "country_error":
                print("Selected Country: ", country_input)
                break

        combined_input = [name_input, budget_input, pax_input, selected_restrictions, selected_goals, calorie_count, selected_cuisine, country_input, protein_count, fat_count]
        all_input = (combined_input)

        print("         MEAL PLANNER PROFILE SEARCH        ")
        print("="*40)
        print(f"User Name: {name_input}")
        print(f"Total Budget: ${budget_input:.2f}")
        print(f"Number of Pax: {pax_input}")
        print(f"Dietary Restrictions: {selected_restrictions}")
        print(f"Cuisine: {selected_cuisine}")
        print(f"Dietary Goal: {selected_goals}")
        print(f"Calories: {calorie_count} kcal")
        print(f"Protein: {protein_count} g")
        print(f"Fats: {fat_count} g")
        print(f"Target Country: {country_input}")
        print("="*40)
        return all_input

def main_menu():
    while True:
        print("\nMain Menu")
        print("-" * 30)
        print("1. Generate New Meal Plan\n2. View Saved Plans and Recipes\n3. Exit")
        print("-" * 30)

        choice = input("\nPlease select an option (1-3): ")
        print()
        
        if choice.isdigit() and 1 <= int(choice) <= 3:
            return int(choice)

        print("Invalid choice. Please try again.")


# Display the newly generated AI meal plan
def display_generated_meal_plan(user_input, ai_output):

    print()
    print(f"Meal Plan for {user_input[0]}")
    print("-" * 30)

    # User input
    print(f"Budget: ${user_input[1]:.2f}")
    print(f"Pax: {user_input[2]}")
    print(f"Dietary Restrictions: {user_input[3]}")
    print(f"Dietary Goal: {user_input[4]}")
    print(f"Calories: {user_input[5]} kcal")
    print(f"Cuisine: {user_input[6]}")
    print(f"Country: {user_input[7]}")

    # AI output
    print(f"\nTotal Grocery Cost: ${ai_output['Total_grocery_cost']:.2f}")

    print("\nIngredient List:")

    for ingredient in ai_output["Grocery_list"]:
        print(
            f"- {ingredient['ingredient_name']} "
            f"({ingredient['Quantity']} - "
            f"${ingredient['Price_per_ingredient']:.2f})"
        )

    print("\nRecipes:")

    for i, recipe in enumerate(ai_output["Dishes"], 1):
        print(
            f"{i}. {recipe['dish_name']} "
            f"[{recipe['cuisine']}] - "
            f"Est. Price: ${recipe['price_per_meal']:.2f}"
        )


# Display a saved meal plan from the final JSON file
def display_meal_plan(plan):

    print()
    print(f"Meal Plan for {plan['name']}")
    print("-" * 30)

    print(f"Total Grocery Cost: ${plan['Total_grocery_cost']:.2f}")

    print("\nIngredient List:")

    for ingredient in plan["Grocery_list"]:
        print(
            f"- {ingredient['ingredient_name']} "
            f"({ingredient['Quantity']} - "
            f"${ingredient['Price_per_ingredient']:.2f})"
        )

    print("\nRecipes:")

    for i, recipe in enumerate(plan["Dishes"], 1):
        print(
            f"{i}. {recipe['dish_name']} "
            f"[{recipe['cuisine']}] - "
            f"Est. Price: ${recipe['price_per_meal']:.2f}"
        )

def display_all_plans(meal_plans):
    print("-" * 30)
    print("Saved Meal Plans")
    print("-" * 30)

    with open(meal_plans, "r") as file:
        plans = json.load(file)

        for plan in plans:
            print(
                f"{plan['id']}: Meal Plan for {plan['name']} "
                f"({plan['pax']} pax) - "
                f"${plan['Total_grocery_cost']:.2f} "
                f"[{plan['date']}]"
            )


def get_selected_plan(meal_plans):
    with open(meal_plans, "r") as file:
        plans = json.load(file)

    while True:
        choice = input(
            "\nEnter the ID of the meal plan you want to view "
            "(or 'back' to return to the main menu): "
        )

        if choice.lower() == "back":
            return None

        if choice.isdigit():
            choice = int(choice)

            for plan in plans:
                if plan["id"] == choice:
                    return plan

        print("Invalid input. Please enter a valid ID.")


def display_recipe_details(recipe):
    print()
    print("-" * 30)
    print(f"Recipe: {recipe['dish_name']} ({recipe['cuisine']})")
    print("-" * 30)
    print(f"Ingredients: {recipe['ingredients']}")
    print(f"Calories: {recipe['calorie_count_per_meal_output']}")
    print(f"Protein: {recipe['protein_count_per_meal_output']}")
    print(f"Fats: {recipe['fats_count_per_meal']}")
    print(f"Estimated Price: ${recipe['price_per_meal']:.2f}")
    print("\nInstructions:")

    instructions = re.split(r"(?=\d+\.\s)", recipe["recipe"])

    for instruction in instructions:
        if instruction.strip():
            print(instruction.strip())


def get_selected_recipe(plan):
    while True:
        choice = input(
            "\nEnter the number of the recipe you want to view "
            "(or 'back' to return to the meal plan): "
        )

        if choice.lower() == "back":
            return False
        if choice.isdigit() and 1 <= int(choice) <= len(plan["Dishes"]):
            display_recipe_details(plan["Dishes"][int(choice) - 1])
        else:
            print("Invalid input. Please enter a valid number.")

PLAN_KEYS = ("pax", "Total_grocery_cost", "Grocery_list", "Dishes")

def get_accept_reject_menu(plan, dish_selection_prompt, user_input, dataManager):
    if not isinstance(plan, dict):
        plan = {}

    dishes = [dish for dish in plan.get("Dishes", []) if isinstance(dish, dict)]

    dish_selection = input(dish_selection_prompt).strip().lower()

    if dish_selection == 'y':

        plan_to_save = {key: plan[key] for key in PLAN_KEYS if key in plan}
        saved_successfully = dataManager.save_record(user_input, plan_to_save)

        if saved_successfully:
            print("Record saved successfully!")
        else:
            print("Warning: Failed to save the record data.")

        try:
            selected_dish_idx = int(input("Enter the number of the dish to view its recipe: "))
            if 1 <= selected_dish_idx <= len(dishes):
                dish = dishes[selected_dish_idx - 1]
                print(f"\n--- Recipe for {dish.get('dish_name')} ---")
                print(f"Ingredients: {dish.get('ingredients', 'Ingredients not found')}")
                instructions = re.split(r"(?=\d+\.\s)", dish["recipe"])
                for instruction in instructions:
                    if instruction.strip():
                        print(instruction.strip())
            else:
                print("Invalid dish number.")
        except ValueError:
            print("Please enter a valid number.")

        print("Thank you for using our service.")
        return 'y', plan_to_save, dishes

    elif dish_selection == 'n':
        print("We are sorry for the inconvenience.")
        ingredient_exclude = input("What would you like excluded? ")
        print("Excluded: ", ingredient_exclude)
        return 'n', None, ingredient_exclude

    else:
        print("Error. Please select y/n.")
        return dish_selection, None, None
