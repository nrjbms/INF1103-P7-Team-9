
import aiManager
import dataManager
import inputManager
import logicManager

inputManager.welcome_msg()

while True:

    choice = inputManager.main_menu()

    if choice == 1:
        user_input = inputManager.main_input()

        if user_input is None:
            continue

        exclude = None

        while True:
            prompt = aiManager.craftprompt(
                user_input[2],
                user_input[1],
                user_input[6],
                exclude
            )

            ai_output = aiManager.GeminiAPI(prompt)

            if "error" in ai_output:
                print("Error found:", ai_output)

                if inputManager.ask_regenerate():
                    continue
                else:
                    break

            plan = logicManager.get_filtered_plan(
                ai_output,
                user_input
            )

            if plan is None:
                if inputManager.ask_regenerate():
                    continue
                else:
                    break

            while True:
                inputManager.display_generated_meal_plan(
                    user_input,
                    plan
                )

                response, plan_to_save, exclude = (
                    inputManager.get_accept_reject_menu(
                        plan,
                        "Accept? (y/n): ",
                        user_input,
                        dataManager
                    )
                )

                if response == 'y':
                    break

                elif response == 'n':
                    regenerate = inputManager.ask_regenerate()

                    if regenerate:
                        break
                    else:
                        exclude = None
                        break

                else:
                    break

            if response == 'y':
                break

            elif response == 'n' and regenerate:
                continue

            else:
                break

    elif choice == 2:
        while True:
            saved_choice = inputManager.saved_plans_menu()

            if saved_choice is None:
                continue

            if saved_choice == 4:
                break

            if saved_choice == 1:
                plans = "meal_history.json"

                inputManager.display_all_plans(plans)

                selected_plan = inputManager.get_selected_plan(plans)

                if selected_plan is None:
                    continue

                inputManager.display_meal_plan(selected_plan)
                inputManager.get_selected_recipe(selected_plan)
                continue

            elif saved_choice == 2:
                name = input("\nEnter the name to search for: ")
                filtered_plans = dataManager.filter_by_name(name)

            elif saved_choice == 3:
                try:
                    budget = float(
                        input("\nEnter the budget to filter by: ")
                    )

                    filtered_plans = dataManager.filter_by_budget(
                        budget
                    )

                except ValueError:
                    print("Invalid budget. Please enter a number.")
                    continue

            inputManager.display_filtered_plans(filtered_plans)

            selected_plan = inputManager.get_selected_filtered_plan(
                filtered_plans
            )

            if selected_plan is None:
                continue

            inputManager.display_meal_plan(selected_plan)
            inputManager.get_selected_recipe(selected_plan)

    else:  # choice == 3
        print("Goodbye!")
        break
