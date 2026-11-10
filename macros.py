class Macros:

    def __init__(self, calories, protein, fat):
        self.__calories = calories
        self.__protein = protein
        self.__fat = fat

    def get_calories(self):
        return self.__calories

    def get_protein(self):
        return self.__protein

    def get_fat(self):
        return self.__fat

    def to_dict(self):
        return {"calorie_count": self.__calories,
                "protein_count": self.__protein,
                "fat_count": self.__fat}

    def __str__(self):
        return f"{self.__calories}kcal, {self.__protein}g protein, {self.__fat}g fat"