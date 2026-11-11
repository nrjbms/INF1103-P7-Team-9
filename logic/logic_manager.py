# Logic Manager - Brandon

import json
import math
from pathlib import Path

from logic.user_profile import UserProfile


# Checks the AI's meal plan against the user's profile and decides the outcome
class LogicManager:

    DEFAULT_RULES_FILE = Path(__file__).resolve().parent.parent / "dietaryRules.json"
    NO_ERROR_VALUES = ("", "none", "null", "n/a", "na", "nil", "no error", "false")
    ACCEPT_RATIO = 0.5
    CUISINE_FALLBACK_WARNING = "No dishes matched your preferred cuisine, so other cuisines are shown"

    def __init__(self, rules_file: str | Path | None = None):
        if rules_file is None:
            rules_file = LogicManager.DEFAULT_RULES_FILE
        self.__rules_file = Path(rules_file)
        self.__keywords = None
        self.__exceptions = None
        self.__load_dietary_rules()

    @property
    def rules_loaded(self) -> bool:
        return self.__keywords is not None

    # Main entry point: AI output + user profile -> filtered plan with an outcome
    def evaluate(self, ai_output: dict | str, profile: UserProfile) -> dict:
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

        # Rule 1: dietary safety, Rule 2: meal goal, Rule 3: cuisine preference
        diet_ok, diet_flagged = self.__filter_dishes(dishes, self.__check_dietary, profile)
        goal_ok, goal_flagged = self.__filter_dishes(diet_ok, self.__check_nutrition, profile)
        valid_dishes, cuisine_flagged = self.__filter_dishes(goal_ok, self.__check_cuisine, profile)

        if len(valid_dishes) == 0 and len(goal_ok) > 0:
            valid_dishes = goal_ok
            cuisine_flagged = []
            plan["warnings"].append(LogicManager.CUISINE_FALLBACK_WARNING)

        plan["Dishes"] = valid_dishes
        plan["flagged_dishes"] = diet_flagged + goal_flagged + cuisine_flagged

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

    # ---------- dish rules ----------

    # Runs one check on every dish; returns (passed dishes, flagged dishes)
    def __filter_dishes(self, dishes: list[dict], check, profile: UserProfile) -> tuple[list[dict], list[dict]]:
        valid = []
        flagged = []
        for dish in dishes:
            reason = check(dish, profile)
            if reason is None:
                valid.append(dish)
            else:
                flagged.append({"dish_name": dish.get("dish_name"), "reason": reason})
        return valid, flagged

    # Removes dishes with restricted ingredients (rules from dietaryRules.json)
    def __check_dietary(self, dish: dict, profile: UserProfile) -> str | None:
        restrictions = profile.restrictions
        if len(restrictions) == 0:
            return None

        if not self.rules_loaded:
            return f"Dietary rules could not be loaded from {self.__rules_file.name}"

        text = str(dish.get("dish_name") or "") + " " + str(dish.get("ingredients") or "")
        text = text.lower()

        found = []
        for restriction in restrictions:
            check_text = text
            for safe_phrase in self.__exceptions.get(restriction, []):
                check_text = check_text.replace(safe_phrase, " ")
            words = self.__split_into_words(check_text)

            for keyword in self.__keywords.get(restriction, [restriction]):
                if self.__contains_keyword(words, keyword):
                    found.append(f"{keyword} ({restriction})")

        if len(found) > 0:
            return "Dish contains restricted ingredients: " + ", ".join(found)
        return None

    # Asks the user's NutritionGoal whether the dish meets it (polymorphism)
    def __check_nutrition(self, dish: dict, profile: UserProfile) -> str | None:
        calories = self.__parse_number(dish.get("calorie_count_per_meal_output"))
        protein = self.__parse_number(dish.get("protein_count_per_meal_output"))
        fat = self.__parse_number(dish.get("fats_count_per_meal"))

        reasons = profile.goal.evaluate(calories, protein, fat)
        if len(reasons) > 0:
            return "; ".join(reasons)
        return None

    # Keeps preferred cuisines (the fallback is handled in evaluate)
    def __check_cuisine(self, dish: dict, profile: UserProfile) -> str | None:
        preferences = profile.cuisines
        if len(preferences) == 0:
            return None

        cuisine = str(dish.get("cuisine")).strip()
        if cuisine.lower() in preferences:
            return None
        return f"Cuisine '{cuisine}' not in preferences"

    def __load_dietary_rules(self) -> None:
        try:
            with open(self.__rules_file, "r", encoding="utf-8") as file:
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

    # ---------- plan checks ----------

    def __to_dict(self, ai_output: dict | str) -> dict | None:
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

    def __set_pax(self, plan: dict, ai_output: dict, profile: UserProfile) -> None:
        user_pax = self.__parse_number(profile.pax)
        ai_pax = self.__parse_number(ai_output.get("pax"))
        if user_pax:
            plan["pax"] = int(user_pax)
        elif ai_pax:
            plan["pax"] = int(ai_pax)
        if user_pax and ai_pax and user_pax != ai_pax:
            plan["warnings"].append(
                f"The AI planned for {round(ai_pax)} pax but you asked for {round(user_pax)}")

    def __check_budget(self, total_grocery_cost, total_budget) -> tuple[bool, str]:
        cost = self.__parse_number(total_grocery_cost)
        budget = self.__parse_number(total_budget)

        if budget is None or math.isnan(budget) or math.isinf(budget):
            return False, "Budget is not a valid number."
        if cost is None:
            return False, "Grocery cost not found."
        if cost > budget:
            return False, f"Total grocery cost (${cost:.2f}) exceeds total budget (${budget:.2f})"
        return True, f"Total grocery cost (${cost:.2f}) is within total budget (${budget:.2f})"

    # Keeps only groceries used by the remaining dishes; returns (kept, removed names, new cost)
    def __filter_grocery_list(self, grocery_list: list | None, valid_dishes: list[dict]) -> tuple[list[dict], list[str], float]:
        used = []
        for dish in valid_dishes:
            for ingredient in str(dish.get("ingredients") or "").split(","):
                ingredient_words = self.__singular_words(ingredient)
                if len(ingredient_words) > 0:
                    used.append(ingredient_words)

        if grocery_list is None:
            grocery_list = []

        kept_items = []
        removed_items = []
        for item in grocery_list:
            if not isinstance(item, dict):
                continue
            name = item.get("ingredient_name")
            if self.__is_used(name, used):
                kept_items.append(item)
            elif name is None or str(name).strip() == "":
                removed_items.append("Unnamed item")
            else:
                removed_items.append(str(name))

        new_cost = 0.0
        for item in kept_items:
            price = self.__parse_number(item.get("Price_per_ingredient"))
            if price is not None:
                new_cost = new_cost + price
        return kept_items, removed_items, round(new_cost, 2)

    def __is_used(self, ingredient_name: str | None, used: list[list[str]]) -> bool:
        name_words = self.__singular_words(ingredient_name)
        if len(name_words) == 0:
            return False
        for ingredient_words in used:
            if self.__all_words_in(ingredient_words, name_words) or self.__all_words_in(name_words, ingredient_words):
                return True
        return False

    @staticmethod
    def __all_words_in(small_list: list[str], big_list: list[str]) -> bool:
        for word in small_list:
            if word not in big_list:
                return False
        return True

    # ---------- reading the AI's text ----------

    # Pulls the first number out of the AI's text, e.g. "450 kcal" -> 450.0
    @staticmethod
    def __parse_number(value) -> float | None:
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
    def __split_into_words(text: str) -> list[str]:
        letters_only = ""
        for char in str(text).lower():
            if char.isalpha():
                letters_only = letters_only + char
            else:
                letters_only = letters_only + " "
        return letters_only.split()

    # True if the keyword (one or more words, plural allowed) appears in the word list
    @staticmethod
    def __contains_keyword(words: list[str], keyword: str) -> bool:
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
    def __make_singular(word: str) -> str:
        if word.endswith("ies") and len(word) > 4:
            return word[:-3] + "y"
        if word.endswith("oes") and len(word) > 4:
            return word[:-2]
        if word.endswith("s") and not word.endswith("ss") and len(word) > 3:
            return word[:-1]
        return word

    def __singular_words(self, text: str) -> list[str]:
        words = []
        for word in self.__split_into_words(text):
            words.append(self.__make_singular(word))
        return words
