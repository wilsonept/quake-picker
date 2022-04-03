import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jsonrpc import JSONRPC
from flask_sock import Sock

from utils import load_json

'''
Файл конфигурации Flask приложения.
'''



# ------------------------------------
# Создание и конфигурация приложения
# ------------------------------------
conf = load_json('config.json')

def create_app(conf):
    global _DB
    global _JSONRPC
    global _SOCK

    
    app = Flask(__name__)
    app.config["SECRET_KEY"]=conf['app_secret']
    
    # Подключение БД
    if conf["db_engine"] == "postgresql":
        engine = (f'postgresql://{conf["user"]}:{conf["password"]}@'
                  f'{conf["host"]}:{conf["port"]}/{conf["db_name"]}')
        # отключаем FSADeprecationWarning при старте приложения.
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    elif conf["db_engine"] == "sqlite":
        db_file_path = os.path.join(conf["db_folder_path"],
                                    f'{conf["db_name"]}.db')
        engine = f'sqlite:///{db_file_path}'
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    else:
        Exception('Не верное значение для db_engine в файле конфигурации')

    app.config['SQLALCHEMY_DATABASE_URI'] = engine
    _DB = SQLAlchemy(app)

    # Инициализируем RPC
    _JSONRPC = JSONRPC(app, '/api', enable_web_browsable_api=True)

    # Инициализируем websocket
    _SOCK = Sock(app)
    return app

app = create_app(conf)


if __name__ == '__main__':
    print('URI подключения:', app.config['SQLALCHEMY_DATABASE_URI'])