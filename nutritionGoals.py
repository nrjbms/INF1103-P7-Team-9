# Nutrition goals for the Logic Manager - Brandon

from abc import ABC, abstractmethod


# <<interface>> every meal goal must implement
class NutritionGoal(ABC):

    TOLERANCE = 0.10
    PROTEIN_KCAL_PER_GRAM = 4
    FAT_KCAL_PER_GRAM = 9

    @abstractmethod
    def evaluate(self, calories: float | None, protein: float | None, fat: float | None) -> list:
        pass

    @abstractmethod
    def validate_targets(self) -> tuple:
        pass


# No nutrition limits
class StandardGoal(NutritionGoal):

    def evaluate(self, calories: float | None, protein: float | None, fat: float | None) -> list:
        if calories is None:
            return ["Missing or unreadable nutrition data: calories"]
        return []

    def validate_targets(self) -> tuple:
        return True, ""


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

    def evaluate(self, calories: float | None, protein: float | None, fat: float | None) -> list:
        if calories is None:
            return ["Missing or unreadable nutrition data: calories"]

        cap = self.__max_calories * (1 + NutritionGoal.TOLERANCE)
        if calories > cap:
            return [f"Calories ({round(calories)} kcal) exceed target ({round(cap)} kcal)"]
        return []

    def validate_targets(self) -> tuple:
        return True, ""


# Protein floor and protein share of calories
class HighProteinGoal(NutritionGoal):

    DEFAULT_MIN_PROTEIN = 30
    MIN_PROTEIN_RATIO = 0.25

    def __init__(self, min_protein: float | None = None):
        if min_protein is None:
            min_protein = HighProteinGoal.DEFAULT_MIN_PROTEIN
        self.__min_protein = min_protein

    @property
    def min_protein(self) -> float:
        return self.__min_protein

    def evaluate(self, calories: float | None, protein: float | None, fat: float | None) -> list:
        missing = []
        if calories is None:
            missing.append("calories")
        if protein is None:
            missing.append("protein")
        if len(missing) > 0:
            return ["Missing or unreadable nutrition data: " + ", ".join(missing)]

        reasons = []
        floor = self.__min_protein * (1 - NutritionGoal.TOLERANCE)
        if protein < floor:
            reasons.append(f"Protein ({round(protein, 1)}g) below target ({round(floor, 1)}g)")

        if calories > 0:
            ratio = (protein * NutritionGoal.PROTEIN_KCAL_PER_GRAM) / calories
            if ratio < HighProteinGoal.MIN_PROTEIN_RATIO:
                reasons.append(f"Protein provides only {round(ratio * 100)}% of calories "
                               f"(goal needs {round(HighProteinGoal.MIN_PROTEIN_RATIO * 100)}%)")
        return reasons

    def validate_targets(self) -> tuple:
        return True, ""


# User's own calorie, protein and fat targets
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

    def evaluate(self, calories: float | None, protein: float | None, fat: float | None) -> list:
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

    def validate_targets(self) -> tuple:
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
