# Standard goal for the Logic Manager - Brandon

from logic.nutrition_goal import NutritionGoal


# No nutrition limits, only needs readable calories
class StandardGoal(NutritionGoal):

    def evaluate(self, calories: float | None, protein: float | None, fat: float | None) -> list[str]:
        if calories is None:
            return ["Missing or unreadable nutrition data: calories"]
        return []

    def validate_targets(self) -> tuple[bool, str]:
        return True, ""
