# Dish rules for the Logic Manager - Brandon

import json
from abc import ABC, abstractmethod
from pathlib import Path


# Reads numbers and words from the AI's text
class TextParser:

    @staticmethod
    def parse_number(value) -> float | None:
        if isinstance(value, bool):
            return None
        if isinstance(value, (int, float)):
            return float(value)
        if not isinstance(value, str):
            return None

        number = ""
        for char in value.replace(",", ""):
            if char.isdigit():
                number = number + char
            elif char == "." and "." not in number:
                number = number + char
            elif number != "" and number != ".":
                break
            else:
                number = ""

        if number == "" or number == ".":
            return None
        return float(number)

    @staticmethod
    def split_into_words(text) -> list:
        letters_only = ""
        for char in str(text).lower():
            if char.isalpha():
                letters_only = letters_only + char
            else:
                letters_only = letters_only + " "
        return letters_only.split()

    @staticmethod
    def contains_keyword(words: list, keyword: str) -> bool:
        keyword_words = keyword.split()
        size = len(keyword_words)

        for start in range(len(words) - size + 1):
            all_match = True
            for i in range(size):
                word = words[start + i]
                target = keyword_words[i]
                if word != target and word != target + "s" and word != target + "es":
                    all_match = False
                    break
            if all_match:
                return True
        return False

    @staticmethod
    def make_singular(word: str) -> str:
        if word.endswith("ies") and len(word) > 4:
            return word[:-3] + "y"
        if word.endswith("oes") and len(word) > 4:
            return word[:-2]
        if word.endswith("s") and not word.endswith("ss") and len(word) > 3:
            return word[:-1]
        return word

    @staticmethod
    def singular_words(text) -> list:
        words = []
        for word in TextParser.split_into_words(text):
            words.append(TextParser.make_singular(word))
        return words


# <<abstract>> base class for all dish rules
class DishRule(ABC):

    def __init__(self, name: str):
        self._name = name

    @property
    def name(self) -> str:
        return self._name

    @abstractmethod
    def check(self, dish: dict, profile) -> str | None:
        pass

    def apply(self, dishes: list, profile) -> dict:
        valid = []
        flagged = []
        for dish in dishes:
            if not isinstance(dish, dict):
                continue
            reason = self.check(dish, profile)
            if reason is None:
                valid.append(dish)
            else:
                flagged.append({"dish_name": dish.get("dish_name"), "reason": reason})
        return {"valid_dishes": valid, "flagged_dishes": flagged, "warnings": []}


# Removes dishes with restricted ingredients (rules from dietaryRules.json)
class DietaryRule(DishRule):

    DEFAULT_FILE = Path(__file__).resolve().parent / "dietaryRules.json"

    def __init__(self, file_path=None):
        super().__init__("Dietary restrictions")
        if file_path is None:
            file_path = DietaryRule.DEFAULT_FILE
        self.__file_path = Path(file_path)
        self.__keywords = None
        self.__exceptions = None
        self.__load_rules()

    def __load_rules(self):
        try:
            with open(self.__file_path, "r", encoding="utf-8") as file:
                rules = json.load(file)
            keywords = rules["restricted_keywords"]
            exceptions = rules["restriction_exceptions"]
            if not isinstance(keywords, dict) or not isinstance(exceptions, dict):
                return
        except (OSError, json.JSONDecodeError, KeyError, TypeError):
            return
        else:
            self.__keywords = keywords
            self.__exceptions = exceptions

    @property
    def rules_loaded(self) -> bool:
        return self.__keywords is not None

    def check(self, dish: dict, profile) -> str | None:
        restrictions = profile.restrictions
        if len(restrictions) == 0:
            return None

        if not self.rules_loaded:
            return f"Dietary rules could not be loaded from {self.__file_path.name}"

        text = str(dish.get("dish_name") or "") + " " + str(dish.get("ingredients") or "")
        text = text.lower()

        found = []
        for restriction in restrictions:
            check_text = text
            for safe_phrase in self.__exceptions.get(restriction, []):
                check_text = check_text.replace(safe_phrase, " ")
            words = TextParser.split_into_words(check_text)

            for keyword in self.__keywords.get(restriction, [restriction]):
                if TextParser.contains_keyword(words, keyword):
                    found.append(f"{keyword} ({restriction})")

        if len(found) > 0:
            return "Dish contains restricted ingredients: " + ", ".join(found)
        return None


# Removes dishes that miss the user's meal goal
class NutritionRule(DishRule):

    def __init__(self):
        super().__init__("Meal goal")

    def check(self, dish: dict, profile) -> str | None:
        calories = TextParser.parse_number(dish.get("calorie_count_per_meal_output"))
        protein = TextParser.parse_number(dish.get("protein_count_per_meal_output"))
        fat = TextParser.parse_number(dish.get("fats_count_per_meal"))

        reasons = profile.goal.evaluate(calories, protein, fat)
        if len(reasons) > 0:
            return "; ".join(reasons)
        return None


# Keeps preferred cuisines; shows all dishes if none match
class CuisineRule(DishRule):

    FALLBACK_WARNING = "No dishes matched your preferred cuisine, so other cuisines are shown"

    def __init__(self):
        super().__init__("Cuisine preference")

    def check(self, dish: dict, profile) -> str | None:
        preferences = profile.cuisines
        if len(preferences) == 0:
            return None

        cuisine = str(dish.get("cuisine")).strip()
        if cuisine.lower() in preferences:
            return None
        return f"Cuisine '{cuisine}' not in preferences"

    def apply(self, dishes: list, profile) -> dict:
        result = super().apply(dishes, profile)

        all_dishes = []
        for dish in dishes:
            if isinstance(dish, dict):
                all_dishes.append(dish)

        if len(result["valid_dishes"]) == 0 and len(all_dishes) > 0:
            return {"valid_dishes": all_dishes, "flagged_dishes": [],
                    "warnings": [CuisineRule.FALLBACK_WARNING]}
        return result
