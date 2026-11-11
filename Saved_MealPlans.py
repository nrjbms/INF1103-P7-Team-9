import json
import math
import os
import tempfile
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime


class StorageError(Exception):
    pass


class Storage(ABC):

    @abstractmethod
    def load(self):
        pass

    @abstractmethod
    def save(self, records):
        pass


class JSONStorage(Storage):

    def __init__(self, filename="meal_history.json"):
        self._filename = os.fspath(filename)

    def load(self):
        if not os.path.exists(self._filename):
            return []
        try:
            with open(self._filename, "r", encoding="utf-8") as file:
                records = json.load(file)
            if not isinstance(records, list) or any(not isinstance(r, dict) for r in records):
                raise StorageError("History must contain a list of meal-plan objects")
            return records
        except (OSError, UnicodeError, json.JSONDecodeError) as exc:
            raise StorageError("Unable to read meal history") from exc

    def save(self, records):
        if not isinstance(records, list) or any(not isinstance(r, dict) for r in records):
            raise StorageError("Records must be a list of dictionaries")
        temporary_path = None
        try:
            json.dumps(records, ensure_ascii=False, allow_nan=False)
            directory = os.path.dirname(os.path.abspath(self._filename))
            with tempfile.NamedTemporaryFile(
                mode="w", encoding="utf-8", dir=directory,
                prefix=".meal_history_", suffix=".tmp", delete=False
            ) as file:
                temporary_path = file.name
                json.dump(records, file, indent=4, ensure_ascii=False, allow_nan=False)
            os.replace(temporary_path, self._filename)
            return True
        except (OSError, TypeError, ValueError) as exc:
            raise StorageError("Unable to save meal history") from exc
        finally:
            if temporary_path is not None and os.path.exists(temporary_path):
                try:
                    os.remove(temporary_path)
                except OSError:
                    pass


@dataclass
class MealPlan:
    id: int
    name: str
    details: dict

    def to_dict(self):
        return {**self.details, "id": self.id, "name": self.name}

    @classmethod
    def from_dict(cls, record):
        if not isinstance(record, dict):
            raise ValueError("Record must be a dictionary")
        record_id = record.get("id")
        name = record.get("name")
        if type(record_id) is not int or record_id <= 0:
            raise ValueError("Invalid meal-plan ID")
        if not isinstance(name, str) or not name.strip():
            raise ValueError("Invalid meal-plan name")
        return cls(record_id, name.strip(), {k: v for k, v in record.items() if k not in ("id", "name")})


class Saved_MealPlans:

    def __init__(self, filename="meal_history.json", storage=None):
        self._storage = storage if storage is not None else JSONStorage(filename)
        if not isinstance(self._storage, Storage):
            raise TypeError("storage must implement Storage")

    @staticmethod
    def _valid_amount(value):
        if isinstance(value, bool):
            return False
        try:
            amount = float(value)
        except (TypeError, ValueError, OverflowError):
            return False
        return math.isfinite(amount) and amount >= 0

    @staticmethod
    def _generate_id(records):
        ids = [r["id"] for r in records if type(r.get("id")) is int and r["id"] > 0]
        return max(ids, default=0) + 1

    def _load_records(self):
        try:
            return self._storage.load()
        except StorageError:
            return None

    def _save_records(self, records):
        try:
            return self._storage.save(records)
        except StorageError:
            return False

    def add_MealPlan(self, plan, user_input=None):
        if isinstance(plan, MealPlan):
            plan = plan.to_dict()
        elif not isinstance(plan, dict) and callable(getattr(plan, "to_dict", None)):
            try:
                plan = plan.to_dict()
            except (TypeError, ValueError, AttributeError):
                return None
        if not isinstance(plan, dict):
            return None
        plan = plan.copy()
        if user_input is not None:
            if not isinstance(user_input, (list, tuple)) or len(user_input) < 10:
                return None
            plan.update(dict(zip(
                ("name", "budget", "pax", "dietary_restrictions", "dietary_goal",
                 "calorie_count", "cuisine", "country", "protein_count", "fat_count"),
                user_input[:10]
            )))
        name = plan.get("name")
        if not isinstance(name, str) or not name.strip():
            return None
        if not self._valid_amount(plan.get("budget")):
            return None
        if type(plan.get("pax")) is not int or plan["pax"] <= 0:
            return None
        if not self._valid_amount(plan.get("Total_grocery_cost")):
            return None
        if not isinstance(plan.get("Grocery_list"), list):
            return None
        if not isinstance(plan.get("Dishes"), list):
            return None
        records = self._load_records()
        if records is None:
            return None  # Never overwrite corrupted history
        new_id = self._generate_id(records)
        plan.update({"id": new_id, "name": name.strip(),
                     "budget": float(plan["budget"]),
                     "date": datetime.now().strftime("%Y-%m-%d")})
        # No user IDs: shared history is accessible to everyone using the app.
        plan.pop("user_id", None)
        records.append(plan)
        return new_id if self._save_records(records) else None

    def get_all_MealPlans(self):
        return self._load_records() or []

    def get_MealPlan(self, plan_id):
        for record in self.get_all_MealPlans():
            if str(record.get("id")) == str(plan_id):
                return record
        return None

    def get_MealPlan_object(self, plan_id):
        record = self.get_MealPlan(plan_id)
        if record is None:
            return None
        try:
            return MealPlan.from_dict(record)
        except ValueError:
            return None

    def get_all_MealPlan_objects(self):
        plans = []
        for record in self.get_all_MealPlans():
            try:
                plans.append(MealPlan.from_dict(record))
            except ValueError:
                continue
        return plans

    def rename_MealPlan(self, plan_id, new_name):
        if not isinstance(new_name, str) or not new_name.strip():
            return False
        records = self._load_records()
        if records is None:
            return False
        for record in records:
            if str(record.get("id")) == str(plan_id):
                record["name"] = new_name.strip()
                return self._save_records(records)
        return False

    def delete_MealPlan(self, plan_id):
        records = self._load_records()
        if records is None:
            return False
        for index, record in enumerate(records):
            if str(record.get("id")) == str(plan_id):
                records.pop(index)
                return self._save_records(records)
        return False

    def filter_MealPlans_by_name(self, name):
        if name is None or not str(name).strip():
            return []
        name = str(name).strip().lower()
        return [r for r in self.get_all_MealPlans()
                if str(r.get("name", "")).strip().lower() == name]

    def filter_MealPlans_by_budget(self, max_budget):
        if not self._valid_amount(max_budget):
            return []
        return [r for r in self.get_all_MealPlans()
                if self._valid_amount(r.get("Total_grocery_cost"))
                and float(r["Total_grocery_cost"]) <= float(max_budget)]

    def search_MealPlan_by_keyword(self, word):
        if word is None or not str(word).strip():
            return []
        keyword = str(word).strip().lower()
        return [r for r in self.get_all_MealPlans()
                if keyword in json.dumps(r, ensure_ascii=False).lower()]
