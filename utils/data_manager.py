import json
import os

data_file = "user_money.json"

def load_data():
    if os.path.exists(data_file):
        with open(data_file, "r") as file:
            return json.load(file)
    return {}

def save_data(data):
    with open(data_file, "w") as file:
        json.dump(data, file, indent=4)
