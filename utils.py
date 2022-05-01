import json
import requests


"""
Файл с вспомогательными функциями и полезностями.
"""


# ------ Функции -------------------------------------------------------

def load_json(json_file):
    with open(json_file) as f:
        json_data = json.load(f)
        return json_data


def file_downloader(path_to_folder, items):
    """Функция для скачивания картинок"""
    for item in items:
        file_name = item.split("/")[-1]
        full_name = path_to_folder + "/" + file_name
        response = requests.get(item)
        with open(full_name, "wb") as f:
            f.write(response.content)


# ------ Разное --------------------------------------------------------

"""Ссылки до изображений использованных в приложении."""

pics = [
    # champs
    "https://dev.quake-champions.com/css/images/champions/nyx.png",
    "https://dev.quake-champions.com/css/images/champions/anarki.png",
    "https://dev.quake-champions.com/css/images/champions/slash.png",
    "https://dev.quake-champions.com/css/images/champions/athena.png",
    "https://dev.quake-champions.com/css/images/champions/ranger.png",
    "https://dev.quake-champions.com/css/images/champions/visor.png",
    "https://dev.quake-champions.com/css/images/champions/galena.png",
    "https://dev.quake-champions.com/css/images/champions/bj.png",
    "https://dev.quake-champions.com/css/images/champions/doom.png",
    "https://dev.quake-champions.com/css/images/champions/strogg.png",
    "https://dev.quake-champions.com/css/images/champions/deathknight.png",
    "https://dev.quake-champions.com/css/images/champions/eisen.png",
    "https://dev.quake-champions.com/css/images/champions/scalebearer.png",
    "https://dev.quake-champions.com/css/images/champions/clutch.png",
    "https://dev.quake-champions.com/css/images/champions/sorlag.png",
    "https://dev.quake-champions.com/css/images/champions/keel.png",
    # maps
    "https://dev.quake-champions.com/css/images/maps/the_molten_falls.jpg",
    "https://dev.quake-champions.com/css/images/maps/ruins_of_sarnath.jpg",
    "https://dev.quake-champions.com/css/images/maps/vale_of_pnath.jpg",
    "https://dev.quake-champions.com/css/images/maps/awoken.jpg",
    "https://dev.quake-champions.com/css/images/maps/corrupted_keep.jpg",
    "https://dev.quake-champions.com/css/images/maps/exile.jpg",
    "https://dev.quake-champions.com/css/images/maps/deep_embrace.jpg"
]

path = "static/images/champions"