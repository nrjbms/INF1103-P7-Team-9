# User profile for the Logic Manager - Brandon

import math

from logic.nutrition_goal import NutritionGoal
from logic.standard_goal import StandardGoal
from logic.low_calorie_goal import LowCalorieGoal
from logic.high_protein_goal import HighProteinGoal
from logic.custom_macros_goal import CustomMacrosGoal


# Holds the user's choices; creates and owns its NutritionGoal (composition)
class UserProfile:

    def __init__(self, name: str | None, budget: float | None, pax: int | None,
                 restrictions: list[str] | tuple | str | None, goal_name: str | tuple | None,
                 cuisines: list[str] | tuple | str | None, country: str | None,
                 calories: float | None = None, protein: float | None = None, fat: float | None = None):
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

    # Builds a profile from the list the IO Manager returns
    @classmethod
    def from_input_list(cls, user_input: list) -> "UserProfile":
        def item(index):
            if index < len(user_input):
                return user_input[index]
            return None

        return cls(name=item(0), budget=item(1), pax=item(2), restrictions=item(3),
                   goal_name=item(4), cuisines=item(6), country=item(7),
                   calories=item(5), protein=item(8), fat=item(9))

    # Picks the NutritionGoal subclass for the user's chosen goal
    @staticmethod
    def __create_goal(goal_name: str | tuple | None, calories: float | None,
                      protein: float | None, fat: float | None) -> NutritionGoal:
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
    def __clean_choices(choices: list[str] | tuple | str | None) -> list[str]:
        if choices is None:
            return []
        if isinstance(choices, str):
            choices = (choices,)
        cleaned = []
        for choice in choices:
            cleaned.append(str(choice).strip().lower())
        return cleaned

    # The IO Manager already validates numbers, so only a simple check is needed here
    @staticmethod
    def __positive_number(value) -> float | None:
        if isinstance(value, bool):
            return None
        try:
            number = float(value)
        except (TypeError, ValueError):
            return None
        if math.isnan(number) or math.isinf(number) or number <= 0:
            return None
        return number

    @property
    def name(self) -> str | None:
        return self.__name

    @property
    def budget(self) -> float | None:
        return self.__budget

    @property
    def pax(self) -> int | None:
        return self.__pax

    @property
    def restrictions(self) -> list[str]:
        return list(self.__restrictions)

    @property
    def cuisines(self) -> list[str]:
        return list(self.__cuisines)

    @property
    def country(self) -> str | None:
        return self.__country

    @property
    def goal(self) -> NutritionGoal:
        return self.__goal
