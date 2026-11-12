from macros import Macros
#new !!!!

class MealPlan:

    def __init__(self, plan_id, name, budget, pax, dietary_restrictions, macros: Macros, cuisine, country, dietary_goal, total_grocery_cost, grocery_list, dishes):
        self.__id = plan_id
        self.__name = name
        self.__budget = budget
        self.__pax = pax
        self.__dietary_restrictions = dietary_restrictions
        self.__macros = macros
        self.__cuisine = cuisine
        self.__country = country
        self.__dietary_goal = dietary_goal
        self.__total_grocery_cost = total_grocery_cost
        self.__grocery_list = grocery_list
        self.__dishes = dishes

#Getters for Meal Plan

    def get_id(self):
        return self.__id

    def get_name(self):
        return self.__name

    def get_budget(self):
        return self.__budget

    def get_pax(self):
        return self.__pax

    def get_dietary_restrictions(self):
        return self.__dietary_restrictions

    def get_macros(self):
        return self.__macros

    def get_cuisine(self):
        return self.__cuisine

    def get_country(self):
        return self.__country

    def get_dietary_goal(self):
        return self.__dietary_goal

    def get_total_grocery_cost(self):
        return self.__total_grocery_cost

    def get_grocery_list(self):
        return self.__grocery_list

    def get_dishes(self):
        return self.__dishes

#Setters for Meal Plan

    def set_id(self, plan_id):
        self.__id = plan_id

    def set_name(self, name):
        self.__name = name


    def to_dict(self):
        return {
            "id": self.__id,
            "name": self.__name,
            "budget": self.__budget,
            "pax": self.__pax,
            "Total_grocery_cost": self.__total_grocery_cost,
            "Grocery_list": self.__grocery_list,
            "Dishes": self.__dishes,
            "dietary_restrictions": self.__dietary_restrictions,
            "dietary_goal": self.__dietary_goal,
            **self.__macros.to_dict(),     # calorie, protein, fat 
            "cuisine": self.__cuisine,
            "country": self.__country,
            "date": self.__date,
        }

    def __str__(self):
        return (f"{self.__id}: Meal Plan for {self.__name} "
                f"({self.__pax} pax) - ${self.__total_grocery_cost:.2f}")