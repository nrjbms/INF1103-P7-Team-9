# Custom macros goal for the Logic Manager - Brandon

from logic.nutrition_goal import NutritionGoal


# User's own calorie, protein and fat targets (multi-condition rule)
class CustomMacrosGoal(NutritionGoal):

    def __init__(self, max_calories: float | None, min_protein: float | None, max_fat: float | None):
        self.__max_calories = max_calories
        self.__min_protein = min_protein
        self.__max_fat = max_fat

    @property
    def max_calories(self) -> float | None:
        return self.__max_calories

    @property
    def min_protein(self) -> float | None:
        return self.__min_protein

    @property
    def max_fat(self) -> float | None:
        return self.__max_fat

    def evaluate(self, calories: float | None, protein: float | None, fat: float | None) -> list[str]:
        missing = []
        if calories is None:
            missing.append("calories")
        if protein is None and self.__min_protein is not None:
            missing.append("protein")
        if fat is None and self.__max_fat is not None:
            missing.append("fat")
        if len(missing) > 0:
            return ["Missing or unreadable nutrition data: " + ", ".join(missing)]

        reasons = []
        if self.__max_calories is not None:
            cap = self.__max_calories * (1 + NutritionGoal.TOLERANCE)
            if calories > cap:
                reasons.append(f"Calories ({round(calories)} kcal) exceed target ({round(cap)} kcal)")
        if self.__min_protein is not None:
            floor = self.__min_protein * (1 - NutritionGoal.TOLERANCE)
            if protein < floor:
                reasons.append(f"Protein ({round(protein, 1)}g) below target ({round(floor, 1)}g)")
        if self.__max_fat is not None:
            cap = self.__max_fat * (1 + NutritionGoal.TOLERANCE)
            if fat > cap:
                reasons.append(f"Fat ({round(fat, 1)}g) exceeds target ({round(cap, 1)}g)")
        return reasons

    # Protein and fat calories must fit inside the calorie target
    def validate_targets(self) -> tuple[bool, str]:
        if self.__max_calories is None or self.__min_protein is None or self.__max_fat is None:
            return True, ""

        macro_calories = (self.__min_protein * NutritionGoal.PROTEIN_KCAL_PER_GRAM
                          + self.__max_fat * NutritionGoal.FAT_KCAL_PER_GRAM)
        if macro_calories > self.__max_calories:
            message = (f"Your protein ({round(self.__min_protein)}g) and fat ({round(self.__max_fat)}g) "
                       f"targets add up to {round(macro_calories)} kcal, which is more than your calorie "
                       f"goal of {round(self.__max_calories)} kcal. Please lower protein or fat, or raise calories.")
            return False, message
        return True, ""
