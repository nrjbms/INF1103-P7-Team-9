# High protein goal for the Logic Manager - Brandon

from logic.nutrition_goal import NutritionGoal


# Protein floor and protein share of calories (multi-condition rule)
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

    def evaluate(self, calories: float | None, protein: float | None, fat: float | None) -> list[str]:
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

    def validate_targets(self) -> tuple[bool, str]:
        return True, ""
