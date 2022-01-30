import json

import requests

# ------ Константы -------------------------------------------------------------

URI = 'http://localhost:5000/api'


# ------- Функции -------------------------------------------------------------

def test_get_state():
    payload = {
        "jsonrpc": "2.0",
        "method": "app.getState",
        "params": {
            "room_uuid": "af052543-9550-4a4a-b5d6-ae742eba2fad"
        },
        "id": 1
    }
    headers = {
        "Content-Type": "application/json",
    }

    response = requests.post(URI, data=json.dumps(payload), headers=headers)
    print(response.json())
    response.raise_for_status()


test_get_state()
