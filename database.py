
#from flask_sqlalchemy.ext.declarative import declarative_base
from flask_sqlalchemy import SQLAlchemy
from application import db
from json_reader import load_json


class Users(db.Model):
    id = db.Column(db.Integer, nullable=False, unique=True, primary_key=True, autoincrement=True)
    nickname = db.Column(db.String(40), nullable=False)
    is_persistent = db.Column(db.Boolean, nullable=False)


#req = engine.execute("select * from users")
#for r in req:
#    print(r)

users_list = Users.query.all()
for r in users_list:
    print(r.id,r.nickname,r.is_persistent)
