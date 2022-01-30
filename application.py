from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jsonrpc import JSONRPC

from helpers import load_json

# ------------------------------------
# Создание и конфигурация приложения
# ------------------------------------
def create_app():
    global _DB
    global _JSONRPC

    app = Flask(__name__)
    app.config["SECRET_KEY"]='F02D4A61CAB5C858641A91F41DBF3CE8759D9F52394239C1AEB81651BB86BCAE'
    
    # Подключение БД
    conf = load_json('config.json')
    engine = f'postgresql://{ conf["user"] }:{ conf["password"] }@{ conf["host"] }:{ conf["port"] }/{ conf["db_name"] }'
    app.config['SQLALCHEMY_DATABASE_URI'] = engine
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False # отключает FSADeprecationWarning при старте приложения.
    _DB = SQLAlchemy(app)

    # Инициализируем RPC
    _JSONRPC = JSONRPC(app, '/api', enable_web_browsable_api=True)
    return app

app = create_app()
