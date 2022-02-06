import random
import json

from flask import jsonify, render_template, url_for, redirect, request

from application import app
from forms import CreateForm, JoinForm, MapsForm
from application import _JSONRPC as jsonrpc
from database import Room, Result, generate_report, start_game, join_room



# ------ Маршруты APP ---------------------------------------------------------

@app.route("/")
@app.route("/home")
def home():
    return '<h1>Hello, Flask</h1>'


@app.route("/create", methods=['GET', 'POST'])
def create():
    ''' Форма создания комнаты '''
    form = CreateForm()
    if form.validate_on_submit():
        # Собираем необходимые данные из формы в словарь
        form_data = {}
        for key, value in request.form.items():
            if key != 'csrf_token' and key != 'submit':
                form_data[key] = value

        # Конвертим полученные данные формы в необходимые для начала игры
        start_game_params = form.convert_data(**form_data)

        # Начинаем игру с создания пользователя, комнаты и результата игрока
        game_state = start_game(**start_game_params)

        return redirect(url_for('room', room_uuid=game_state['room_uuid']))

    return render_template('create_form.html', form=form, errors=form.errors)


@app.route("/<room_uuid>/join", methods=['GET', 'POST'])
def join(room_uuid):
    ''' Форма подключения к комнате '''
    form = JoinForm()
    if form.validate_on_submit():
        # Собираем необходимые данные из формы в словарь
        form_data = {}
        form_data["room_uuid"] = room_uuid
        for key, value in request.form.items():
            if key != 'csrf_token' and key != 'submit':
                form_data[key] = value

        join_room_params = form.convert_data(**form_data)
        join_room(**join_room_params)


        return redirect(url_for('room', room_uuid=room_uuid))
    else:
        return render_template('join_form.html', form=form, errors=form.errors,
                               room_uuid=room_uuid)


@app.route("/<room_uuid>/room", methods=['GET', 'POST'])
def room(room_uuid):
    ''' Основная страница выбора, она же комната '''
    return render_template('room.html', room_uuid=room_uuid)




# ------ Маршруты API ---------------------------------------------------------

@jsonrpc.method("app.getState", validate=False)
def getState(room_uuid:str) -> str:
    '''Возвращает текущее состояние игры на основе room_id и nickname
    в JSON формате
    '''

    return json.dumps(generate_report(room_uuid))


@jsonrpc.method("app.updateState")
def updateState(room_uuid:str, action:str, nickname:str, choice:str) -> str:
    '''Принимает выбор игрока, room_id, action, nickname, choice.
    Возвращает json cо всем состоянием игры
    '''
    
    # Ищем комнату и активного игрока
    room = Room.get_room(room_uuid)
    if room.rel_users.nickname != nickname:
        # TODO написать нормальную обработку ошибок
        return

    # Вносим изменения в результат
    try:
        Result.update_result(room.id, action, room.current_user_id, choice)
    except ValueError:
        # TODO написать нормальную обработку ошибок
        print('Something went wrong inside the class method')

    # Возвращаем состояние комнаты
    # TODO Разобраться как вызвать JSON-RPC роут по аналогии с redirect()
    return json.dumps(generate_report(room_uuid))




# ------ Тестовые маршруты ----------------------------------------------------

@app.route("/<room_uuid>/maps")
def maps(room_uuid):
    ''' Страница результатов выбора '''
    return render_template('maps.html', room_uuid=room_uuid)


@app.route("/<room_uuid>/champions")
def champions(room_uuid):
    ''' Страница результатов выбора '''
    return render_template('champions.html', room_uuid=room_uuid)


@app.route("/<room_uuid>/results")
def results(room_uuid):
    ''' Страница результатов выбора '''
    return render_template('results.html', room_uuid=room_uuid)


@app.route("/picking_form", methods=['GET'])
def picking_form():
    ''' Форма пика карт'''
    form = MapsForm()
    return render_template('maps_form.html', form=form)




# ------ маршруты, для проверки работы с xhr запросами ------------------------

@app.route("/state")
def state():
    result = random.choice(['map', 'champ', 'result'])
    response = {'result': result}
    return jsonify(response)

@app.route("/test")
def test():
    return render_template('hello.html')




# ------ Запуск приложения ----------------------------------------------------

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)
