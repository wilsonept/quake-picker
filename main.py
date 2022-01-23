from flask import render_template, url_for, redirect
from application import app
from forms import CreateForm, JoinForm



# ------------------------------------
# Маршруты
# ------------------------------------
@app.route("/")
def home():
    return render_template('hello.html')


@app.route("/create", methods=['GET', 'POST'])
def create():
    ''' Форма создания комнаты '''
    form = CreateForm()
    if form.validate_on_submit():

        ''' TODO блок обработки удачного создания комнаты
        на этом этапе необходимо создать комнату в базе и
        получить id комнаты для передачи его в redirect
        '''
        # TODO Проверка наличия пользователя, если нет то создать пользователя
        # TODO Создать комнату и привязать пользователя
        # TODO Создать результат

        room_id = 123434244142342
        return redirect(url_for('room', room_id=room_id))
    return render_template('create_form.html', form=form, errors=form.errors)


@app.route("/<room_id>/join", methods=['GET', 'POST'])
def join(room_id):
    ''' Форма подключения к комнате '''
    form = JoinForm()
    if form.validate_on_submit():

        # TODO проверка существования комнаты

        return redirect(url_for('room', room_id=room_id))
    else:
        return render_template('join_form.html', form=form, errors=form.errors, room_id=room_id)


@app.route("/<room_id>/room", methods=['GET', 'POST'])
def room(room_id):
    ''' Основная страница выбора, она же комната '''
    return render_template('results.html', room_id=room_id)


@app.route("/<room_id>/results")
def results(room_id):
    ''' Страница результатов выбора '''
    return render_template('room.html', room_id=room_id)



# ------------------------------------
# Запуск приложения
# ------------------------------------
if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)