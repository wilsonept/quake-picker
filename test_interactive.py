import json
import requests

from database import Room, User, Result




# ------ Константы -------------------------------------------------------------

URI = 'http://localhost:5000/api'


# ------- Функции -------------------------------------------------------------

def test_getState():
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

# test_getState()


def test_updateState():
    payload = {
        "jsonrpc": "2.0",
        "method": "app.updateState",
        "params": {
            "room_uuid": "dc3ad9c1-7452-40b6-99a1-e98ddc18a31e",
            "action": "ban",
            "nickname": "wilson",
            "choice": "awoken"
        },
        "id": 1
    }
    headers = {
        "Content-Type": "application/json",
    }

    response = requests.post(URI, data=json.dumps(payload), headers=headers)
    print(response.json())
    response.raise_for_status()

# test_updateState()


user_id = User.create_user('wilson')

game_mode = 1
bo_type = 1
seed = 1

room = Room.create_room(game_mode, bo_type, seed)

result = Result.create_result(user_id, room['id'], team_id=1)

result