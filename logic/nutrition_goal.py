# Nutrition goal interface for the Logic Manager - Brandon

from abc import ABC, abstractmethod


# <<interface>> every meal goal must implement
class NutritionGoal(ABC):

    TOLERANCE = 0.10
    PROTEIN_KCAL_PER_GRAM = 4
    FAT_KCAL_PER_GRAM = 9

    # Returns the reasons a dish misses this goal (an empty list means it passes)
    @abstractmethod
    def evaluate(self, calories: float | None, protein: float | None, fat: float | None) -> list[str]:
        pass

    # Returns (True, "") if the goal's own targets make sense, else (False, message)
    @abstractmethod
    def validate_targets(self) -> tuple[bool, str]:
        pass
