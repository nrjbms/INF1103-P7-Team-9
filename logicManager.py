# Logic Manager - Brandon

import json
import math

from dishRules import DishRule, DietaryRule, NutritionRule, CuisineRule, TextParser
from nutritionGoals import (NutritionGoal, StandardGoal, LowCalorieGoal,
                            HighProteinGoal, CustomMacrosGoal)


# Holds the user's choices; creates and owns its NutritionGoal (composition)
class UserProfile:

    def __init__(self, name, budget, pax, restrictions, goal_name, cuisines, country,
                 calories=None, protein=None, fat=None):
        self.__name = name
        self.__budget = budget
        self.__pax = pax
        self.__restrictions = UserProfile.__clean_choices(restrictions)
        self.__restrictions = [choice for choice in self.__restrictions if choice != "none"]
        self.__cuisines = UserProfile.__clean_choices(cuisines)
        if "anything" in self.__cuisines:
            self.__cuisines = []
        self.__country = country
        self.__goal = UserProfile.__create_goal(goal_name,
                                                UserProfile.__positive_number(calories),
                                                UserProfile.__positive_number(protein),
                                                UserProfile.__positive_number(fat))

    @classmethod
    def from_input_list(cls, user_input):
        def item(index):
            if index < len(user_input):
                return user_input[index]
            return None

        return cls(name=item(0), budget=item(1), pax=item(2), restrictions=item(3),
                   goal_name=item(4), cuisines=item(6), country=item(7),
                   calories=item(5), protein=item(8), fat=item(9))

    @staticmethod
    def __create_goal(goal_name, calories, protein, fat) -> NutritionGoal:
        if isinstance(goal_name, (tuple, list)):
            if len(goal_name) > 0:
                goal_name = goal_name[0]
            else:
                goal_name = None
        if goal_name is None:
            name = "standard"
        else:
            name = str(goal_name).strip().lower()

        if name == "low calorie" or name == "low calories":
            return LowCalorieGoal(calories)
        elif name == "high protein":
            return HighProteinGoal(protein)
        elif name == "custom macros" or name == "custom":
            return CustomMacrosGoal(calories, protein, fat)
        return StandardGoal()

    @staticmethod
    def __clean_choices(choices) -> list:
        if choices is None:
            return []
        if isinstance(choices, str):
            choices = (choices,)
        cleaned = []
        for choice in choices:
            cleaned.append(str(choice).strip().lower())
        return cleaned

    @staticmethod
    def __positive_number(value) -> float | None:
        number = TextParser.parse_number(value)
        if number is None or number <= 0:
            return None
        return number

    @property
    def name(self):
        return self.__name

    @property
    def budget(self):
        return self.__budget

    @property
    def pax(self):
        return self.__pax

    @property
    def restrictions(self) -> list:
        return list(self.__restrictions)

    @property
    def cuisines(self) -> list:
        return list(self.__cuisines)

    @property
    def country(self):
        return self.__country

    @property
    def goal(self) -> NutritionGoal:
        return self.__goal


# Runs every registered DishRule on the AI's plan and decides the outcome
class LogicManager:

    NO_ERROR_VALUES = ("", "none", "null", "n/a", "na", "nil", "no error", "false")
    ACCEPT_RATIO = 0.5

    def __init__(self):
        self.__rules = []

    @classmethod
    def create_default(cls):
        manager = cls()
        manager.register_rule(DietaryRule())
        manager.register_rule(NutritionRule())
        manager.register_rule(CuisineRule())
        return manager

    def register_rule(self, rule: DishRule):
        if not isinstance(rule, DishRule):
            raise TypeError("Only DishRule objects can be registered")
        self.__rules.append(rule)

    @property
    def rules(self) -> list:
        return list(self.__rules)

    def evaluate(self, ai_output, profile: UserProfile) -> dict:
        ai_output = self.__to_dict(ai_output)

        plan = {
            "pax": 0,
            "Error": "",
            "Total_grocery_cost": 0,
            "Grocery_list": [],
            "Dishes": [],
            "outcome": "REJECTED",
            "warnings": [],
            "flagged_dishes": [],
        }

        if not isinstance(ai_output, dict) or not isinstance(profile, UserProfile):
            plan["Error"] = "Invalid data passed to the logic manager"
            return plan

        targets_ok, targets_error = profile.goal.validate_targets()
        if not targets_ok:
            plan["Error"] = targets_error
            return plan

        ai_error = self.__ai_error(ai_output)
        if ai_error.lower() not in LogicManager.NO_ERROR_VALUES:
            plan["Error"] = ai_error
            return plan

        if not isinstance(ai_output.get("Dishes"), list) or len(ai_output["Dishes"]) == 0:
            plan["Error"] = "The AI returned no dishes"
            return plan

        dishes = []
        for dish in ai_output["Dishes"]:
            if isinstance(dish, dict):
                dishes.append(dish)

        self.__set_pax(plan, ai_output, profile)

        valid_dishes = dishes
        for rule in self.__rules:
            result = rule.apply(valid_dishes, profile)
            valid_dishes = result["valid_dishes"]
            plan["flagged_dishes"] = plan["flagged_dishes"] + result["flagged_dishes"]
            plan["warnings"] = plan["warnings"] + result["warnings"]
        plan["Dishes"] = valid_dishes

        kept_items, removed_items, new_cost = self.__filter_grocery_list(
            ai_output.get("Grocery_list", []), valid_dishes)
        plan["Grocery_list"] = kept_items
        plan["Total_grocery_cost"] = new_cost
        if len(removed_items) > 0:
            plan["warnings"].append("Removed unused groceries: " + ", ".join(removed_items))

        budget_ok, budget_reason = self.__check_budget(new_cost, profile.budget)
        if not budget_ok:
            plan["Error"] = budget_reason
        elif len(valid_dishes) == 0:
            plan["Error"] = "No dishes passed all the rules"
        elif len(valid_dishes) / len(dishes) >= LogicManager.ACCEPT_RATIO:
            plan["outcome"] = "ACCEPTED"
        else:
            plan["outcome"] = "FLAGGED"
            plan["warnings"].append(
                f"Only {len(valid_dishes)} of {len(dishes)} suggested dishes met your "
                "requirements. You may want to regenerate for more options"
            )
        return plan

    def __to_dict(self, ai_output):
        if isinstance(ai_output, str):
            try:
                return json.loads(ai_output)
            except json.JSONDecodeError:
                return {"Error": ai_output}
        return ai_output

    def __ai_error(self, ai_output: dict) -> str:
        if ai_output.get("Error") is None:
            return ""
        return str(ai_output.get("Error")).strip()

    def __set_pax(self, plan: dict, ai_output: dict, profile: UserProfile):
        user_pax = TextParser.parse_number(profile.pax)
        ai_pax = TextParser.parse_number(ai_output.get("pax"))
        if user_pax:
            plan["pax"] = int(user_pax)
        elif ai_pax:
            plan["pax"] = int(ai_pax)
        if user_pax and ai_pax and user_pax != ai_pax:
            plan["warnings"].append(
                f"The AI planned for {round(ai_pax)} pax but you asked for {round(user_pax)}")

    def __check_budget(self, total_grocery_cost, total_budget) -> tuple:
        cost = TextParser.parse_number(total_grocery_cost)
        budget = TextParser.parse_number(total_budget)

        if budget is None or math.isnan(budget) or math.isinf(budget):
            return False, "Budget is not a valid number."
        if cost is None:
            return False, "Grocery cost not found."
        if cost > budget:
            return False, f"Total grocery cost (${cost:.2f}) exceeds total budget (${budget:.2f})"
        return True, f"Total grocery cost (${cost:.2f}) is within total budget (${budget:.2f})"

    def __filter_grocery_list(self, grocery_list, valid_dishes: list) -> tuple:
        used = []
        for dish in valid_dishes:
            for ingredient in str(dish.get("ingredients") or "").split(","):
                ingredient_words = TextParser.singular_words(ingredient)
                if len(ingredient_words) > 0:
                    used.append(ingredient_words)

        if grocery_list is None:
            grocery_list = []

        kept_items = []
        removed_items = []
        for item in grocery_list:
            if not isinstance(item, dict):
                continue
            if self.__is_used(item.get("ingredient_name", ""), used):
                kept_items.append(item)
            else:
                removed_items.append(item.get("ingredient_name"))

        new_cost = 0.0
        for item in kept_items:
            price = TextParser.parse_number(item.get("Price_per_ingredient"))
            if price is not None:
                new_cost = new_cost + price
        return kept_items, removed_items, round(new_cost, 2)

    def __is_used(self, ingredient_name, used: list) -> bool:
        name_words = TextParser.singular_words(ingredient_name)
        if len(name_words) == 0:
            return False
        for ingredient_words in used:
            if self.__all_words_in(ingredient_words, name_words) or self.__all_words_in(name_words, ingredient_words):
                return True
        return False

    def __all_words_in(self, small_list: list, big_list: list) -> bool:
        for word in small_list:
            if word not in big_list:
                return False
        return True