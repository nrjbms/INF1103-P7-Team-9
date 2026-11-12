import json
from aiManager import GeminiAPI
from inputManager import InputManager
from Saved_MealPlans import Saved_MealPlans
from logic.logic_manager import LogicManager
from logic.user_profile import UserProfile

# No dataManager functions is used yet as database is still being developed. 
# Once the database is ready, the dataManager functions will be called to save and retrieve meal plans.
# InputManager will aslo be updated


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

    

    # Option 1: Generate Meal Plan
    def __generate_meal_plan(self):
        user_input = self.__input_manager.main_input() 

        if user_input is None:
            return

        # Build the user's profile once; it stays the same across regenerations
        profile = UserProfile.from_input_list(user_input)

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

            # Logic Manager checks the AI output against the user's profile (Brandon)
            plan = self.__logic_manager.evaluate(ai_output, profile)

            # Show removed dishes, rejection reason and warnings
            self.__input_manager.display_plan_messages(plan)

            #if AI output is all rejected for flagged, ask for regeneration
            if plan["outcome"] == "REJECTED":
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
                # TO BE ADDED WITH NEW DATABASE METHODS
                
                
                break
            
#OPtion 2: Manage Meal Plans
    def __manage_meal_plans(self):
        while True:
            #Manage Meal Plan Menu
            saved_choice = self.__input_manager.manage_plans_menu()

            if saved_choice is None:
                continue
            #Back to Main Menu
            if saved_choice == 7:
                break

            # Nothing to view, rename or delete if no plan has been saved yet
            if saved_choice in (1, 4, 5) and not self.__saved_plans.get_all_MealPlans():#Need to change to new method for database
                print("\nNo saved meal plans yet.")
                continue

            #View All Saved Meal Plans (New Methods to be added for database)
            if saved_choice == 1:
                yo = 1; #Added to avoided error line.
                

            # Filter by Name
            elif saved_choice == 2:
                yo = 1; #Added to avoided error line.

            #Filter by Budget
            elif saved_choice == 3:
                yo = 1; #Added to avoided error line.

            #Change Name of Meal Plan
            elif saved_choice == 4:
               yo = 1; #Added to avoided error line.

            # Delete Meal Plan
            elif saved_choice == 5:
                yo = 1; #Added to avoided error line.

            elif saved_choice == 6:
                self.__get_feedback()
                

    
    def __get_feedback(self):
        # Will add later as need to retrieve from database and convert into json before feeding to AI API
        return 0

    # Option to save the improved meal plan
    def __offer_to_save(self, plan, user_input):#basic structure for now, will be updated once database is ready
        while True:
            save_choice = input("\nSave this improved meal plan? (y/n): ").strip().lower()
            
            #calling of new function to save the improved meal plan into the database

            if save_choice == "y":
                y = 1; #Added to avoided error line.

            elif save_choice == "n":
                
                return

            else:
                print("\nInvalid input. Please enter Y or N.")