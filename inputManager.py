import tkinter as tk
import pycountry

# name,
def get_name_input(name_input):
    name_input = input(name_input)
    if name_input.lower() == "quit":
        return "quit"
    else:
        return name_input

# budget,
def get_budget_input(budget_input):
    budget_input = input(budget_input)
    try:
        budget_input = float(budget_input)
        if budget_input <= 9.9:
            print("It will be difficult to suggest meal plans with such a small budge. Please allocate more budget and try again.")
            return
        else:
            return budget_input
    except:
        print("Error. Please enter a valid number")
        return

# pax per,
def get_pax_input(pax_input):
    pax_input = input(pax_input)
    if pax_input.isdigit():
        if int(pax_input) <= 0:
            print("Error. Please enter a valid number.")
        else:
            return int(pax_input)
    else:
        print("Error. Please enter a valid number.")

# dietary restrictions,
def open_restrictions_menu():

    global root_restrictions, listbox_restrictions, RESTRICTIONS
    print("\n------[Opening Dietary Restrictions Menu]------")

    root_restrictions = tk.Tk()
    root_restrictions.title("Dietary Restrictions")

    root_restrictions.protocol("WM_DELETE_WINDOW", get_restrictions_selected)

    RESTRICTIONS = ("Seafood", "Nuts", "Dairy", "Wheat", "Eggs", "Halal")

    listbox_restrictions = tk.Listbox(root_restrictions, selectmode="multiple", height=5)
    listbox_restrictions.pack(padx = 10, pady= 10)

    # 2. Populate the listbox from the tuple
    for item in RESTRICTIONS:
        listbox_restrictions.insert(tk.END, item)

    btn_restrictions = tk.Button(root_restrictions, text = "Submit", command = get_restrictions_selected)
    btn_restrictions.pack(pady = 5)

    root_restrictions.mainloop()

def get_restrictions_selected():
    global selected_restrictions
    selected_restrictions = listbox_restrictions.curselection()
    if not selected_restrictions:
        print("No dietary restriction selected.")
        selected_restrictions = ('None',)
    else:
        selected_restrictions = tuple(RESTRICTIONS[i] for i in selected_restrictions)
        print("Selected Dietary Restrictions: ", selected_restrictions)
    root_restrictions.destroy()
    return selected_restrictions

# meal goal,
def open_goal_menu():

    global listbox_goal, root_goal, GOALS
    print("\n------[Opening Dietary Goal Menu]------")

    root_goal = tk.Tk()
    root_goal.title("Dietary Goals")

    root_goal.protocol("WM_DELETE_WINDOW", get_goal_selected)

    GOALS = ("Standard", "Low Calories", "High Calories", "Custom")

    listbox_goal = tk.Listbox(root_goal, selectmode="single", height=5)
    listbox_goal.pack(padx = 10, pady= 10)

    # 2. Populate the listbox from the tuple
    for item in GOALS:
        listbox_goal.insert(tk.END, item)

    btn = tk.Button(root_goal, text = "Submit", command = get_goal_selected)
    btn.pack(pady = 5)

    root_goal.mainloop()

def get_goal_selected():
    global selected_goals
    selected_goals = listbox_goal.curselection()
    if not selected_goals:
            selected_goals = ('None',)
    else:
        selected_goals = tuple(GOALS[i] for i in selected_goals)
        print("Selected Dietary Goals: ", selected_goals)
    root_goal.destroy()
    return selected_goals

def get_calorie_count(selected_goals): 

    match selected_goals:
            case('Standard',):
                calorie_count = 2000
                print("Calorie Count: ", calorie_count)
            case('Low Calories',):
                calorie_count = 1000
                print("Calorie Count: ", calorie_count)
            case('High Calories',):
                calorie_count = 3000
                print("Calorie Count: ", calorie_count)
            case('Custom',):
                calorie_count = input("Please enter your desired calories: ")
                if calorie_count.isdigit():
                    calorie_count = int(calorie_count)
                    print("Your selected calorie is: ", calorie_count)
                else:
                    print("Goal not defined. Standard will be chosen")
                    calorie_count = 2000
            case('None',):
                print("Since you have not selected a calorie goal, Standard will be chosen")
                calorie_count = 2000                
            case _:
                print("Goal not defined. Standard will be chosen")
                calorie_count = 2000
    return calorie_count

# country/currency,
def get_country_input(country_input):
    country_input = input(country_input)
    try:
        pycountry.countries.search_fuzzy(country_input)
        return country_input
    except:
        print("Error, country not found. Please enter a valid country.")
        return "country_error"

def main():
    while True:
        
        name_input = get_name_input("Enter name (Enter 'quit' to quit): ")
        if name_input == "quit":
            break
        else:
            print("Welcome: ", name_input)

        while True:
            budget_input = get_budget_input("Enter Budget (Min $10.0): ")
            if isinstance(budget_input, float):
                print("Your budget is:", budget_input)
                break

        while True:
            pax_input = get_pax_input("Enter Pax: ")
            if isinstance(pax_input, int):
                print("Number of pax: ", pax_input)
                break

        open_restrictions_menu()

        open_goal_menu()

        calorie_count = get_calorie_count(selected_goals)

        while True:
            country_input = get_country_input("\nEnter country: ")
            if not country_input == "country_error":
                print("Selected Country: ", country_input)
                break

        combined_input = [name_input, budget_input, pax_input, selected_restrictions, selected_goals, calorie_count, country_input]
        all_input = (combined_input)

        print("         MEAL PLANNER PROFILE SEARCH        ")
        print("="*40)
        print(f"User Name: {name_input}")
        print(f"Total Budget: ${budget_input:.2f}")
        print(f"Number of Pax: {pax_input}")
        print(f"Dietary Restrictions: {selected_restrictions}")
        print(f"Dietary Goal: {selected_goals}")
        print(f"Calories: {calorie_count} kcal")
        print(f"Target Country: {country_input}")
        print("="*40)
        return all_input

if __name__ == "__main__":
    profile_input = main()
    print(profile_input)
