import json
from aiManager import GeminiAPI
from inputManager import InputManager
from Saved_MealPlans import Saved_MealPlans
from mysql_storage import MySQLStorage


class Main:

    def __init__(self, test_mode=False):
        self.__test_mode = test_mode
        self.__saved_plans = Saved_MealPlans(storage = MySQLStorage())
        self.__input_manager = InputManager(self.__saved_plans)


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

    

    # Option 1: Generate Meal Plan
    def __generate_meal_plan(self):
        user_input = self.__input_manager.main_input() 

        if user_input is None:
            return
        

        exclude = None # assuming user first time generating a meal plan, no exclusions yet

        while True:
            ai = GeminiAPI(user_input[2], user_input[1], user_input[7], exclude)

            # Error Handling if the AI call fails
            if not self.__request_ai(ai, "generate"):

                #User regeneration request if error is found
                if self.__input_manager.ask_regenerate():
                    continue
                else:
                    break

            ai_output = ai.generate_meal_plan()

            # Logic Manager processes ai_output (Brandon To Add New Codes)
            plan = ai_output  # Placeholder for actual logic processing

            #if AI output is all rejected for flagged, ask for regeneration
            if plan["outcome"] == "REJECTED":
                print("Unable to generate a valid meal plan.")

                if self.__input_manager.ask_regenerate():
                    continue
                else:
                    break

            self.__input_manager.display_generated_meal_plan(user_input, plan)

            response, plan_to_save, exclude = self.__input_manager.get_accept_reject_menu(plan, "Accept? (y/n): ", user_input)

            # regenerate if user rejects meal plan
            if response == "n":
                if self.__input_manager.ask_regenerate():
                    continue
                else:
                    exclude = None
                    break

            else:
                saved_id = self.__saved_plans.add_MealPlan(plan_to_save, self.__sql_user_input(user_input))
                if saved_id is None:
                    print("Warning: Failed to save the meal plan.")
                else:
                    print(f"Meal plan saved successfully! ID: {saved_id}")
                    # Export the saved record with its database ID and date.
                    saved_plan = self.__saved_plans.get_MealPlan(saved_id)
                    self.__input_manager.offer_pdf_export(saved_plan or plan_to_save, user_input)
                break
            
#OPtion 2: Manage Meal Plans
    def __manage_meal_plans(self):
        while True:
            saved_choice = self.__input_manager.manage_plans_menu()
            if saved_choice is None:
                continue
            if saved_choice == 8:
                break

            records = self.__saved_plans.get_all_MealPlans()
            if saved_choice in (1, 4, 5, 7) and not records:
                print("\nNo saved meal plans yet.")
                continue

            if saved_choice == 1:
                self.__input_manager.display_all_plans(records)
                selected = self.__input_manager.get_selected_plan(records)
                if selected is not None:
                    self.__view_saved_plan(selected)

            elif saved_choice == 2:
                name = self.__input_manager.get_name_filter()
                matches = self.__saved_plans.filter_MealPlans_by_name(name)
                self.__view_filtered_plans(matches)

            elif saved_choice == 3:
                budget = self.__input_manager.get_budget_filter()
                matches = self.__saved_plans.filter_MealPlans_by_budget(budget)
                self.__view_filtered_plans(matches)

            elif saved_choice == 4:
                self.__input_manager.display_all_plans(records)
                selected = self.__input_manager.get_selected_plan(records)
                if selected is not None:
                    new_name = self.__input_manager.change_meal_plan_name(selected)
                    if self.__saved_plans.rename_MealPlan(selected["id"], new_name):
                        print("Meal plan renamed successfully!")
                    else:
                        print("Unable to rename meal plan.")

            elif saved_choice == 5:
                selected_id = self.__input_manager.delete_meal_plan(records)
                if selected_id is not None:
                    if self.__saved_plans.delete_MealPlan(selected_id):
                        print("Meal plan deleted successfully!")
                    else:
                        print("Unable to delete meal plan.")

            elif saved_choice == 6:
                self.__get_feedback()

            elif saved_choice == 7:
                self.__input_manager.display_all_plans(records)
                selected = self.__input_manager.get_selected_plan(records)
                if selected is not None:
                    self.__input_manager.offer_pdf_export(selected)

    def __view_saved_plan(self, plan):
        self.__input_manager.display_meal_plan(plan)
        self.__input_manager.get_selected_recipe(plan)

    def __view_filtered_plans(self, plans):
        self.__input_manager.display_filtered_plans(plans)
        if plans:
            selected = self.__input_manager.get_selected_filtered_plan(plans)
            if selected is not None:
                self.__view_saved_plan(selected)

    def __get_feedback(self):
        # Retrieve saved plans before requesting feedback from the AI
        records = self.__saved_plans.get_all_MealPlans()
        if not records:
            print("\nNo saved meal plans available for feedback.")
            return

        self.__input_manager.display_all_plans(records)
        previous_plan = self.__input_manager.get_selected_plan(records)
        if previous_plan is None:
            return

        # Use the saved profile details to configure the feedback request
        user_input = [
            previous_plan.get("name", "User"),
            previous_plan.get("budget", 0),
            previous_plan.get("pax", 1),
            previous_plan.get("dietary_restrictions", ("None",)),
            previous_plan.get("dietary_goal", ("Standard",)),
            previous_plan.get("calorie_count", 650),
            previous_plan.get("cuisine", ("Anything",)),
            previous_plan.get("country", "Singapore"),
            previous_plan.get("protein_count", 27),
            previous_plan.get("fat_count", 20),
        ]
        # Keep the selected saved plan and profile when regenerating feedback.
        while True:
            ai = GeminiAPI(user_input[2], user_input[1], user_input[7], None)
            if not self.__request_ai(ai, "feedback", previous_plan):
                print("Unable to generate feedback. Please try again.")
                if self.__input_manager.ask_regenerate():
                    continue
                return

            feedback = ai.generate_meal_plan()
            if isinstance(feedback, str):
                try:
                    feedback = json.loads(feedback)
                except json.JSONDecodeError:
                    print("Unable to read the AI feedback.")
                    if self.__input_manager.ask_regenerate():
                        continue
                    return

            if not isinstance(feedback, dict):
                print("The AI returned an invalid feedback response.")
                if self.__input_manager.ask_regenerate():
                    continue
                return

            if feedback.get("Error") and str(feedback["Error"]).strip().lower() not in ("none", "null", "no error", "n/a", "", "false", "nil", "na"):
                print("Feedback error:", feedback["Error"])
                if self.__input_manager.ask_regenerate():
                    continue
                return

            # Logic Manager processes ai_output (Brandon To Add New Codes)
            # Leave Logic Manager integration to Brandon.
            if feedback.get("outcome") in ("REJECTED", "FLAGGED"):
                self.__input_manager.display_plan_messages(feedback)
                print("The improved meal plan was rejected or flagged.")
                if self.__input_manager.ask_regenerate():
                    continue
                return

            self.__input_manager.display_feedback(feedback)
            if not isinstance(feedback.get("Dishes"), list) or not feedback["Dishes"]:
                print("No improved dishes were returned to save.")
                if self.__input_manager.ask_regenerate():
                    continue
                return

            self.__offer_to_save(feedback, user_input)
            return

    # Convert menu choices into database-compatible values before saving.
    # dietary_goal and cuisine are VARCHAR columns; restrictions are JSON.
    @staticmethod
    def __sql_user_input(user_input):
        values = list(user_input)
        for index in (4, 6):
            choice = values[index]
            if isinstance(choice, (tuple, list)):
                values[index] = ", ".join(str(item) for item in choice)
        restrictions = values[3]
        if isinstance(restrictions, tuple):
            values[3] = list(restrictions)
        return values

    # Option to save the improved meal plan
    def __offer_to_save(self, plan, user_input):
        while True:
            save_choice = self.__input_manager.ask_save_improved_plan()
            if not save_choice:
                print("Improved meal plan was not saved.")
                self.__input_manager.offer_pdf_export(plan, user_input)
                return

            # Save as a new plan; the original saved meal plan is not overwritten.
            saved_id = self.__saved_plans.add_MealPlan(plan, self.__sql_user_input(user_input))
            
            if saved_id is None:
                print("Warning: Failed to save the improved meal plan.")
            else:
                print(f"Improved meal plan saved successfully! ID: {saved_id}")
                saved_plan = self.__saved_plans.get_MealPlan(saved_id)
                self.__input_manager.offer_pdf_export(saved_plan or plan, user_input)
            return
