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

        plan = logicManager.get_filtered_plan(ai_output, user_input)

        if plan is None:
            continue

        inputManager.display_generated_meal_plan(
            user_input,
            plan
        )

        inputManager.get_accept_reject_menu(
            plan["Dishes"],     
            "Accept? (y/n): ",   
            user_input,          
            dataManager)          
        
        

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