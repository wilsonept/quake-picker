import random
from flask import jsonify, render_template, url_for, redirect, request
from application import app
from forms import CreateForm, JoinForm
from database import start_game



# ------------------------------------
# Маршруты
# ------------------------------------
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


# ------------------------------------
# Тестовые маршруты
# ------------------------------------
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

# маршруты, для проверки работы с xhr запросами
@app.route("/state")
def state():
    result = random.choice(['map', 'champ', 'result'])
    response = {'result': result}
    return jsonify(response)

@app.route("/test")
def test():
    return render_template('hello.html')


# ------------------------------------
# Запуск приложения
# ------------------------------------
if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)