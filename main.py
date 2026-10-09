
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

                again = input("Do you want to regenerate? (Yes/No): ")

                if again.lower() == "yes":
                    continue
                else:
                    break

            plan = logicManager.get_filtered_plan(ai_output, user_input)

            if plan is None:
                again = input("Do you want to regenerate? (Yes/No): ")

                if again.lower() == "yes":
                    continue
                else:
                    break

            while True:
                inputManager.display_generated_meal_plan(user_input, plan)

                response, plan_to_save, exclude = inputManager.get_accept_reject_menu(
                    plan,
                    "Accept? (y/n): ",
                    user_input,
                    dataManager
                )

                if response == 'y':
                    break

                elif response == 'n':
                    again = input("Do you want to regenerate? (Yes/No): ")

                    if again.lower() == "yes":
                        break
                    else:
                        exclude = None
                        break

                else:
                    break

            if response == 'y':
                break
            elif response == 'n' and again.lower() == "yes":
                continue
            else:
                break

    elif choice == 2:
        plans = "meal_history.json"

        inputManager.display_all_plans(plans)

        selected_plan = inputManager.get_selected_plan(plans)

        if selected_plan is None:
            continue

        inputManager.display_meal_plan(selected_plan)
        inputManager.get_selected_recipe(selected_plan)

    else:  # choice == 3
        print("Goodbye!")
        break