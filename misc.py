'''
Данный файл хранит в себе все необходимые данные для работы приложения.
Представляет из себя набор кортежей словарей предназначеных для
заполнения базы данных командой:
    ``python ./models.py rebuild force``

Список таблиц заполняемых данным файлом:
    - object_types
    - objects
    - current_season
    - actions
    - game_modes
    - bo_types
    - teams
    - rules
    - current_game_state_model
    - player_state
'''


object_types = (
    {"name": "map"},
    {"name": "champ"},
    {"name": "result"}
)

objects = (
    {"type": 1, "name": "Awoken", "shortname": "Awoken", "img_url": "awoken.jpg"},
    {"type": 1, "name": 'Blood Covenant', "shortname": 'BC', "img_url": 'blood_covenant.jpg'},
    {"type": 1, "name": 'Blood Run', "shortname": 'BR', "img_url": 'blood_run.jpg'},
    {"type": 1, "name": 'Corrupted Keep', "shortname": 'CK', "img_url": 'corrupted_keep.jpg'},
    {"type": 1, "name": 'Deep Embrace', "shortname": 'DE', "img_url": 'deep_embrace.jpg'},
    {"type": 1, "name": 'Exile', "shortname": 'Exile', "img_url": 'exile.jpg'},
    {"type": 1, "name": 'Insomnia', "shortname": 'IN', "img_url": 'insomnia.jpg'},
    {"type": 1, "name": 'Ruins of Sarnath', "shortname": 'Ruins', "img_url": 'ruins_of_sarnath.jpg'},
    {"type": 1, "name": 'The Molten Falls', "shortname": 'Molten', "img_url": 'the_molten_falls.jpg'},
    {"type": 1, "name": 'Tower of Koth', "shortname": 'Koth', "img_url": 'tower_of_koth.jpg'},
    {"type": 1, "name": 'Vale of Pnath', "shortname": 'Vale', "img_url": 'vale_of_pnath.jpg'},
    {"type": 2, "name": 'Anarki', "shortname": 'Anarki', "img_url": 'anarki.png'},
    {"type": 2, "name": 'Athena', "shortname": 'Athena', "img_url": 'athena.png'},
    {"type": 2, "name": 'B.J. Blaskowicz', "shortname": 'BJ', "img_url": 'bj.png'},
    {"type": 2, "name": 'Clutch', "shortname": 'Clutch', "img_url": 'clutch.png'},
    {"type": 2, "name": 'Death Knight', "shortname": 'DK', "img_url": 'deathknight.png'},
    {"type": 2, "name": 'Doom', "shortname": 'Doom', "img_url": 'doom.png'},
    {"type": 2, "name": 'Eisen', "shortname": 'Eisen', "img_url": 'eisen.png'},
    {"type": 2, "name": 'Galena', "shortname": 'Galena', "img_url": 'galena.png'},
    {"type": 2, "name": 'Keel', "shortname": 'Keel', "img_url": 'keel.png'},
    {"type": 2, "name": 'Nyx', "shortname": 'Nyx', "img_url": 'nyx.png'},
    {"type": 2, "name": 'Ranger', "shortname": 'Ranger', "img_url": 'ranger.png'},
    {"type": 2, "name": 'Scalebearer', "shortname": 'Scale', "img_url": 'scalebearer.png'},
    {"type": 2, "name": 'Slash', "shortname": 'Slash', "img_url": 'slash.png'},
    {"type": 2, "name": 'Sorlag', "shortname": 'Sorlag', "img_url": 'sorlag.png'},
    {"type": 2, "name": 'Strogg & Peeker', "shortname": 'Strogg', "img_url": 'strogg.png'},
    {"type": 2, "name": 'Visor', "shortname": 'Visor', "img_url": 'visor.png'},
)

current_season = (
    {"object_id": 9},
    {"object_id": 8},
    {"object_id": 11},
    {"object_id": 1},
    {"object_id": 4},
    {"object_id": 6},
    {"object_id": 5},
)

actions = (
    {"name": "pick"},
    {"name": "ban"},
    {"name": "end"},
)

game_modes = (
    {"name": "duel", "player_count": 2},
    {"name": "tdm", "player_count": 4},
)

bo_types = (
    {"name": "bo3"},
    {"name": "bo5"},
    {"name": "bo7"},
    {"name": "bo1"},
)

teams = (
    {"name": "blue"},
    {"name": "red"},
)

rules = (
    {"step": 1, "game_mode_id": 1, "bo_type_id": 1, "object_type_id": 1, "action_id": 2},
    {"step": 2, "game_mode_id": 1, "bo_type_id": 1, "object_type_id": 1, "action_id": 2},
    {"step": 3, "game_mode_id": 1, "bo_type_id": 1, "object_type_id": 1, "action_id": 1},
    {"step": 4, "game_mode_id": 1, "bo_type_id": 1, "object_type_id": 1, "action_id": 1},
    {"step": 5, "game_mode_id": 1, "bo_type_id": 1, "object_type_id": 1, "action_id": 2},
    {"step": 6, "game_mode_id": 1, "bo_type_id": 1, "object_type_id": 1, "action_id": 2},
    {"step": 7, "game_mode_id": 1, "bo_type_id": 1, "object_type_id": 1, "action_id": 1},
    {"step": 8, "game_mode_id": 1, "bo_type_id": 1, "object_type_id": 2, "action_id": 2},
    {"step": 9, "game_mode_id": 1, "bo_type_id": 1, "object_type_id": 2, "action_id": 1},
    {"step": 10, "game_mode_id": 1, "bo_type_id": 1, "object_type_id": 2, "action_id": 1},
    {"step": 11, "game_mode_id": 1, "bo_type_id": 1, "object_type_id": 2, "action_id": 2},
    {"step": 12, "game_mode_id": 1, "bo_type_id": 1, "object_type_id": 2, "action_id": 1},
    {"step": 13, "game_mode_id": 1, "bo_type_id": 1, "object_type_id": 2, "action_id": 1},
    {"step": 14, "game_mode_id": 1, "bo_type_id": 1, "object_type_id": 2, "action_id": 2},
    {"step": 15, "game_mode_id": 1, "bo_type_id": 1, "object_type_id": 2, "action_id": 1},
    {"step": 16, "game_mode_id": 1, "bo_type_id": 1, "object_type_id": 2, "action_id": 1},
    {"step": 17, "game_mode_id": 1, "bo_type_id": 1, "object_type_id": 3, "action_id": 3},
)

current_game_state_model = {
    "room_uuid": "",
    "current_action": "",
    "current_player": "",
    "seed": 0,
    "players": [],
    "maps": [],
    "champs": [],
}

player_state = {
    "nickname": "",
    "map_picks": [],
    "map_bans": [],
    "champ_picks": [],
    "champ_bans": [],
}