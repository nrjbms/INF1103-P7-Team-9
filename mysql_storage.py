
import json
from datetime import datetime
from mysql.connector import Error
from db_config import get_db_connection
from Saved_MealPlans import Storage, StorageError


class MySQLStorage(Storage):

    # Establish a connection to the JustEat database
    def _connect(self):
        connection = get_db_connection()

        if connection is None:
            raise StorageError("Unable to connect to MySQL")

        return connection

    # Convert database records into Python dictionaries
    def _convert_record(self, record):
        for field in ["dietary_restrictions", "Grocery_list", "Dishes"]:
            value = record.get(field)

            if isinstance(value, (str, bytes)):
                record[field] = json.loads(value)

        for field in [
            "budget",
            "calorie_count",
            "protein_count",
            "fat_count",
            "Total_grocery_cost"
        ]:
            if record.get(field) is not None:
                record[field] = float(record[field])

        created = record.pop("date_created", None)

        if created is not None:
            record["date"] = created.isoformat()

        return record

    # Retrieve all saved meal plans
    def load(self):
        connection = self._connect()
        cursor = None

        try:
            cursor = connection.cursor(dictionary=True)

            cursor.execute(
                "SELECT * FROM saved_meal_plans ORDER BY id"
            )

            records = cursor.fetchall()

            return [
                self._convert_record(record)
                for record in records
            ]

        except (Error, ValueError, TypeError) as e:
            raise StorageError("Unable to load meal plans") from e

        finally:
            if cursor is not None:
                cursor.close()
            connection.close()

    # Prepare values for an INSERT or UPDATE query
    def _record_values(self, record):
        date = record.get("date")

        if isinstance(date, str):
            date = datetime.fromisoformat(date)

        return (
            record.get("name"),
            date,
            record.get("budget"),
            record.get("pax"),
            json.dumps(record.get("dietary_restrictions")),
            record.get("dietary_goal"),
            record.get("calorie_count"),
            record.get("cuisine"),
            record.get("country"),
            record.get("protein_count"),
            record.get("fat_count"),
            record.get("Total_grocery_cost"),
            json.dumps(record.get("Grocery_list")),
            json.dumps(record.get("Dishes"))
        )

    # Save changes without deleting and recreating every row
    def save(self, records):
        if not isinstance(records, list):
            raise StorageError("Records must be a list")

        connection = self._connect()
        cursor = None

        try:
            cursor = connection.cursor()

            connection.start_transaction()

            cursor.execute(
                "SELECT id FROM saved_meal_plans FOR UPDATE"
            )

            existing_ids = {
                row[0] for row in cursor.fetchall()
            }

            new_ids = set()

            columns = """
                name, date_created, budget, pax,
                dietary_restrictions, dietary_goal,
                calorie_count, cuisine, country,
                protein_count, fat_count,
                Total_grocery_cost, Grocery_list, Dishes
            """

            for record in records:
                if not isinstance(record, dict):
                    raise StorageError("Invalid meal plan record")

                plan_id = record.get("id")

                if type(plan_id) is not int or plan_id <= 0:
                    raise StorageError("Invalid meal plan ID")

                if plan_id in new_ids:
                    raise StorageError("Duplicate meal plan ID")

                new_ids.add(plan_id)

                values = self._record_values(record)

                if plan_id in existing_ids:
                    # Update an existing meal plan
                    query = """
                        UPDATE saved_meal_plans
                        SET name=%s,
                            date_created=%s,
                            budget=%s,
                            pax=%s,
                            dietary_restrictions=%s,
                            dietary_goal=%s,
                            calorie_count=%s,
                            cuisine=%s,
                            country=%s,
                            protein_count=%s,
                            fat_count=%s,
                            Total_grocery_cost=%s,
                            Grocery_list=%s,
                            Dishes=%s
                        WHERE id=%s
                    """

                    cursor.execute(query, values + (plan_id,))

                else:
                    # Insert a new meal plan
                    placeholders = ", ".join(["%s"] * 15)

                    query = (
                        "INSERT INTO saved_meal_plans "
                        f"(id, {columns}) "
                        f"VALUES ({placeholders})"
                    )

                    cursor.execute(
                        query,
                        (plan_id,) + values
                    )

            # Delete only records removed from the supplied history
            removed_ids = existing_ids - new_ids

            if removed_ids:
                cursor.executemany(
                    "DELETE FROM saved_meal_plans WHERE id=%s",
                    [(plan_id,) for plan_id in removed_ids]
                )

            connection.commit()
            return True

        except (Error, ValueError, TypeError, StorageError) as e:
            connection.rollback()
            raise StorageError("Unable to save meal plans") from e

        finally:
            if cursor is not None:
                cursor.close()
            connection.close()
