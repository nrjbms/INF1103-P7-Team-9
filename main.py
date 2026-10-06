import aiManager
import dataManager
import inputManager
import logicManager


while True:

    choice = inputManager.main_menu()

    if choice == 1:
        user_input = inputManager.main_input()

        if user_input is None:
            continue

        prompt = aiManager.craftprompt(
            user_input[2],
            user_input[1],
            user_input[6],
            None
        )

        ai_output = aiManager.HCodeGeminiAPI(prompt)

        if "error" in ai_output:
            print("Error found:", ai_output)

            again = input("Do you want to regenerate? (Yes/No): ")

            if again.lower() == "yes":
                prompt = aiManager.craftprompt(
                    user_input[2],
                    user_input[1],
                    user_input[6],
                    None
                )

                ai_output = aiManager.HCodeGeminiAPI(prompt)

                if "error" in ai_output:
                    print("Error found again:", ai_output)
                    continue

            else:
                continue

        filtered_output = logicManager.process_ai_response(
            ai_output,
            user_input
        )

        inputManager.display_generated_meal_plan(
            user_input,
            ai_output
        )
        
        inputManager.get_accept_reject_menu("Are you satisfied? (Y/N): ")
        inputManager.get_select_dish()
        
        

    elif choice == 2:
        plans = "meal_plans.json"

        inputManager.display_all_plans(plans)

        selected_plan = inputManager.get_selected_plan(plans)

        if selected_plan is None:
            continue

        inputManager.display_meal_plan(selected_plan)

    else:  # choice == 3
        print("Goodbye!")
        break