import aiManager
import dataManager
import inputManager
import logicManager

inputManager.welcome_msg()

while True:
    choice = inputManager.main_menu()

    if choice is None:
        continue
    
    #Option 1: Generate Meal Plan
    if choice == 1:
        user_input = inputManager.main_input() #Input Prompt and Validation

        if user_input is None: # Error Handling if user_input is empty
            continue

        exclude = None # Initialise exclude as None, assuming user first generation

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

            inputManager.display_plan_messages(plan) # Flags and Rejects

            #if AI output is all rejected for flagged, ask for regeneration
            if plan["outcome"] == "REJECTED":
                print("Unable to generate a valid meal plan.")

                if inputManager.ask_regenerate():
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
