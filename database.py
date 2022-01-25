#from flask_sqlalchemy.ext.declarative import declarative_base
from random import choice
from application import db
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import text as sa_text


# ------------------------------------
# Модели
# ------------------------------------
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
    player_count = db.Column(db.Integer, nullable=False, unique=False)

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


# ------------------------------------
# Функции основные
# ------------------------------------
def create_user(nickname) -> int:
    '''Создает пользователя в таблице users если необходимо и
    возвращает id пользователя.'''
    # Проверяем пользователя в базе
    user_exist = bool(Users.query.filter_by(nickname=nickname).first())

    if user_exist == False:
        # Создаем пользователя
        new_user = Users(nickname=nickname)
        db.session.add(new_user)
        ''' TODO добавить обработку ошибок на случай:
            * если запрос не дошел до базы
            * если ответ не пришел от базы'''
        db.session.commit(new_user)
    else:
        new_user = Users.query.filter_by(nickname=nickname).first()

    return new_user.id


def create_room(game_mode, bo_type, seed) -> dict:
    '''Создает комнату в таблице rooms и возвращает
    словарь содержащий id и uuid комнаты.'''
    # TODO объединить в одну функцию
    # assign_team
    if seed > 2 and seed < 1:
        seed = choice([1,2])
    else: 
        seed = seed
        
    new_room = Rooms(
        game_mode_id = game_mode,
        bo_type_id = bo_type,
        # TODO Сделать так что бы seed в таблице могло принимать значения
        # только 1, 2. Где 1 это синяие, 2 это красные.
        seed = seed
    )
    db.session.add(new_room)
    ''' TODO добавить обработку ошибок на случай:
       * если запрос не дошел до базы
       * если ответ не пришел от базы'''
    db.session.commit()
    return {'id': new_room.id, 'uuid': new_room.uuid}


# TODO Функция создания результата
def create_result(new_user_id, new_room_id, seed) -> int:
    '''Создает результат в таблице results и
    возвращает id результата.'''
    # TODO Проверяем заполнена ли комната
    # в случае если комната заполнена, выбрасываем exception, хз какой правда.

    new_results = Results(
        room_id = new_room_id,
        user_id = new_user_id,
        # TODO Сделать так что бы seed в таблице могло принимать значения
        # только 1, 2. Где 1 это синяие, 2 это красные.
        team_id = seed
    )

    db.session.add(new_results)
    ''' TODO добавить обработку ошибок на случай:
       * если запрос не дошел до базы
       * если ответ не пришел от базы'''
    db.session.commit()
    return new_results.id

def start_game(nickname, game_mode, bo_type, seed) -> dict:
    ''' Создает пользователя если необходимо, создает комнату и результат
    для пользователя создавшего комнату. Возвращает словарь основных
    параметров игры для передачи его фронту.'''
    new_user_id = create_user(nickname)
    new_room = create_room(game_mode, bo_type, seed)
    new_result_id = create_result(new_user_id, new_room['id'], seed)
    game_params = {
        'nickname': nickname,
        'user_id': new_user_id,
        'room_uuid': new_room['uuid'],
        'game_mode': game_mode,
        'bo_type': bo_type,
        # TODO Сделать так что бы seed в таблице могло принимать значения
        # только 1, 2. Где 1 это синяие, 2 это красные.
        'seed': seed,
        'result_id': new_result_id
    }
    return game_params

def join_room(post_nickname, post_room_uuid) -> dict:
    '''Создает пользователя если необходимо, проверяет существование комнаты
    создает результат для подключающегося пользователя. Возвращает словарь
    основных параметров игры для передачи его фронту.'''
    # Проверка на существование комнаты
    room_exist = bool(Rooms.query.filter_by(room_uuid=post_room_uuid).first())

    if room_exist == False:
        # TODO бросаем exception, хз какой правда.
        pass

    new_user_id = create_user(nickname=post_nickname)
    # Получаем id комнаты по uuid
    room = Rooms.query.filter_by(room_uuid=post_room_uuid).first()
    # TODO объединить в одну функцию
    # assign_team
    if room.seed == 1:
        team_id = 2
    elif room.seed == 2:
        team_id = 1
    else:
        # TODO бросаем exception, получены не верные данные из бд.
        pass

    new_result_id = create_result(new_user_id, room.id, team_id)
    game_params = {
        'nickname': post_nickname,
        'user_id': new_user_id,
        # TODO Сделать так что бы seed в таблице могло принимать значения
        # только 1, 2. Где 1 это синие, 2 это красные.
        'seed': team_id,
        'result_id': new_result_id
    }
    return game_params


# ------------------------------------
# Функции вспомогательные
# ------------------------------------
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

#req = engine.execute("select * from users")
#for r in req:
#    print(r)
