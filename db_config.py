# import mysql.connector
# from mysql.connector import Error

# def get_db_connection():
#     try:
#         connection = mysql.connector.connect(
#             host="localhost",
#             port=3306,
#             user="root",
#             password="",  # Replace with your actual MySQL password
#             database="justeat"         # Targets your database name
#         )
        
#         if connection.is_connected():
#             return connection

#     except Error as e:
#         print(f"Error while connecting to MySQL: {e}")
#         return None

import os
from dotenv import load_dotenv
import mysql.connector
from mysql.connector import Error

load_dotenv()

db_host = os.getenv("DB_HOST", "localhost")  # Defaults to localhost if not in Docker
db_user = os.getenv("DB_USER", "root")
db_password = os.getenv("DB_PASSWORD", "")   # Match your actual MySQL password
db_name = os.getenv("DB_NAME", "justeat")    # Defaults to 'justeat' based on your old code
db_port = int(os.getenv("DB_PORT", 3306))

def get_db_connection():
    """Establishes and returns a connection to the MySQL database."""
    try:
        connection = mysql.connector.connect(
            host=db_host,
            port=db_port,
            user=db_user,
            password=db_password,
            database=db_name
        )
        
        if connection.is_connected():
            return connection

    except Error as e:
        print(f"Error while connecting to MySQL: {e}")
        return None