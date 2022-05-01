"""
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
"""


object_types = (
    {"name": "map"},
    {"name": "champ"},
    {"name": "result"}
)

objects = (
    {"type": 1, "name": "Awoken", "short_name": "AWOKEN", "img_url": "awoken.jpg"},
    {"type": 1, "name": "Blood Covenant", "short_name": "BC", "img_url": "blood_covenant.jpg"},
    {"type": 1, "name": "Blood Run", "short_name": "BR", "img_url": "blood_run.jpg"},
    {"type": 1, "name": "Corrupted Keep", "short_name": "CK", "img_url": "corrupted_keep.jpg"},
    {"type": 1, "name": "Deep Embrace", "short_name": "DE", "img_url": "deep_embrace.jpg"},
    {"type": 1, "name": "Exile", "short_name": "EXILE", "img_url": "exile.jpg"},
    {"type": 1, "name": "Insomnia", "short_name": "IN", "img_url": "insomnia.jpg"},
    {"type": 1, "name": "Ruins of Sarnath", "short_name": "RUINS", "img_url": "ruins_of_sarnath.jpg"},
    {"type": 1, "name": "The Molten Falls", "short_name": "MOLTEN", "img_url": "the_molten_falls.jpg"},
    {"type": 1, "name": "Tower of Koth", "short_name": "KOTH", "img_url": "tower_of_koth.jpg"},
    {"type": 1, "name": "Vale of Pnath", "short_name": "VALE", "img_url": "vale_of_pnath.jpg"},
    {"type": 2, "name": "Anarki", "short_name": "ANARKI", "img_url": "anarki.png"},
    {"type": 2, "name": "Athena", "short_name": "ATHENA", "img_url": "athena.png"},
    {"type": 2, "name": "B.J. Blaskowicz", "short_name": "BJ", "img_url": "bj.png"},
    {"type": 2, "name": "Clutch", "short_name": "CLUTCH", "img_url": "clutch.png"},
    {"type": 2, "name": "Death Knight", "short_name": "DK", "img_url": "deathknight.png"},
    {"type": 2, "name": "Doom", "short_name": "DOOM", "img_url": "doom.png"},
    {"type": 2, "name": "Eisen", "short_name": "EISEN", "img_url": "eisen.png"},
    {"type": 2, "name": "Galena", "short_name": "GALENA", "img_url": "galena.png"},
    {"type": 2, "name": "Keel", "short_name": "KEEL", "img_url": "keel.png"},
    {"type": 2, "name": "Nyx", "short_name": "NYX", "img_url": "nyx.png"},
    {"type": 2, "name": "Ranger", "short_name": "RANGER", "img_url": "ranger.png"},
    {"type": 2, "name": "Scalebearer", "short_name": "SCALE", "img_url": "scalebearer.png"},
    {"type": 2, "name": "Slash", "short_name": "SLASH", "img_url": "slash.png"},
    {"type": 2, "name": "Sorlag", "short_name": "SORLAG", "img_url": "sorlag.png"},
    {"type": 2, "name": "Strogg & Peeker", "short_name": "STROGG", "img_url": "strogg.png"},
    {"type": 2, "name": "Visor", "short_name": "VISOR", "img_url": "visor.png"},
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