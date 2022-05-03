"""
Данный файл хранит в себе все необходимые данные для работы приложения.
Представляет из себя набор кортежей словарей предназначеных для
заполнения базы данных командой:
    `python ./models.py rebuild force`

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
    {"type": 1, "name": "Awoken", "short_name": "AWOKEN", "img_url": "/static/images/maps/awoken.jpg"},
    {"type": 1, "name": "Blood Covenant", "short_name": "BC", "img_url": "/static/images/maps/bc.jpg"},
    {"type": 1, "name": "Blood Run", "short_name": "BR", "img_url": "/static/images/maps/br.jpg"},
    {"type": 1, "name": "Corrupted Keep", "short_name": "CK", "img_url": "/static/images/maps/ck.jpg"},
    {"type": 1, "name": "Deep Embrace", "short_name": "DE", "img_url": "/static/images/maps/de.jpg"},
    {"type": 1, "name": "Exile", "short_name": "EXILE", "img_url": "/static/images/maps/exile.jpg"},
    {"type": 1, "name": "Insomnia", "short_name": "IN", "img_url": "/static/images/maps/in.jpg"},
    {"type": 1, "name": "Ruins of Sarnath", "short_name": "RUINS", "img_url": "/static/images/maps/ruins.jpg"},
    {"type": 1, "name": "The Molten Falls", "short_name": "MOLTEN", "img_url": "/static/images/maps/molten.jpg"},
    {"type": 1, "name": "Tower of Koth", "short_name": "KOTH", "img_url": "/static/images/maps/koth.jpg"},
    {"type": 1, "name": "Vale of Pnath", "short_name": "VALE", "img_url": "/static/images/maps/vale.jpg"},
    {"type": 2, "name": "Anarki", "short_name": "ANARKI", "img_url": "/static/images/champions/anarki.png", "r_img_url": "/static/images/champions/r_anarki.png"},
    {"type": 2, "name": "Athena", "short_name": "ATHENA", "img_url": "/static/images/champions/athena.png", "r_img_url": "/static/images/champions/r_athena.png"},
    {"type": 2, "name": "B.J. Blaskowicz", "short_name": "BJ", "img_url": "/static/images/champions/bj.png", "r_img_url": "/static/images/champions/r_bj.png"},
    {"type": 2, "name": "Clutch", "short_name": "CLUTCH", "img_url": "/static/images/champions/clutch.png", "r_img_url": "/static/images/champions/r_clutch.png"},
    {"type": 2, "name": "Death Knight", "short_name": "DK", "img_url": "/static/images/champions/dk.png", "r_img_url": "/static/images/champions/r_dk.png"},
    {"type": 2, "name": "Doom", "short_name": "DOOM", "img_url": "/static/images/champions/doom.png", "r_img_url": "/static/images/champions/r_doom.png"},
    {"type": 2, "name": "Eisen", "short_name": "EISEN", "img_url": "/static/images/champions/eisen.png", "r_img_url": "/static/images/champions/r_eisen.png"},
    {"type": 2, "name": "Galena", "short_name": "GALENA", "img_url": "/static/images/champions/galena.png", "r_img_url": "/static/images/champions/r_galena.png"},
    {"type": 2, "name": "Keel", "short_name": "KEEL", "img_url": "/static/images/champions/keel.png", "r_img_url": "/static/images/champions/r_keel.png"},
    {"type": 2, "name": "Nyx", "short_name": "NYX", "img_url": "/static/images/champions/nyx.png", "r_img_url": "/static/images/champions/r_nyx.png"},
    {"type": 2, "name": "Ranger", "short_name": "RANGER", "img_url": "/static/images/champions/ranger.png", "r_img_url": "/static/images/champions/r_ranger.png"},
    {"type": 2, "name": "Scalebearer", "short_name": "SCALE", "img_url": "/static/images/champions/scale.png", "r_img_url": "/static/images/champions/r_scale.png"},
    {"type": 2, "name": "Slash", "short_name": "SLASH", "img_url": "/static/images/champions/slash.png", "r_img_url": "/static/images/champions/r_slash.png"},
    {"type": 2, "name": "Sorlag", "short_name": "SORLAG", "img_url": "/static/images/champions/sorlag.png", "r_img_url": "/static/images/champions/r_sorlag.png"},
    {"type": 2, "name": "Strogg & Peeker", "short_name": "STROGG", "img_url": "/static/images/champions/strogg.png", "r_img_url": "/static/images/champions/r_strogg.png"},
    {"type": 2, "name": "Visor", "short_name": "VISOR", "img_url": "/static/images/champions/visor.png", "r_img_url": "/static/images/champions/r_visor.png"},
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