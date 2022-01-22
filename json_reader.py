import json

def load_json(json_file):
    with open(json_file) as f:
        json_data = json.load(f)
        return json_data