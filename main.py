import json

from flask import render_template, url_for, redirect, request

from forms import CreateForm, JoinForm
from models import Room, generate_report, start_game, join_game
from application import app
from application import _JSONRPC as jsonrpc
from application import _SOCK as sock
from utils import request_to_dict

"""
Основной файл запуска приложения и по совместительству файл маршрутов.
"""


# ------ Маршруты APP --------------------------------------------------

@app.route("/")
@app.route("/home")
def home():
    return redirect(url_for("create"))


@app.route("/create", methods=["GET", "POST"])
def create():
    """Форма создания комнаты."""
    form = CreateForm()
    if form.validate_on_submit():
        # Собираем необходимые данные из формы в словарь.
        form_data = request_to_dict(request)

        # Начинаем игру с создания пользователя, комнаты и сессии игрока.
        room = start_game(**form_data)
        room_uuid = room.room_uuid
        nickname = room.rel_sessions[0].rel_user.nickname

        redirect_url = url_for("room", room_uuid=room_uuid,
                               nickname=nickname)
        return redirect(redirect_url)

    # Отображения формы создания игры.
    return render_template("create_form.html", form=form, errors=form.errors)


@app.route("/join/<uuid:room_uuid>", methods=["GET", "POST"])
def join(room_uuid):
    """Форма подключения к комнате."""
    form = JoinForm()
    if form.validate_on_submit():
        # Собираем необходимые данные из формы в словарь.
        form_data = request_to_dict(request, room_uuid)

        # Подключаемся к комнате, создавая пользователя и его сессию.
        is_joined = join_game(**form_data)

        # Переходим в режим наблюдателя.
        if not is_joined:
            return redirect(url_for("room", room_uuid=form_data["room_uuid"]))

        # Подключаемся в режиме игрока.
        redirect_url = url_for("room", room_uuid=form_data["room_uuid"],
                               nickname=form_data["nickname"])
        return redirect(redirect_url)

    else:
        # Отображение формы подключения к игре.
        return render_template("join_form.html", form=form, errors=form.errors,
                               room_uuid=room_uuid)


@app.route("/<uuid:room_uuid>")
@app.route("/<uuid:room_uuid>/<string:nickname>", methods=["GET","POST"])
def room(room_uuid, nickname=None):
    """Основная страница выбора, она же комната."""

    # NOTE При переходе на postgresql функцию str надо убрать.
    room_uuid = str(room_uuid)
    game_state = generate_report(room_uuid)

    # Отображаем шаблон комнаты.
    return render_template("room.html", room_uuid=room_uuid,
                           game_state=game_state)


@app.route("/results/<uuid:room_uuid>")
def results(room_uuid):
    """Страница результатов выбора."""

    room_uuid = str(room_uuid)
    game_state = generate_report(room_uuid)

    # 16 это количество активных шагов в игре. Для всех режимов оно
    # остается # одинаковым меняется только количество банов. Чем больше
    # карт необходимо сыграть тем меньше банов необходимо сделать. Для
    # проверки на окончание выбора в БД присутствует еще 1 шаг под
    # номером 17. Он добавлен для того что бы можно было оставить общую
    # логику с инкрементированием шага в комнате. Если бы его не было,
    # то БД постоянно ругалась из-за неразрешенной связи с таблицей
    # Objects.

    if game_state["current_object_type"] == "result":
        # Формируем словарь пар с одинаковым названием карты.
        # NOTE Данный код работает только для режима duel.
        map_short_name = game_state["champ_choices"][0]["map_short_name"]
        pair = []
        players_choices = {}
        for champ in game_state["champ_choices"]:
            if map_short_name == champ["map_short_name"]:
                pair.append(champ)
            else:
                players_choices[map_short_name] = pair
                map_short_name = champ["map_short_name"]
                pair = [champ]

        players_choices[map_short_name] = pair
        # Отображаем шаблон результатов.
        return render_template("results.html",
                               room_uuid=room_uuid,
                               game_state=game_state,
                               players_choices=players_choices)
    
    # Отображаем шаблон комнаты.
    return redirect("room", room_uuid=room_uuid)


# ------ Маршруты API --------------------------------------------------

@jsonrpc.method("app.getState", validate=False)
def getState(room_uuid:str) -> str:
    """Возвращает текущее состояние игры на основе room_id в JSON формате."""

    room_uuid = str(room_uuid)
    return json.dumps(generate_report(room_uuid))


@jsonrpc.method("app.updateState")
def updateState(room_uuid:str, action:str, nickname:str, choice:str,
                object_type:str, map_sname:str=None) -> str:
    """
    Принимает выбор игрока:
        
        - :str:`room_id`: uuid комнаты.
        - :str:`action`: действие (ban или pick).
        - :str:`nickname`: имя игрока который выполняет действие.
        - :str:`choice`: название карты или чемпиона.
        - :str:`object_type`: тип выбора (map или champ)
        - :str:`map_sname`: короткое имя карты (при выборе чемпиона).

    Возвращает json cо всем состоянием игры.
    """
    
    # Ищем комнату и активного игрока
    room_uuid = str(room_uuid)
    room = Room.query.filter_by(room_uuid=room_uuid).first()

    # Вносим изменения в результат
    room.save_choice(nickname, action, object_type, choice, map_sname)

    # Возвращаем состояние комнаты
    return json.dumps(generate_report(room_uuid))


# ------ Тестовые маршруты ---------------------------------------------

@sock.route("/get_state")
def getStateWS(ws):
    """
    Возвращаем состояние игры через `websocket`.
    Принимает на вход строку состоящую из действия и `uuid` комнаты разделенных
    пробелом.
    
    Например:

        update 654a5711-3f89-4702-8d95-3db9cb8c4215
    """
    while True:
        
        # TODO Переделать что бы websocket принимал JSON, 
        # а не строку через пробел
        data = ws.receive()
        action, room_uuid = data.split(" ")[0], data.split(" ")[1]

        if action == "update" and room_uuid:
            try:
                ws.send(json.dumps(generate_report(room_uuid)))
            except:
                ws.send(None)
        else:
            ws.send(None)


# ------ Запуск приложения ---------------------------------------------

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
