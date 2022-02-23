import json

from flask import render_template, send_from_directory, url_for, redirect, request

from application import app
from forms import CreateForm, JoinForm
from application import _JSONRPC as jsonrpc
from database import Room, generate_report, start_game, join_room


''' TODO Начать делать тесты!!! Становится понятно зачем они вообще нужны...
Отсутвие тестов приводит к тому что мы упускаем поломки кода в связи со свежими
изменениями. Чем дольше мы не исправляем эти ошибки тем сложнее их исправить
в дальнейшем.
'''

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
        params = start_game(**start_game_params)
        game_state = generate_report(params['room_uuid'])

        return redirect(url_for('room', room_uuid=params['room_uuid'],
                                nickname=params['nickname'],
                                game_state=game_state))

    return render_template('create_form.html', form=form, errors=form.errors)


@app.route("/<uuid:room_uuid>/join", methods=['GET', 'POST'])
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

        # Подключаемся к комнате, создавая пользователя и его результата
        operation_result = join_room(**form_data)

        game_state = generate_report(room_uuid)

        if operation_result == False:
            return redirect(url_for('room', room_uuid=room_uuid))

        return redirect(url_for('room', room_uuid=room_uuid,
                                nickname=form_data['nickname'],
                                game_state=game_state))
    else:
        return render_template('join_form.html', form=form, errors=form.errors,
                               room_uuid=room_uuid)


@app.route("/<uuid:room_uuid>")
@app.route("/<uuid:room_uuid>/<string:nickname>", methods=['GET'])
def room(room_uuid, nickname=None):
    ''' Основная страница выбора, она же комната '''

    game_state = generate_report(room_uuid)

    return render_template('room.html', room_uuid=room_uuid,
                            game_state=game_state)




# ------ Маршруты API ---------------------------------------------------------

@jsonrpc.method("app.getState", validate=False)
def getState(room_uuid:str) -> str:
    '''Возвращает текущее состояние игры на основе room_id в JSON формате
    '''

    return json.dumps(generate_report(room_uuid))


@jsonrpc.method("app.updateState")
def updateState(room_uuid:str, action:str, nickname:str, choice:str,
                object_type:str) -> str:
    '''Принимает выбор игрока, room_id, action, nickname, choice.
    Возвращает json cо всем состоянием игры
    '''
    
    # Ищем комнату и активного игрока
    room = Room.get_room(room_uuid)
    if room.rel_users.nickname != nickname:
        raise Exception(f'Очередь пользователя {nickname} еще не наступила')

    # Вносим изменения в результат
    try:
        room.update_result(action, object_type, choice)
        room.next_step()
    except ValueError:
        # TODO написать нормальную обработку ошибок
        print('Something went wrong inside the class method')

    # Возвращаем состояние комнаты
    # TODO Разобраться как вызвать JSON-RPC роут по аналогии с redirect()
    return json.dumps(generate_report(room_uuid))




# ------ Тестовые маршруты ----------------------------------------------------

@app.route("/<uuid:room_uuid>/results")
def results(room_uuid):
    ''' Страница результатов выбора '''

    # TODO Если игра не окончена то redirect в комнату

    game_state = generate_report(room_uuid)

    # TODO Условие должно быть сгенерировано на основе режима игры в комнате.
    if game_state['step'] >= 16:
    
        player_1 = game_state['players'][0]
        player_2 = game_state['players'][1]

        index = 1
        maps = player_1['map_picks']
        for map in player_2['map_picks']:
            maps.insert(1,map)
            index = index + 2

        game_results = []
        for result in zip(maps, player_1['champ_picks'], player_2['champ_picks']):
            game_results.append(result)

        return render_template('results.html', room_uuid=room_uuid,
                               game_results=game_results, game_state=game_state)
    
    return redirect('room', room_uuid=room_uuid)


@app.route("/robots.txt")
def robots():
    return send_from_directory(app.static_folder, 'robots.txt')

# ------ Запуск приложения ----------------------------------------------------

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)
