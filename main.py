<<<<<<< Updated upstream
import aiManager
import dataManager
import inputManager
import logicManager
=======
import json
from aiManager import GeminiAPI
from inputManager import InputManager
from Saved_MealPlans import Saved_MealPlans
from logic.logic_manager import LogicManager
from logic.user_profile import UserProfile
>>>>>>> Stashed changes

inputManager.welcome_msg()

while True:
    choice = inputManager.main_menu()

<<<<<<< Updated upstream
    if choice is None:
        continue
=======
class Main:

    __MEAL_PLANS = "meal_history.json"
    __PLAN_KEYS = ("pax", "Total_grocery_cost", "Grocery_list", "Dishes")

    def __init__(self, test_mode=False):
        self.__test_mode = test_mode
        self.__saved_plans = Saved_MealPlans()
        self.__input_manager = InputManager()
        self.__logic_manager = LogicManager()



    # Test Mode Enabled function for test.py
    def set_test_mode(self, enabled=True):
        self.__test_mode = enabled

    def get_test_mode(self):
        return self.__test_mode

    # Runs the program until the user exits
    def run(self):
        self.__input_manager.welcome_msg()


        while True:
            choice = self.__main_menu()

            #Option 1: Generate Meal Plan
            if choice == 1:
                self.__generate_meal_plan()

            #Option 2: Manage Meal Plans
            elif choice == 2:
                self.__manage_meal_plans()

            #Option 3: Get Feedback on a Previous Meal Plan
            elif choice == 3:
                self.__get_feedback()

            # Quit Program
            elif choice == 4:
                print("Goodbye!")
                break


    def __main_menu(self):
        print("\nMain Menu")
        print("-" * 30)
        print("1. Generate Meal Plan\n2. Manage Meal Plans\n3. Get Feedback on a Previous Meal Plan\n4. Exit")

        while True:
            choice = input("\nPlease select an option (1-4): ").strip()

            if choice.isdigit() and 1 <= int(choice) <= 4:
                return int(choice)

            print("Invalid choice. Please select 1-4.")

    #Function to call AImanager and handle both test mode and regular mode
    def __request_ai(self, ai, prompt_type, previous_plan=None):
        
        # Test mode: no prompt is crafted and Hardcoded values are used
        if self.__test_mode:
            if prompt_type == "feedback":
                message = ai.hardcode_feedback_meal_plan()
            else:
                message = ai.hardcode_normal_meal_plan()

            if message:
                print(message)
                return False

            if ai.generate_meal_plan() is None:
                return False

            return True

        # Regular mode: craft the prompt and call the AI
        if prompt_type == "feedback":
            ai.craft_feedback_prompt(previous_plan)
        else:
            ai.craft_prompt()

        return ai.call_api(prompt_type)

>>>>>>> Stashed changes
    
    #Option 1: Generate Meal Plan
    if choice == 1:
        user_input = inputManager.main_input() #Input Prompt and Validation

        if user_input is None: # Error Handling if user_input is empty
            continue

<<<<<<< Updated upstream
        exclude = None # Initialise exclude as None, assuming user first generation
=======
        if user_input is None:
            return

        # Build the user's profile once; it stays the same across regenerations
        profile = UserProfile.from_input_list(user_input)

        exclude = None # assuming user first time generating a meal plan, no exclusions yet
>>>>>>> Stashed changes

        while True:
            # Prompt Creation and Call for AI API
            prompt = aiManager.craftprompt(user_input[2],user_input[1],user_input[7],exclude)
            ai_output = aiManager.GeminiAPI(prompt)

            # Error Handling if AI Output has an error
            if "error" in ai_output:
                print("Error found:", ai_output)

                #User regeneration request if error is found
                if inputManager.ask_regenerate():
                    continue
                else:
                    break
            
            # Logic Manager processes ai_output
            plan = logicManager.get_filtered_plan(ai_output, user_input)

<<<<<<< Updated upstream
            inputManager.display_plan_messages(plan) # Flags and Rejects

            #if AI output is all rejected for flagged, ask for regeneration
            if plan["outcome"] == "REJECTED":
                print("Unable to generate a valid meal plan.")

                if inputManager.ask_regenerate():
=======
            ai_output = ai.generate_meal_plan()

            # Logic Manager checks the AI output against the user's profile (Brandon)
            plan = self.__logic_manager.evaluate(ai_output, profile)

            # Show removed dishes, rejection reason and warnings
            self.__input_manager.display_plan_messages(plan)

            #if AI output is all rejected for flagged, ask for regeneration
            if plan["outcome"] == "REJECTED":
                if self.__input_manager.ask_regenerate():
>>>>>>> Stashed changes
                    continue
                else:
                    break

            inputManager.display_generated_meal_plan(user_input, plan)

            response, plan_to_save, exclude = inputManager.get_accept_reject_menu(plan, "Accept? (y/n): ", user_input ,dataManager)
            
            # regenerate if user rejects meal plan
            if response == "n":
                if inputManager.ask_regenerate():
                    continue
                else:
                    exclude = None
                    break

            else:
                print("Invalid response.")
                break

    
    elif choice == 2:
        while True:
            #Manage Meal Plan Menu
            saved_choice = inputManager.manage_plans_menu()

            if saved_choice is None:
                continue
            #Back to Main Menu
            if saved_choice == 6:
                break

            #View All Saved Meal Plans
            elif saved_choice == 1:
                meal_plans = "meal_history.json"

                inputManager.display_all_plans(meal_plans)

                selected_plan = inputManager.get_selected_plan(meal_plans)

                if selected_plan is None:
                    continue

                inputManager.display_meal_plan(selected_plan)
                inputManager.get_selected_recipe(selected_plan)

            # Filter by Name
            elif saved_choice == 2:
                name = inputManager.get_name_filter()

                filtered_plans = dataManager.filter_by_name(name)

                inputManager.display_filtered_plans(filtered_plans)

                selected_plan = inputManager.get_selected_filtered_plan(filtered_plans)

                if selected_plan is None:
                    continue

                inputManager.display_meal_plan(selected_plan)
                inputManager.get_selected_recipe(selected_plan)

            #Filter by Budget
            elif saved_choice == 3:
                budget = inputManager.get_budget_filter()

                filtered_plans = dataManager.filter_by_budget(budget)

                inputManager.display_filtered_plans(filtered_plans)

                selected_plan = inputManager.get_selected_filtered_plan(filtered_plans)

                if selected_plan is None:
                    continue

                inputManager.display_meal_plan(selected_plan)
                inputManager.get_selected_recipe(selected_plan)

            #Change Name of Meal Plan
            elif saved_choice == 4:
                meal_plans = "meal_history.json"

                inputManager.display_all_plans(meal_plans)

                selected_plan = inputManager.get_selected_plan(meal_plans)

                if selected_plan is None:
                    continue

                new_name = inputManager.change_meal_plan_name(selected_plan)

                if new_name:
                    dataManager.update_meal_plan_name(selected_plan["id"], new_name)

            # Delete Meal Plan
            elif saved_choice == 5:
                inputManager.delete_meal_plan("meal_history.json")

    # Quit Program
    elif choice == 3:
        print("Goodbye!")
        break
