import json
import requests

#from database import Room, User, Result




# ------ Константы -------------------------------------------------------------

URI = 'http://localhost:5000/api'
room_uuid = "7ad138ca-b89e-463d-8345-d7314fa76aa2"



# ------- Функции -------------------------------------------------------------
'''
def test_getState():
    payload = {
        "jsonrpc": "2.0",
        "method": "app.getState",
        "params": {
            "room_uuid": room_uuid
        },
        "id": 1
    }
    headers = {
        "Content-Type": "application/json",dw
    }

    response = requests.post(URI, data=payload, headers=headers)
    print(response.json())
    response.raise_for_status()

# test_getState()


def test_updateState():
    payload = {
        "jsonrpc": "2.0",
        "method": "app.updateState",
        "params": {
            "room_uuid": room_uuid,
            "action": "ban",
            "nickname": "wilson",
            "choice": "awoken"
        },
        "id": 1
    }
    headers = {
        "Content-Type": "application/json",
    }

    response = requests.post(URI, json=payload, headers=headers)
    print(response.json())
    response.raise_for_status()

'''

# test_updateState()


# Тестируем создание юзера
# user_id = User.create_user('wilson')

# Тестируем создание комнаты
# game_mode = 1
# bo_type = 1
# seed = 1
# room = Room.create_room(game_mode, bo_type, seed)

# Тестируем создание результата
# result = Result.create_result(user_id, room['id'], team_id=1)
# result

# Тестируем интерфейс формы подключения
# room_id = IJoinForm('fccb25ed-6373-4d6f-9087-5fce45a2fd64')

# Тестируем интерфейс формы создания игры
# game_mode = 'duel'
# bo_type = 'bo3'
# seed = 'You'
# gbs = ICreateForm(game_mode, bo_type, seed)


# Тестируем room.update_result
# room_uuid = '63b71f72-7eab-4de9-bbf6-fc1dd8bc64da'
# nickname = 'pashok'
# room = Room.get_room(room_uuid)
# if room.rel_users.nickname != nickname:
#     raise Exception(f'Очередь пользователя {nickname} еще не наступила')
# room.update_result('ban','map','Awoken')
# room


# Тестируем room.next_user()
# room_uuid = '56cff8ad-f1c1-4f20-b438-3ce9fbdd6b57'
# room = Room.get_room(room_uuid)
# room.next_step()
# room



headers = {
    'Content-Type': 'application/json',
}

payload = {
    "jsonrpc": "2.0",
    "method": "app.test",
    "params": {
        'lastname': 'Zakharchenko',
        'name': 'Dmitry',
        'surname': 'Leonidovich',
    },
    "id": 1
}

response = requests.post(URI, json=payload, headers=headers)
response.raise_for_status()

print(response.json())

