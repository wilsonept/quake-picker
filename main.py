import json

from flask import render_template, url_for, redirect, request

from forms import CreateForm, JoinForm
from models import Room, generate_report, start_game, join_game
from application import app
from application import _JSONRPC as jsonrpc
from application import _SOCK as sock


"""
Основной файл запуска приложения и по совместительству файл маршрутов.
"""

# TODO Перепроверить код на наличие сравнения с булевой.

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
        # Собираем необходимые данные из формы в словарь
        form_data = {}
        for key, value in request.form.items():
            if key != "csrf_token" and key != "submit":
                form_data[key] = value

        # Конвертим полученные данные формы в необходимые для начала игры
        start_game_params = form.convert_data(**form_data)

        # Начинаем игру с создания пользователя, комнаты и результата игрока
        params = start_game(**start_game_params)

        return redirect(
            url_for("room",
                room_uuid=params["room_uuid"],
                nickname=params["nickname"])
        )

    return render_template("create_form.html", form=form, errors=form.errors)


@app.route("/join/<uuid:room_uuid>", methods=["GET", "POST"])
def join(room_uuid):
    """Форма подключения к комнате."""
    form = JoinForm()
    if form.validate_on_submit():
        # Собираем необходимые данные из формы в словарь
        form_data = {}
        form_data["room_uuid"] = room_uuid
        for key, value in request.form.items():
            if key != "csrf_token" and key != "submit":
                form_data[key] = value

        # NOTE При переходе на postgresql функцию str надо убрать.
        room_uuid = str(room_uuid)
        
        # Подключаемся к комнате, создавая пользователя и его результата
        operation_result = join_game(**form_data)

        # game_state = generate_report(room_uuid)

        # Переходим в режим наблюдателя.
        if operation_result == False:
            return redirect(url_for("room", room_uuid=room_uuid))

        return redirect(
            url_for("room",
                room_uuid=room_uuid,
                nickname=form_data["nickname"])
        )
    else:
        return render_template("join_form.html", form=form, errors=form.errors,
                               room_uuid=room_uuid)


@app.route("/<uuid:room_uuid>")
@app.route("/<uuid:room_uuid>/<string:nickname>", methods=["GET","POST"])
def room(room_uuid, nickname=None):
    """Основная страница выбора, она же комната."""

    # NOTE При переходе на postgresql функцию str надо убрать.
    game_state = generate_report(str(room_uuid))

    return render_template("room.html", room_uuid=room_uuid,
                           game_state=game_state)


@app.route("/results/<uuid:room_uuid>")
def results(room_uuid):
    """Страница результатов выбора."""

    game_state = generate_report(room_uuid)

    # 16 это количество активных шагов в игре. Для всех режимов оно остается
    # одинаковым меняется только количество банов. Чем больше карт необходимо
    # сыграть тем меньше банов необходимо сделать. Для проверки на окончание
    # выбора в БД присутствует еще 1 шаг под номером 17. Он добавлен для того
    # что бы можно было оставить общую логику с инкрементированием шага в
    # комнате. Если бы его не было, то БД постоянно ругалась из-за
    # неразрешенной связи с таблицей Objects.
    if game_state["current_object"] == "result":
    
        # Расставляем игроков согласно очереди подключения к комнате.
        if game_state["players"][0]["team"] == 1:
            player_1 = game_state["players"][1]
            player_2 = game_state["players"][0]
        else:
            player_1 = game_state["players"][0]
            player_2 = game_state["players"][1]

        index = 1
        maps = player_1["map_choices"]["picks"]
        for map in player_2["map_choices"]["picks"]:
            maps.insert(1,map)
            index = index + 2

        game_results = []
        for result in zip(maps, player_1["champ_choices"]["picks"],
                          player_2["champ_choices"]["picks"]):
            game_results.append(result)

        return render_template("results.html",
                               room_uuid=room_uuid,
                               game_results=game_results,
                               game_state=game_state)
    
    return redirect("room", room_uuid=room_uuid)


# ------ Маршруты API --------------------------------------------------

@jsonrpc.method("app.getState", validate=False)
def getState(room_uuid:str) -> str:
    """Возвращает текущее состояние игры на основе room_id в JSON формате."""

    return json.dumps(generate_report(room_uuid))


@jsonrpc.method("app.updateState")
def updateState(room_uuid:str, action:str, nickname:str, choice:str,
                object_type:str, map_name:str=None) -> str:
    """
    Принимает выбор игрока:
        
        room_id - uuid комнаты.
        action - действие (ban или pick).
        nickname - имя игрока который выполняет действие.
        choice - название карты или чемпиона.
        object_type - тип выбора (map или champ)

    Возвращает json cо всем состоянием игры.
    """
    
    # Ищем комнату и активного игрока
    room = Room.query.filter_by(room_uuid=room_uuid).first()
    if room.rel_users.nickname != nickname:
        raise Exception(f"Очередь пользователя {nickname} еще не наступила")

    # Вносим изменения в результат
    try:
        room.update_result(action, object_type, choice, map_name)
        room.next_step()
    except ValueError:
        # TODO написать нормальную обработку ошибок
        print("Something went wrong inside the class method")

    # Возвращаем состояние комнаты
    # TODO Разобраться как вызвать JSON-RPC роут по аналогии с redirect()
    return json.dumps(generate_report(room_uuid))


# ------ Тестовые маршруты ---------------------------------------------

@sock.route("/get_state")
def get_state(ws):
    """
    Возвращаем состояние игры через websocket.
    Принимает на вход строку состоящую из действия и uuid комнаты разделенных
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
