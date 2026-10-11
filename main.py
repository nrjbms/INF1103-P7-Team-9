import aiManager
import dataManager
import inputManager
import logicManager

inputManager.welcome_msg()

while True:
    choice = inputManager.main_menu()

    if choice is None:
        continue

    if choice == 1:
        user_input = inputManager.main_input()

        if user_input is None:
            continue

        exclude = None

        while True:
            prompt = aiManager.craftprompt(user_input[2],user_input[1],user_input[6],exclude)

            ai_output = aiManager.GeminiAPI(prompt)

            
            if "error" in ai_output:
                print("Error found:", ai_output)

                if inputManager.ask_regenerate():
                    continue
                else:
                    break

            plan = logicManager.get_filtered_plan(ai_output, user_input)

            inputManager.display_plan_messages(plan)

            if plan["outcome"] == "REJECTED":
                print("Unable to generate a valid meal plan.")

                if inputManager.ask_regenerate():
                    continue
                else:
                    break

            inputManager.display_generated_meal_plan(user_input, plan)

            response, plan_to_save, exclude = inputManager.get_accept_reject_menu(plan, "Accept? (y/n): ", user_input ,dataManager)
            
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
            saved_choice = inputManager.manage_plans_menu()

            if saved_choice is None:
                continue

            if saved_choice == 6:
                break

            
            elif saved_choice == 1:
                meal_plans = "meal_history.json"

                inputManager.display_all_plans(meal_plans)

                selected_plan = inputManager.get_selected_plan(meal_plans)

                if selected_plan is None:
                    continue

                inputManager.display_meal_plan(selected_plan)
                inputManager.get_selected_recipe(selected_plan)

            
            elif saved_choice == 2:
                name = inputManager.get_name_filter()

                filtered_plans = dataManager.filter_by_name(name)

                inputManager.display_filtered_plans(filtered_plans)

                selected_plan = inputManager.get_selected_filtered_plan(filtered_plans)

                if selected_plan is None:
                    continue

                inputManager.display_meal_plan(selected_plan)
                inputManager.get_selected_recipe(selected_plan)

            
            elif saved_choice == 3:
                budget = inputManager.get_budget_filter()

                filtered_plans = dataManager.filter_by_budget(budget)

                inputManager.display_filtered_plans(filtered_plans)

                selected_plan = inputManager.get_selected_filtered_plan(filtered_plans)

                if selected_plan is None:
                    continue

                inputManager.display_meal_plan(selected_plan)
                inputManager.get_selected_recipe(selected_plan)

            
            elif saved_choice == 4:
                meal_plans = "meal_history.json"

                inputManager.display_all_plans(meal_plans)

                selected_plan = inputManager.get_selected_plan(meal_plans)

                if selected_plan is None:
                    continue

                new_name = inputManager.change_meal_plan_name(selected_plan)

                if new_name:
                    dataManager.update_meal_plan_name(selected_plan["id"], new_name)

 
            elif saved_choice == 5:
                inputManager.delete_meal_plan("meal_history.json")


    elif choice == 3:
        print("Goodbye!")
        break
