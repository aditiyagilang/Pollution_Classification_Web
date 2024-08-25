# db.py

import mysql.connector
from mysql.connector import Error

db_config = {
    'host': 'localhost',
    'database': 'polusi_db',
    'user': 'root',
    'password': ''  
}

def connect_db():
    try:
        connection = mysql.connector.connect(**db_config)
        if connection.is_connected():
            return connection
    except Error as e:
        print("Error while connecting to MySQL", e)
    return None
