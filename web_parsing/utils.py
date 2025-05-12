import json
import os

def read_file(path_to_file):
    try:
        file = open(path_to_file, "r")
        return file.read()
    except Exception as e:
        print("Cant access the file: " + e)

def read_json(file_path):
    with open(file_path) as f:
        json_object = json.load(f)
        return json_object

def get_db_url():
    host = os.getenv('DB_HOST', 'localhost')
    port = os.getenv('DB_PORT', '5432')
    db_name = os.getenv('DB_NAME', 'parse_db')
    user = os.getenv('DB_USER', 'parser')
    password = os.getenv('DB_PASSWORD', '123456')
    
    return f"postgresql://{user}:{password}@{host}:{port}/{db_name}"