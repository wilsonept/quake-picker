#from flask_sqlalchemy.ext.declarative import declarative_base
from email.policy import default
from application import db
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import text as sa_text



class Users(db.Model):
    id = db.Column(db.Integer, nullable=False, unique=True, primary_key=True, autoincrement=True)
    nickname = db.Column(db.String(40), nullable=False)
    is_persistent = db.Column(db.Boolean, nullable=False, default=False)
    rel_results = db.relationship("Results", back_populates="rel_users")

class Actions(db.Model):
    id = db.Column(db.Integer, nullable=False, unique=True, primary_key=True, autoincrement=True)
    name = db.Column(db.String(30), nullable=False)
    rel_rooms = db.relationship("Rooms", back_populates="rel_actions")

class Bo_types(db.Model):
    id = db.Column(db.Integer, nullable=False, unique=True, primary_key=True, autoincrement=True)
    name = db.Column(db.String(40), nullable=False)
    rel_rooms = db.relationship("Rooms", back_populates="rel_bo_types")

class Current_season(db.Model):
    id = db.Column(db.Integer, nullable=False, unique=True, primary_key=True, autoincrement=True)
    object_id = db.Column(db.Integer,db.ForeignKey('objects.id'), nullable=False)
    rel_objects = db.relationship("Objects", back_populates="rel_current_season")

class Game_modes(db.Model):
    id = db.Column(db.Integer, nullable=False, unique=True, primary_key=True, autoincrement=True)
    name = db.Column(db.String(40), nullable=False)
    rel_rooms = db.relationship("Rooms", back_populates="rel_game_modes")

class Match_types(db.Model):
    id = db.Column(db.Integer, nullable=False, unique=True, primary_key=True, autoincrement=True)
    name = db.Column(db.String(40), nullable=False)

class Object_types(db.Model):
    id = db.Column(db.Integer, nullable=False, unique=True, primary_key=True, autoincrement=True)
    name = db.Column(db.String(40), nullable=False)
    rel_objects = db.relationship("Objects", back_populates="rel_object_types")

class Objects(db.Model):
    id = db.Column(db.Integer, nullable=False, unique=True, primary_key=True, autoincrement=True)
    type = db.Column(db.Integer,db.ForeignKey('object_types.id'), nullable=False)
    name = db.Column(db.String(40), nullable=False)
    shortname = db.Column(db.String(10), nullable=False)
    img_url = db.Column(db.String(300), nullable=False)
    rel_current_season = db.relationship("Current_season", back_populates="rel_objects")
    rel_object_types = db.relationship("Object_types", back_populates="rel_objects")

class Results(db.Model):
    id = db.Column(db.Integer, nullable=False, unique=True, primary_key=True, autoincrement=True)
    room_id = db.Column(db.Integer,db.ForeignKey('rooms.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    picks = db.Column(db.String, nullable=True)
    bans = db.Column(db.String, nullable=True)
    team_id = db.Column(db.Integer,db.ForeignKey('teams.id'), nullable=False)
    rel_users = db.relationship("Users", back_populates="rel_results")
    rel_rooms = db.relationship("Rooms", back_populates="rel_results")
    rel_teams = db.relationship("Teams", back_populates="rel_results")


class Rooms(db.Model):
    id = db.Column(db.Integer, nullable=False, unique=True, primary_key=True, autoincrement=True)
    #????#
    room_uuid = db.Column(UUID(as_uuid=True),nullable=True, server_default=sa_text("uuid_generate_v4()")) 
    game_mode_id = db.Column(db.Integer,db.ForeignKey('game_modes.id'), nullable=False)
    bo_type_id = db.Column(db.Integer,db.ForeignKey('bo_types.id'), nullable=False)
    seed = db.Column(db.Integer, nullable=False)
    current_action_id = db.Column(db.Integer, db.ForeignKey('actions.id') ,nullable=False, default = 4)
    rel_results = db.relationship("Results", back_populates="rel_rooms")
    rel_game_modes = db.relationship("Game_modes", back_populates="rel_rooms")
    rel_bo_types = db.relationship("Bo_types", back_populates="rel_rooms")
    rel_actions = db.relationship("Actions", back_populates="rel_rooms")


class Teams(db.Model):
    id = db.Column(db.Integer, nullable=False, unique=True, primary_key=True, autoincrement=True)
    name = db.Column(db.String(40), nullable=False)
    rel_results = db.relationship("Results", back_populates="rel_teams")

#req = engine.execute("select * from users")
#for r in req:
#    print(r)

def create_req(post_nickname,post_game_mode,post_bo_type,post_seed):
    #users_list = Objects.query.all()
    #for r in users_list:
    #    print(r.rel_current_season)
    ex_user = bool(Users.query.filter_by(nickname=post_nickname).first())

    if ex_user == False:
        new_user = Users(
            nickname = post_nickname
        )
        db.session.add(new_user)
        db.session.commit()
    new_room = Rooms(
        game_mode_id = post_game_mode,
        bo_type_id = post_bo_type,
        seed = post_seed
    )
    db.session.add(new_room)
    db.session.commit()

create_req("Pipiskin",1,1,1)


