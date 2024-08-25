import os
from mysql.connector import connect, Error

def load_env_variables(env_path='.env'):
    env_vars = {}
    with open(env_path, 'r') as file:
        for line in file:
            if line.startswith('#') or not line.strip():
                continue
            key, value = line.strip().split('=', 1)
            env_vars[key] = value
    return env_vars

env_vars = load_env_variables()

db_config = {
    'host': env_vars.get('DATABASE_HOST'),
    'database': env_vars.get('DATABASE_NAME'),
    'user': env_vars.get('DATABASE_USER'),
    'password': env_vars.get('DATABASE_PASSWORD')
}

def connect_db():
    try:
        connection = connect(**db_config)
        if connection.is_connected():
            return connection
    except Error as e:
        print("Error while connecting to MySQL", e)
    return None
