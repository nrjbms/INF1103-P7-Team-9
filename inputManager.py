import pycountry
import re
import pdfmaker

class InputManager:
    # Welcome Message to JustEat
    def welcome_msg(self):
        print()
        print("=" *50)
        print("Welcome to JustEat!")
        print("Budget Meal Planner")
        print("=" *50)

    # Name
    def __get_name_input(self, name_input): 
        # Prompt user for their names
        name_input = input(name_input)
        # Allows user to quit
        if name_input.lower() == "quit":
            return "quit"
        else:
            return name_input

    # budget,
    __MIN_BUDGET = 9.99
    def __get_budget_input(self, budget_input):
        # Prompt user for their budget
        budget_input = input(budget_input)
        # Validates if budget is a number/float
        try:
            budget_input = float(budget_input)
        except ValueError:
            print("Error. Please enter a valid number")
            return None
        # Rejects budget if budget is too small
        if budget_input <= self.__MIN_BUDGET:
            print("It will be difficult to suggest meal plans with such a small budge. Please allocate more budget and try again.")
            return None
        else:
            return budget_input

    # pax per,
    def __get_pax_input(self, pax_input):
        # Prompt user for their pax
        pax_input = input(pax_input)
        # Validates if pax is a number and if pax entered is bigger than 0
        if pax_input.isdigit() and int(pax_input) > 0:
            return int(pax_input)
        else:
            print("Error. Please enter a valid number.")
            return None

    # dietary restrictions,
    def __open_restrictions_menu(self):
        # Displays dietary restriction menu, allows user to select mulitple restrictions
        restrictions_selected = self.__prompt_menu("Dietary Restrictions Menu", self.__RESTRICTIONS, multiple=True)
        if restrictions_selected is None:
            print("No dietary restriction selected.")
            # Returns ('None',) if users press Enter to skip
            return ('None',)
        print("Selected Dietary Restrictions: ", restrictions_selected)
        # Returns tuple of selected restriction
        return restrictions_selected

    # meal goal,
    def __open_goal_menu(self):
        # Displays dietary goals menu, only allows user to select one option
        goals_selected = self.__prompt_menu("Dietary Goal Menu", self.__GOALS, multiple=False)
        if goals_selected is None:
            # Returns ('None',) if users press Enter to skip
            return ('None',)
        print("Selected Dietary Goals: ", goals_selected)
        # Returns a one-item tuple with selected goal
        return goals_selected

    __PRESET_MACROS = {
        "Standard": (650, 27, 20),
        "Low Calories": (500, 22, 15),
        "High Protein": (800, 35, 25),
    }
    __DEFAULT_MACROS = __PRESET_MACROS["Standard"]

    def __minimum_goals(self, prompt, minimum, error_msg):
        while True:
            raw = input(prompt)
            if raw.isdigit() and int(raw) >= minimum:
                return int(raw)
            print(error_msg)

    def __print_macros(self, calories, protein, fat):
        print(f"Calorie Count: {calories}kcal")
        print(f"Protein Count: {protein}g")
        print(f"Fat Count: {fat}g")

    def __get_calorie_count(self, selected_goals): 
        # Uses the selected goal to determine calorie, protein, and fat count
        goal = selected_goals[0] if len(selected_goals) == 1 else None
        if goal in self.__PRESET_MACROS:
            calories, protein, fat = self.__PRESET_MACROS[goal]
            self.__print_macros(calories, protein, fat)

        elif goal == "Custom Macros":
            # Allows user to input their desired macros
            # Loops until user inputs the appropriate calorie values
            calories = self.__minimum_goals(
                "Enter calorie goal (kcal): ", 350,
                "Please have at least 350kcal to receive sufficient nutrients.\n")
            protein = self.__minimum_goals(
                "Enter protein goal (g): ", 20,
                "Please have at least 20g of protein to receive sufficient nutrients.\n")
            fat = self.__minimum_goals(
                "Enter fat goal (g): ", 10,
                "Please have at least 10g of fat to receive sufficient nutrients.\n")
 
            print("\n--- Goals Set ---")
            self.__print_macros(calories, protein, fat)
 
        elif goal == "None":
            print("Since you have not selected a calorie goal, Standard will be chosen")
            calories, protein, fat = self.__DEFAULT_MACROS
            self.__print_macros(calories, protein, fat)
 
        else:
            print("Goal not defined. Standard will be chosen")
            calories, protein, fat = self.__DEFAULT_MACROS
            self.__print_macros(calories, protein, fat)
 
        return calories, protein, fat

    #Cuisine
    def __open_cuisine_menu(self):
        # Displays cuisine menu, allows user to select mulitple cuisine
        cuisine_selected = self.__prompt_menu("Cuisine Menu", self.__CUISINE, multiple=True)
        if cuisine_selected is None:
            # Returns ('Anything',) if users press Enter to skip
            print("No cuisine selected. Anything will be chosen")
            return ('Anything',)
        print("Selected Cuisine: ", cuisine_selected)
        # Returns tuple of selected cuisine
        return cuisine_selected


    # Selection Menu
    # Tuples used to keep choices fixed and ordered
    # Choices shown in dietary restriction menu
    __RESTRICTIONS = ("Seafood", "Nuts", "Dairy", "Wheat", "Eggs", "Halal")
    # Choices shown in dietary goal menu
    __GOALS = ("Standard", "Low Calories", "High Protein", "Custom Macros")
    # Choices shown in cuisine menu
    __CUISINE = ("Anything", "Chinese", "Malay", "Indian", "Japanese", "Thai",
            "Korean", "Vietnamese", "Italian", "Mexican", "Western")

    def __prompt_menu(self, title, options, multiple):
        # Displays each menu according to their title
        print(f"\n------[{title}]------")
        # Numbering starts at 1
        for i, item in enumerate(options, 1):
            print(f"{i}. {item}")

        # Displays prompt text based on multi/single select menu
        if multiple:
            prompt = "Enter number(s) separated by commas (or press Enter to skip): "
        else:
            prompt = "Enter a number (or press Enter to skip): "

        # Loops until a valid option or a skip is selected
        while True:
            raw = input(prompt).strip()

            # An empty input will skip the menu
            if raw == "":
                return None

            # Splits "1, 3,4" into ["1", "3", "4"], ignoring blank spaces
            parts = [p.strip() for p in raw.split(",") if p.strip()]

            # Validates if there is at least one part and every part is a number within the menu range
            valid = bool(parts) and all(
                p.isdigit() and 1 <= int(p) <= len(options) for p in parts
            )
            if not valid:
                print(f"Error. Please enter number(s) between 1 and {len(options)}.")
                continue

            # Ensures not more than one option is selected for single select menu
            if not multiple and len(parts) > 1:
                print("Error. Please choose only one option.")
                continue

            # Convert 1-based numbers to 0-based indexes; set() removes duplicates and sorted() keeps menu order
            indexes = sorted(set(int(p) - 1 for p in parts))
            return tuple(options[i] for i in indexes)

    # country/currency,
    def __get_country_input(self, country_input):
        # Prompts for a country and validates it with pycountry.
        country_input = input(country_input)
        # Rejects numbers
        if country_input.isdigit():
            print("Error, invalid. Please enter a valid country.")
            return "country_error"
        else:
            # Tries each look up for pycountry in order
            try:
                country_validation =  (pycountry.countries.get(name=country_input)
                                        or pycountry.countries.get(official_name=country_input)
                                        or pycountry.countries.get(alpha_2=country_input.upper())
                                        or pycountry.countries.get(alpha_3=country_input.upper()))
                if country_validation:
                    # Returns country's standard name if valid
                    return country_validation.name
                else:
                    print("Error, invalid. Please enter a valid country.")
                    return "country_error"
            # Rejects invalid input
            except LookupError:
                print("Error, country not found. Please enter a valid country.")
                return "country_error"

    # Runs full input flow
    def main_input(self):
        while True:

            # Name/Quit
            name_input = self.__get_name_input("Enter name (Enter 'quit' to quit): ").strip()
            if not name_input:
                print("Name cannot be empty. Please try again.")
                continue
            if name_input.lower() == "quit":
                return None
            else:
                print("Welcome: ", name_input)

            budget_input = None
            while not isinstance(budget_input, float):
                budget_input = self.__get_budget_input("Enter Budget (Min $10.0): ")
            print("Your budget is:", budget_input)
 
            pax_input = None
            while not isinstance(pax_input, int):
                pax_input = self.__get_pax_input("Enter Pax: ")
            print("Number of pax: ", pax_input)

            # restriction, cuisine, goals menu
            selected_restrictions = self.__open_restrictions_menu()
            
            selected_cuisine = self.__open_cuisine_menu()

            selected_goals = self.__open_goal_menu()

            # Turns the chosen goal into calorie/protein/fat counts
            calorie_count, protein_count, fat_count = self.__get_calorie_count(selected_goals)

            # Loops until the error value isn't returned
            while True:
                country_input = self.__get_country_input("\nEnter country: ")
                if not country_input == "country_error":
                    print("Selected Country: ", country_input)
                    break   

            # Prints all inputs and returns all inputs as a list
            combined_input = [name_input, budget_input, pax_input, selected_restrictions, selected_goals, calorie_count, selected_cuisine, country_input, protein_count, fat_count]
            all_input = (combined_input)

            print()
            print("         MEAL PLANNER PROFILE SEARCH        ")
            print("="*40)
            print(f"User Name: {name_input}")
            print(f"Total Budget: ${budget_input:.2f}")
            print(f"Number of Pax: {pax_input}")
            print(f"Dietary Restrictions: {selected_restrictions}")
            print(f"Cuisine: {selected_cuisine}")
            print(f"Dietary Goal: {selected_goals}")
            print(f"Calories: {calorie_count}kcal")
            print(f"Protein: {protein_count}g")
            print(f"Fats: {fat_count}g")
            print(f"Target Country: {country_input}")
            print("="*40)
            return all_input



    # Printing AI Output
    def display_generated_meal_plan(self, user_input, ai_output):

        print()
        print(f"Meal Plan for {user_input[0]}")
        print("-" * 30)

        print(f"\nBudget: ${user_input[1]:.2f}")
        print(f"Pax: {user_input[2]}")
        print(f"Dietary Restrictions: {user_input[3]}")
        print(f"Dietary Goal: {user_input[4]}")
        print(f"Calories: {user_input[5]}kcal")
        print(f"Protein: {user_input[8]}g")
        print(f"Fats: {user_input[9]}g")
        print(f"Cuisine: {user_input[6]}")
        print(f"Country: {user_input[7]}")

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


    # Display One Meal Plan
    def display_meal_plan(self, plan):

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

    # Display saved meal plans supplied by the data manager
    def display_all_plans(self, meal_plans):
        print("\nSaved Meal Plans")
        print("-" * 30)
        
        if not meal_plans:
            print("No saved meal plans yet.")
            return
        
        for plan in meal_plans:
            self.__print_plan_summary(plan)

    def __print_plan_summary(self, plan):
        
        cost = plan.get("Total_grocery_cost")
        
        cost_text = f"${float(cost):.2f}" if cost is not None else "N/A"
        
        print(f"{plan.get('id', 'N/A')}: Meal Plan for {plan.get('name', 'N/A')} "
              f"({plan.get('pax', 'N/A')} pax) - {cost_text} "
              f"[{plan.get('date', 'N/A')}]")

    # Select an existing plan from the supplied records
    def get_selected_plan(self, meal_plans):
        
        if not meal_plans:
            print("No meal plans available to select.")
            return None
        
        while True:
            choice = input("\nEnter a meal plan ID (or 'back' to return): ").strip()
            
            if choice.lower() == "back":
                return None
            
            for plan in meal_plans:
                if str(plan.get("id")) == choice:
                    return plan
                
            print("Invalid input. Please enter a valid ID.")

    # display recipe details for one meal plan
    def display_recipe_details(self, recipe):
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

    # Export a generated, saved, or improved meal plan as a PDF.
    def offer_pdf_export(self, plan, user_input=None):
        
        while True:
            answer = input("\nExport this meal plan as a PDF? (y/n): ").strip().lower()
            if answer in ("n", "no"):
                return False
            if answer in ("y", "yes"):
                
                if not isinstance(plan, dict):
                    print("No valid meal plan available to export.")
                    return False
                
                export_plan = plan.copy()
                
                if user_input is not None:
                    export_plan.setdefault("name", user_input[0])
                    export_plan.setdefault("pax", user_input[2])
                    
                export_plan.setdefault("name", "User")
                export_plan.setdefault("pax", 1)
                export_plan.setdefault("date", __import__("datetime").date.today().isoformat())
                
                filename = input("Enter filename for the PDF: ").strip()
                if filename == "":
                    print("Filename cannot be empty. Please try again.")
                    continue
                
                try:
                    pdfmaker.PDF(export_plan, filename).makepdf()
                except (OSError, ValueError, TypeError, KeyError, ImportError) as error:
                    print(f"Unable to export PDF: {error}")
                    return False
                
                print(f"PDF exported: {filename}.pdf")
                return True
            
            print("Invalid input. Please enter Y or N.")

    # validation for what recipe user would like to view
    def get_selected_recipe(self, plan):
        while True:
            choice = input(
                "\nEnter a recipe number to view ('back' to return): ").strip().lower()
            
            if choice == "back":
                return False
            
            if choice.isdigit() and 1 <= int(choice) <= len(plan.get("Dishes", [])):
                self.display_recipe_details(plan["Dishes"][int(choice) - 1])
            else:
                print("\nInvalid input. Please enter a valid number or 'back'.")

    # Option 2: Manage Meal Plans menu            
    def manage_plans_menu(self):
        print("\nManage Meal Plans")
        print("-" * 50)
        print("1. View All Plans")
        print("2. Filter by Name")
        print("3. Filter by Budget")
        print("4. Rename Meal Plan")
        print("5. Delete Meal Plan")
        print("6. Get Feedback")
        print("7. Export Meal Plan to PDF")
        print("8. Back to Main Menu")

        choice = input("\nPlease select an option (1-8): ")

        if choice.isdigit() and 1 <= int(choice) <= 8:
            return int(choice)

        print("Invalid choice. Please select 1-8.")
        return None


    # Display filtered meal plans and select from the results
    def display_filtered_plans(self, filtered_plans):
        print("\nFiltered Saved Meal Plans")
        print("-" * 50)
        
        if not filtered_plans:
            print("No matching meal plans found.")
            return
        
        for plan in filtered_plans:
            self.__print_plan_summary(plan)

    def get_selected_filtered_plan(self, filtered_plans):
        return self.get_selected_plan(filtered_plans)

    # regeneration prompt and validation
    def ask_regenerate(self):
        while True:
            again = input("\nDo you want to regenerate? (Yes/No): ").strip().lower()

            if again == "yes":
                return True
            elif again == "no":
                return False
            else:
                print("\nInvalid input. Please enter Yes or No.")

    # validation to change name of meal plan
    def change_meal_plan_name(self, plan):
        print("\nChange Meal Plan Name")
        print("-" * 30)
        print(f"Current name: {plan.get('name', 'N/A')}")

        while True:
            new_name = input("\nEnter the new name: ").strip()

            if new_name:
                return new_name
            else:
                print("\nName cannot be empty. Please try again.")

    # Confirm deletion; the Main class handles storage changes
    def delete_meal_plan(self, meal_plans):
        self.display_all_plans(meal_plans)
        
        selected_plan = self.get_selected_plan(meal_plans)
        
        if selected_plan is None:
            return None
        
        print(f"\nSelected meal plan: {selected_plan.get('name', 'N/A')}")
        
        while True:
            confirm = input("Are you sure you want to delete this meal plan? (yes/no): ").strip().lower()
            
            if confirm == "yes":
                return selected_plan["id"]
            
            if confirm == "no":
                print("Deletion cancelled.")
                
                return None
            print("Invalid input. Please enter Yes or No.")

    # input validationfor name for filtering to match for dataManager function
    def get_name_filter(self):
        user_input = input("\nEnter the name to search for: ").strip()
        if user_input == "":
            print("\nName cannot be empty. Please try again.")
            return self.get_name_filter()
        return user_input

    # input validation for budget for filtering to match for dataManager function
    def get_budget_filter(self):
        while True:
            try:
                budget = float(input("\nEnter the budget to filter by: $"))

                if budget < 0:
                    print("\nBudget cannot be negative.")
                else:
                    return budget

            except ValueError:
                print("\nInvalid budget. Please enter a number.")


    __PLAN_KEYS = ("pax", "Total_grocery_cost", "Grocery_list", "Dishes")
        # plan: dict with keys such as "Dishes", "Grocery_list", etc.
        # dish_selection_prompt: the y/n prompt shown to the user
        # user_input: the user's profile
    def get_accept_reject_menu(self, plan, dish_selection_prompt, user_input):
        
        # Saving is handled by Main through Saved_MealPlans.
        if not isinstance(plan, dict):
            plan = {}
            
        while True:
            response = input(dish_selection_prompt).strip().lower()
            
            if response == "y":
                plan_to_save = {key: plan[key] for key in self.__PLAN_KEYS if key in plan}
                self.view_generated_recipes(plan, user_input)
                return "y", plan_to_save, None
            
            if response == "n":
                exclude = input("What would you like excluded? ").strip()
                print("Excluded:", exclude)
                return "n", None, exclude
            print("Error. Please select y/n.")

    def view_generated_recipes(self, plan, user_input=None):
        dishes = [d for d in plan.get("Dishes", []) if isinstance(d, dict)]
        
        if not dishes:
            print("No dishes available to view.")
            return
        print("\nDishes in your plan:")
        for index, dish in enumerate(dishes, 1):
            print(f"{index}. {dish.get('dish_name', 'Unnamed dish')}")
        while True:
            choice = input("Enter a dish number to view its recipe, or 'back' to return: ").strip()
            if not choice:
                return
            if choice.lower() == "back":
                return
            elif choice.isdigit() and 1 <= int(choice) <= len(dishes):
                self.display_recipe_details(dishes[int(choice) - 1])
            else:
                print("Invalid dish number.")

    # Show the logic manager's results: removed dishes, rejection reason and warnings (brandon)
    def display_plan_messages(self, plan):
        for flagged in plan.get("flagged_dishes", []):
            print(f"Removed '{flagged['dish_name']}': {flagged['reason']}")

        if plan.get("outcome") == "REJECTED":
            print("Plan rejected:", plan.get("Error", "Unknown reason"))
            return

        for warning in plan.get("warnings", []):
            print("Warning:", warning)
            
            
    # Display AI feedback and the improved meal plan
    def display_feedback(self, feedback):
        print("\nNutritional Feedback")
        print("-" * 30)
        print(feedback.get("observation") or "No nutritional observation provided.")

        print("\nSuggested Improved Meal Plan")
        print("-" * 30)
        
        cost = feedback.get("Total_grocery_cost", 0)
        
        try:
            print(f"Total Grocery Cost: ${float(cost):.2f}")
        except (TypeError, ValueError):
            print(f"Total Grocery Cost: {cost}")

        print("\nGrocery List:")
        for item in feedback.get("Grocery_list", []):
            if isinstance(item, dict):
                print(f"- {item.get('ingredient_name', 'Unknown ingredient')} "
                      f"({item.get('Quantity', 'N/A')}) - "
                      f"${item.get('Price_per_ingredient', 'N/A')}")

        print("\nImproved Dishes:")
        for index, dish in enumerate(feedback.get("Dishes", []), 1):
            if isinstance(dish, dict):
                print(f"{index}. {dish.get('dish_name', 'Unnamed dish')} "
                      f"[{dish.get('cuisine', 'Unknown cuisine')}]")
        self.view_generated_recipes(feedback)

    # Ask whether the improved meal plan should be saved
    def ask_save_improved_plan(self):
        while True:
            choice = input("\nSave this improved meal plan? (y/n): ").strip().lower()
            if choice in ("y", "yes"):
                return True
            if choice in ("n", "no"):
                return False
            print("Invalid input. Please enter Y or N.")
