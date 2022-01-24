#from flask_sqlalchemy.ext.declarative import declarative_base
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




# NOTE на данную функцию имеется unittest.
def create_room(nickname, game_mode, bo_type, seed):
    ''' Создает пользователя если необходимо, создает комнату
    и результат для пользователя создавшего комнату'''
    # Проверяем пользователя в базе
    user_exist = bool(Users.query.filter_by(nickname=nickname).first())

    if user_exist == False:
        # Создаем пользователя
        new_user = Users(nickname=nickname)
        db.session.add(new_user)

    # Создаем комнату
    new_room = Rooms(
        game_mode_id = game_mode,
        bo_type_id = bo_type,
        seed = seed
    )
    db.session.add(new_room)
    db.session.commit()
    
    # Создаем результат
    new_results = Results(
        room_id = new_room.id,
        user_id = new_user.id,
        team_id = seed + 1 # id команд начинаются с 1, а seed с нуля. Поэтому нужно инкрементировать.
    )

    db.session.add(new_results)
    db.session.commit()

    # возвращаем id'шники созданных вхождений
    operation_result = {
        "room_id": new_room.id,
        "user_id": new_user.id,
        "results_id": new_results.id
    }
    #redirect_url =  f'/{new_room.room_uuid}/{new_user.nickname}'
    room_uuid = new_room.room_uuid

    return operation_result , room_uuid

def join_room(post_nickname, post_room_uuid):
    # Проверка на существование комнаты
    room_exist = bool(Rooms.query.filter_by(room_uuid=post_room_uuid).first())
    
    if room_exist == False:
        
        # TODO Пользователю нужно вернуть страницу с инфой о том что такой румы нет
        return True
    
    # Проверяем пользователя в базе
    user_exist = bool(Users.query.filter_by(nickname=post_nickname).first())

    if user_exist == False:
    # Создаем пользователя
        new_user = Users(nickname=post_nickname)
        db.session.add(new_user)
        db.session.commit()

    # Создаем результат
    # TODO проверить зовется ли room.id через room
    room = Rooms.query.filter_by(room_uuid=post_room_uuid).first()
    new_results = Results(
        room_id = room.id,
        user_id = new_user.id,
        # TODO нужна логика определения сида для остальных участников
        #team_id = seed + 1 # id команд начинаются с 1, а seed с нуля. Поэтому нужно инкрементировать.
    )

    db.session.add(new_results)
    db.session.commit()


# NOTE на данную функцию имеется unittest.
def delete_room(room_id, user_id, results_id):
    ''' Удаляет пользователя, комнату и результат по заданным id таблиц'''
    # получаем вхождения который надо удалить
    entries_to_delete = [
        Rooms.query.filter_by(id=room_id).first(),
        Users.query.filter_by(id=user_id).first(),
        Results.query.filter_by(id=results_id).first(),
    ]
    # удаляем
    for entry in entries_to_delete:
        try:
            db.session.delete(entry)
        except:
            return False

    db.session.commit()
    return True