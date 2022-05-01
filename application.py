import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jsonrpc import JSONRPC
from flask_sock import Sock

from utils import load_json

"""
# Файл конфигурации Flask приложения.
Для работы файла необходим `config.json` в корневой директории.
Приложение поддерживает работу с двумя типами баз данных:
    - `SQLite`: используется для разработки.
    - `PostgreSQL`: используется для прода.

`config.json` должен быть для каждой БД в своем формате.

## PostgreSQL (prod)
```json
{
    "host": "<database ip address>",
    "port": "<database port>",
    "user": "<database admin>",
    "password": "<database password>",
    "db_name": "quakepicker",
    "app_secret": "<random string as secret key>",
    "db_engine": "postgresql"
} 
```
Вопросы развертывания описаны в документации:
https://app.gitbook.com/s/qg0Ltf53I35tt60xYYEl/app-deployment-prod

## SQLite (dev):
```json
{
    "host": "<database ip address>",
    "port": "<database port>",
    "user": "<database admin>",
    "password": "<database password>",
    "db_name": "quakepicker",
    "app_secret": "<random string as secret key>",
    "db_engine": "postgresql"
} 
```
Вопросы развертывания описаны в документации:
https://app.gitbook.com/s/qg0Ltf53I35tt60xYYEl/app-deployment-dev
"""

# ------ Создание и конфигурация приложения ----------------------------

conf = load_json("config.json")

def create_app(conf):
    """Создает и настраивает объект приложения."""
    global _DB
    global _JSONRPC
    global _SOCK

    app = Flask(__name__)
    app.config["SECRET_KEY"]=conf["app_secret"]
    
    # Подключение БД
    if conf["db_engine"] == "postgresql":
        engine = (f"postgresql://{conf['user']}:{conf['password']}@"
                  f"{conf['host']}:{conf['port']}/{conf['db_name']}")
        # отключаем FSADeprecationWarning при старте приложения.
        app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    elif conf["db_engine"] == "sqlite":
        db_file_path = os.path.join(conf["db_folder_path"],
                                    f"{conf['db_name']}.db")
        engine = f"sqlite:///{db_file_path}"
        app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    else:
        Exception("Не верное значение для db_engine в файле конфигурации")

    app.config["SQLALCHEMY_DATABASE_URI"] = engine
    _DB = SQLAlchemy(app)

    # Инициализируем RPC
    _JSONRPC = JSONRPC(app, "/api", enable_web_browsable_api=True)

    # Инициализируем websocket
    _SOCK = Sock(app)
    return app

app = create_app(conf)


if __name__ == "__main__":
    print("URI подключения:", app.config["SQLALCHEMY_DATABASE_URI"])