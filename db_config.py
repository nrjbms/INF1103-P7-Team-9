#Done by Chong Li Heng 2603072
import os
from dotenv import load_dotenv
import mysql.connector
from mysql.connector import Error

load_dotenv()

db_host = os.getenv("DB_HOST", "localhost")  # Defaults to localhost if not in Docker
db_user = os.getenv("DB_USER", "root")       # Defaults to root if not in Docker
db_password = os.getenv("DB_PASSWORD", "")   # SQL Password
db_name = os.getenv("DB_NAME", "justeat")    # Database name
db_port = int(os.getenv("DB_PORT", 3306))   

#try connecting to database
def get_db_connection():
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