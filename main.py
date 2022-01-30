import random
import json

from flask import jsonify, render_template, url_for, redirect, request

from application import app
from forms import CreateForm, JoinForm
from application import _JSONRPC as jsonrpc
from database import Room, Current_season, Object


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
        start_game_params = {}
        for key, value in request.form.items():
            if key != 'csrf_token' and key != 'submit':
                start_game_params[key] = value

        print(
            start_game_params
        )
        
        ''' TODO Функция start_game: должна создавать пользователя, комнату
        и результат. Так же должна возвращать json со всеми значениями формы
        для фронтенда.
        '''
        # game_params = start_game(**start_game_params)
        # return redirect(url_for('room', room_id=room_id, params=game_params))
        
        room_id = 123434244142342
        return redirect(url_for('room', room_id=room_id))
    return render_template('create_form.html', form=form, errors=form.errors)


@app.route("/<room_id>/join", methods=['GET', 'POST'])
def join(room_id):
    ''' Форма подключения к комнате '''
    form = JoinForm()
    if form.validate_on_submit():

        # TODO вставить функцию подключения к комнате

        return redirect(url_for('room', room_id=room_id))
    else:
        return render_template('join_form.html', form=form, errors=form.errors, room_id=room_id)


@app.route("/<room_id>/room", methods=['GET', 'POST'])
def room(room_id):
    ''' Основная страница выбора, она же комната '''
    return render_template('results.html', room_id=room_id)




# ------ Маршруты API ---------------------------------------------------------

@jsonrpc.method("app.getState")
def getState(room_uuid:str) -> str:
    '''Возвращает текущее состояние игры на основе room_id и nickname'''

    # Получаем инфу по комнате и по доступным картам
    room = Room.get_room(room_uuid=room_uuid)
    champions = Object.query.filter_by(type=2).all()
    current_season = Current_season.query.all()
    season_maps = [item.rel_objects for item in current_season]
    results = room.rel_results

    # Генерим инфу по игрокам
    player_state = {}
    player_states = []
    current_game_state = {}
    for result in results:
        player_state['nickname'] = result.rel_users.nickname
        player_state['map_picks'] = [
            obj.name for obj in result.picks if obj.type==1
        ]
        player_state['map_bans'] = [
            obj.name for obj in result.bans if obj.type==1
        ]
        player_state['champ_picks'] = [
            obj.name for obj in result.picks if obj.type==2
        ]
        player_state['champ_bans'] = [
            obj.name for obj in result.bans if obj.type==2
        ]
        player_states.append(player_state)
        player_state = {}

    # Генерим инфу по комнате
    current_game_state['current_action'] = room.rel_actions.name
    current_game_state['players'] = player_states
    current_game_state['room_uuid'] = room_uuid
    current_game_state['seed'] = room.seed

    current_game_state['maps'] = [
        map.name for map in season_maps if map.type==1
    ]
    current_game_state['champs'] = [
        champ.name for champ in champions
    ]

    if room.rel_users != None:
        current_game_state['current_player'] = room.rel_users.nickname
    else:
        current_game_state['current_player'] = ''

    return json.dumps(current_game_state)




# ------ Тестовые маршруты ----------------------------------------------------

@app.route("/<room_id>/maps")
def maps(room_id):
    ''' Страница результатов выбора '''
    return render_template('maps.html', room_id=room_id)


@app.route("/<room_id>/champions")
def champions(room_id):
    ''' Страница результатов выбора '''
    return render_template('champions.html', room_id=room_id)


@app.route("/<room_id>/results")
def results(room_id):
    ''' Страница результатов выбора '''
    return render_template('results.html', room_id=room_id)




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
