import mysql.connector
from mysql.connector import Error

def get_db_connection():
    """Establishes and returns a connection to the MySQL database."""
    try:
        connection = mysql.connector.connect(
            host="localhost",
            port=3306,
            user="root",
            password="",  # Replace with your actual MySQL password
            database="justeat"         # Targets your database name
        )
        
        if connection.is_connected():
            return connection

    except Error as e:
        print(f"Error while connecting to MySQL: {e}")
        return None