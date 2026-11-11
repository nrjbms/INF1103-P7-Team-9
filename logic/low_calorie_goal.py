# Low calorie goal for the Logic Manager - Brandon

from logic.nutrition_goal import NutritionGoal


# Calorie cap
class LowCalorieGoal(NutritionGoal):

    DEFAULT_MAX_CALORIES = 500

    def __init__(self, max_calories: float | None = None):
        if max_calories is None:
            max_calories = LowCalorieGoal.DEFAULT_MAX_CALORIES
        self.__max_calories = max_calories

    @property
    def max_calories(self) -> float:
        return self.__max_calories

    def evaluate(self, calories: float | None, protein: float | None, fat: float | None) -> list[str]:
        if calories is None:
            return ["Missing or unreadable nutrition data: calories"]

        cap = self.__max_calories * (1 + NutritionGoal.TOLERANCE)
        if calories > cap:
            return [f"Calories ({round(calories)} kcal) exceed target ({round(cap)} kcal)"]
        return []

    def validate_targets(self) -> tuple[bool, str]:
        return True, ""
