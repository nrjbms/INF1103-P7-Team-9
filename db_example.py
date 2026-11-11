from db_config import get_db_connection

def fetch_restaurants():
    # Get the connection using our config function
    connection = get_db_connection()
    
    if connection is None:
        print("Failed to connect to the database.")
        return

    try:
        cursor = connection.cursor()
        
        # Execute query to retrieve restaurants data
        query = "SELECT id, name, cuisine_type, rating, is_active FROM restaurants;"
        cursor.execute(query)
        
        rows = cursor.fetchall()
        
        print(f"Successfully retrieved {len(rows)} record(s):\n")
        print(f"{'ID':<5} | {'Name':<20} | {'Cuisine':<15} | {'Rating':<8} | {'Active'}")
        print("-" * 65)
        
        for row in rows:
            rest_id, name, cuisine, rating, is_active = row
            print(f"{rest_id:<5} | {name:<20} | {cuisine:<15} | {rating:<8} | {is_active}")

    except Exception as e:
        print(f"An error occurred while executing the query: {e}")

    finally:
        # Always clean up cursors and connections
        if cursor:
            cursor.close()
        if connection.is_connected():
            connection.close()
            print("\nMySQL connection closed.")

if __name__ == "__main__":
    fetch_restaurants()