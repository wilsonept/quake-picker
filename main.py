from flask import Flask, render_template, url_for, redirect
from forms import CreateForm, JoinForm

# ------------------------------------
# Создание и конфигурация приложения
# ------------------------------------
def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"]='F02D4A61CAB5C858641A91F41DBF3CE8759D9F52394239C1AEB81651BB86BCAE'
    return app

app = create_app()






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

        ''' блок обработки удачного создания комнаты
        на этом этапе необходимо создать комнату в базе и
        получить id комнаты для передачи его в redirect
        '''
        room_id = 123434244142342
        return redirect(url_for('room', room_id=room_id))
    return render_template('create_form.html', form=form, errors=form.errors)

@app.route("/<room_id>/join", methods=['GET', 'POST'])
def join(room_id):
    ''' Форма подключения к комнате '''
    form = JoinForm()
    if form.validate_on_submit():
        return redirect(url_for('room.html', room_id=room_id))
    else:
        return render_template('join_form.html', form=form, errors=form.errors)

@app.route("/<room_id>/room", methods=['GET', 'POST'])
def room(room_id):
    ''' Основная страница выбора, она же комната '''
    return render_template('room.html', room_id=room_id)

@app.route("/<room_id>/results")
def results(room_id):
    ''' Страница результатов выбора '''
    return render_template('room.html', room_id=room_id)


# ------------------------------------
# Запуск приложения
# ------------------------------------
if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)