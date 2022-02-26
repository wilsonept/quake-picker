from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jsonrpc import JSONRPC

from helpers import load_json

'''
Файл конфигурации Flask приложения
'''



# ------------------------------------
# Создание и конфигурация приложения
# ------------------------------------
def create_app():
    global _DB
    global _JSONRPC

    conf = load_json('config.json')
    
    app = Flask(__name__)
    app.config["SECRET_KEY"]=conf['app_secret']
    
    # Подключение БД
    engine = (f'postgresql://{conf["user"]}:{conf["password"]}@{conf["host"]}'
              f':{conf["port"]}/{conf["db_name"]}')
    app.config['SQLALCHEMY_DATABASE_URI'] = engine
    # отключаем FSADeprecationWarning при старте приложения.
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    _DB = SQLAlchemy(app)

    # Инициализируем RPC
    _JSONRPC = JSONRPC(app, '/api', enable_web_browsable_api=True)
    return app

app = create_app()
