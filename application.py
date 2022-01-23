from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from json_reader import load_json

# ------------------------------------
# Создание и конфигурация приложения
# ------------------------------------
def create_app():
    global db

    app = Flask(__name__)
    app.config["SECRET_KEY"]='F02D4A61CAB5C858641A91F41DBF3CE8759D9F52394239C1AEB81651BB86BCAE'
    
    # Подключение БД
    conf = load_json('config.json')
    engine = f'postgresql://{{ conf["user"] }}:{{ conf["password"] }}@{{ conf["host"] }}:{{ conf["port"] }}/{{ conf["db_name"] }}'
    app.config['SQLALCHEMY_DATABASE_URI'] = engine
    db = SQLAlchemy(app)
    return app

app = create_app()