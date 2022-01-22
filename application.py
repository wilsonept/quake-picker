from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from json_reader import load_json

app = Flask(__name__)

conf = load_json('config.json')
engine = 'postgresql://'+conf["user"]+':'+conf["password"]+'@'+conf["host"]+':'+conf["port"]+'/'+conf["db_name"]
app.config['SQLALCHEMY_DATABASE_URI'] = engine
db = SQLAlchemy(app)