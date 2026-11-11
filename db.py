import mysql.connector
from mysql.connector import Error

try:
    # Establish the connection
    connection = mysql.connector.connect(
        host="localhost",
        port=3306,
        user="root",
        password="",      # Replace with your MySQL password
        database="justeat"       # Replace with your database name
    )

    if connection.is_connected():
        db_info = connection.get_server_info
        print(f"Successfully connected to MySQL Server version {db_info}")
        
        cursor = connection.cursor()
        cursor.execute("SELECT DATABASE();")
        record = cursor.fetchone()
        print(f"Connected to database: {record[0]}")

except Error as e:
    print(f"Error while connecting to MySQL: {e}")

finally:
    # Ensure the connection is safely closed
    if 'connection' in locals() and connection.is_connected():
        cursor.close()
        connection.close()
        print("MySQL connection is closed.")