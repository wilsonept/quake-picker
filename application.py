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
    "app_host": "<application ip>",
    "app_port": "<application port>",
    "app_secret": "<random string as secret key>",

    "db_host": "<database ip address>",
    "db_port": "<database port>",
    "db_user": "<database admin>",
    "db_password": "<database password>",
    "db_name": "quakepicker",
    "db_engine": "postgresql"
} 
```
Вопросы развертывания описаны в документации:
https://app.gitbook.com/s/qg0Ltf53I35tt60xYYEl/app-deployment-prod

## SQLite (dev):
```json
{
    "app_host": "<application ip>",
    "app_port": "<application port>",
    "app_secret": "<random string as secret key>",
    
    "db_name": "quakepicker",
    "db_engine": "sqlite",
    "db_folder_path": "./"  
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
    
    # Подключение БД.
    if conf["db_engine"] == "postgresql":
        engine = (f"postgresql://{conf['db_user']}:{conf['db_password']}@"
                  f"{conf['db_host']}:{conf['db_port']}/{conf['db_name']}")
        # Отключаем FSADeprecationWarning при старте приложения.
        app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    elif conf["db_engine"] == "sqlite":
        db_file_path = os.path.join(conf["db_folder_path"],
                                    f"{conf['db_name']}.db")
        engine = f"sqlite:///{db_file_path}"
        app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    else:
        Exception("Не верное значение для db_engine в файле конфигурации.")

    app.config["SQLALCHEMY_DATABASE_URI"] = engine
    _DB = SQLAlchemy(app)

    # Инициализируем RPC.
    _JSONRPC = JSONRPC(app, "/api", enable_web_browsable_api=True)

    # Инициализируем websocket.
    _SOCK = Sock(app)
    return app

app = create_app(conf)


if __name__ == "__main__":
    print("[ DEBUG ] URI подключения:",
        app.config["SQLALCHEMY_DATABASE_URI"])
