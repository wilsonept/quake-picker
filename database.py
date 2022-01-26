from random import choice
from application import db
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import text as sa_text
from exceptions import RoomDoesNotExist

# TODO Привести в порядок свойства отношений моделей. Что бы названия
# соответствовали типам связей между таблицами.

# ------------------------------------
# Модели
# ------------------------------------
class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, nullable=False, unique=True, primary_key=True, autoincrement=True)
    nickname = db.Column(db.String(40), nullable=False)
    is_persistent = db.Column(db.Boolean, nullable=False, default=False)

    rel_results = db.relationship("Result", back_populates="rel_users")

    @classmethod
    def get_user(cls, nickname):
        '''Ищет пользователя в таблице по имени'''
        try:
            requested_user = cls.query.filter_by(nickname=nickname).first()
            db.session.commit()
        except:
            # отменяем транзакцию в случае ошибки.
            db.session.rollback()
            raise
        return requested_user

    @classmethod
    def create_user(cls, nickname) -> int:
        '''Создает пользователя в таблице если необходимо и
    возвращает id пользователя.'''
        # Проверяем пользователя в базе
        user_exist = bool(cls.get_user(nickname))

        if user_exist == False:
            # Создаем пользователя
            new_user = cls(nickname=nickname)
            try:
                db.session.add(new_user)
                db.session.commit()
            except:
                # отменяем транзакцию в случае ошибки.
                db.session.rollback()
                raise
        else:
            new_user = User.query.filter_by(nickname=nickname).first()

        return new_user.id


class Room(db.Model):
    __tablename__ = 'rooms'

    id = db.Column(db.Integer, nullable=False, unique=True, primary_key=True, autoincrement=True)
    #????#
    room_uuid = db.Column(UUID(as_uuid=True),nullable=True, server_default=sa_text("uuid_generate_v4()")) 
    game_mode_id = db.Column(db.Integer,db.ForeignKey('game_modes.id'), nullable=False)
    bo_type_id = db.Column(db.Integer,db.ForeignKey('bo_types.id'), nullable=False)
    seed = db.Column(db.Integer, nullable=False)
    current_action_id = db.Column(db.Integer, db.ForeignKey('actions.id') ,nullable=False, default = 4)

    rel_results = db.relationship("Result", back_populates="rel_rooms")
    rel_game_modes = db.relationship("Game_mode", back_populates="rel_rooms")
    rel_bo_types = db.relationship("Bo_type", back_populates="rel_rooms")
    rel_actions = db.relationship("Action", back_populates="rel_rooms")

    @classmethod
    def get_room(cls, room_uuid):
        '''Ищет комнату в таблице по uuid'''
        try:
            requested_room = cls.query.filter_by(room_uuid=room_uuid).first()
            db.session.commit()
        except:
            # отменяем транзакцию в случае ошибки.
            db.session.rollback()
            raise
        return requested_room

    @classmethod
    def create_room(cls, game_mode, bo_type, seed) -> dict:
        '''Создает комнату в таблице rooms и возвращает
        словарь содержащий id и uuid комнаты.'''
        # проверяем seed, если он больше или меньше 1 или 2 то выбрать
        # рандомного игрока.
        if seed > 2 and seed < 1:
            seed = choice([1,2])
        else: 
            seed = seed

        new_room = cls(
            game_mode_id = game_mode,
            bo_type_id = bo_type,
            # TODO Сделать так что бы seed в таблице могло принимать значения
            # только 1, 2. Где 1 это синяие, 2 это красные.
            seed = seed
        )
        try:
            db.session.add(new_room)
            db.session.commit()
        except:
            # отменяем транзакцию в случае ошибки.
            db.session.rollback()
            raise
        return {'id': new_room.id, 'uuid': new_room.uuid}

    @classmethod
    def delete_room(cls, room_uuid):
        room_to_delete = cls.get_room(room_uuid)
        try:
            db.session.delete(room_to_delete)
            db.session.commit()
        except:
            db.session.rollback()
            raise
        return True


class Result(db.Model):
    __tablename__ = 'results'

    id = db.Column(db.Integer, nullable=False, unique=True, primary_key=True, autoincrement=True)
    room_id = db.Column(db.Integer,db.ForeignKey('rooms.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    picks = db.Column(db.String, nullable=True)
    bans = db.Column(db.String, nullable=True)
    team_id = db.Column(db.Integer,db.ForeignKey('teams.id'), nullable=False)

    rel_users = db.relationship("User", back_populates="rel_results")
    rel_rooms = db.relationship("Room", back_populates="rel_results")
    rel_teams = db.relationship("Team", back_populates="rel_results")

    @classmethod
    def get_result(cls, room_id):
        '''Ищет результаты по id комнаты'''
        try:
            requested_result = cls.query.filter_by(room_id=room_id).all()
            db.session.commit()
        except:
            # отменяем транзакцию в случае ошибки.
            db.session.rollback()
            raise
        return requested_result

    @classmethod
    def create_result(cls, new_user_id, new_room_id, seed) -> int:
        '''Создает результат в таблице results и
        возвращает id результата.'''
        # TODO Проверяем заполнена ли комната
        # в случае если комната заполнена, выбрасываем exception, хз какой правда.

        new_results = cls(
            room_id = new_room_id,
            user_id = new_user_id,
            # TODO Сделать так что бы seed в таблице могло принимать значения
            # только 1, 2. Где 1 это синяие, 2 это красные.
            team_id = seed
        )
        try:
            db.session.add(new_results)
            db.session.commit()
        except:
            # отменяем транзакцию в случае ошибки.
            db.session.rollback()
            raise
        return new_results.id


class Action(db.Model):
    __tablename__ = 'actions'
    id = db.Column(db.Integer, nullable=False, unique=True, primary_key=True, autoincrement=True)
    name = db.Column(db.String(30), nullable=False)

    rel_rooms = db.relationship("Room", back_populates="rel_actions")


class Bo_type(db.Model):
    __tablename__ = 'bo_types'
    
    id = db.Column(db.Integer, nullable=False, unique=True, primary_key=True, autoincrement=True)
    name = db.Column(db.String(40), nullable=False)

    rel_rooms = db.relationship("Room", back_populates="rel_bo_types")


class Current_season(db.Model):
    __tablename__ = 'current_season'

    id = db.Column(db.Integer, nullable=False, unique=True, primary_key=True, autoincrement=True)
    object_id = db.Column(db.Integer,db.ForeignKey('objects.id'), nullable=False)

    rel_objects = db.relationship("Object", back_populates="rel_current_season")


class Game_mode(db.Model):
    __tablename__ = 'game_modes'

    id = db.Column(db.Integer, nullable=False, unique=True, primary_key=True, autoincrement=True)
    name = db.Column(db.String(40), nullable=False)
    player_count = db.Column(db.Integer, nullable=False, unique=False)

    rel_rooms = db.relationship("Room", back_populates="rel_game_modes")


class Match_type(db.Model):
    __tablename__ = 'match_types'

    id = db.Column(db.Integer, nullable=False, unique=True, primary_key=True, autoincrement=True)
    name = db.Column(db.String(40), nullable=False)

class Object_type(db.Model):
    __tablename__ = 'object_types'

    id = db.Column(db.Integer, nullable=False, unique=True, primary_key=True, autoincrement=True)
    name = db.Column(db.String(40), nullable=False)

    rel_objects = db.relationship("Object", back_populates="rel_object_types")


class Object(db.Model):
    __tablename__ = 'objects'

    id = db.Column(db.Integer, nullable=False, unique=True, primary_key=True, autoincrement=True)
    type = db.Column(db.Integer,db.ForeignKey('object_types.id'), nullable=False)
    name = db.Column(db.String(40), nullable=False)
    shortname = db.Column(db.String(10), nullable=False)
    img_url = db.Column(db.String(300), nullable=False)

    rel_current_season = db.relationship("Current_season", back_populates="rel_objects")
    rel_object_types = db.relationship("Object_type", back_populates="rel_objects")


class Team(db.Model):
    __tablename__ = 'teams'

    id = db.Column(db.Integer, nullable=False, unique=True, primary_key=True, autoincrement=True)
    name = db.Column(db.String(40), nullable=False)

    rel_results = db.relationship("Result", back_populates="rel_teams")


# ------------------------------------
# Функции основные
# ------------------------------------
def start_game(nickname, game_mode, bo_type, seed) -> dict:
    ''' Создает пользователя если необходимо, создает комнату и результат
    для пользователя создавшего комнату. Возвращает словарь основных
    параметров игры для передачи его фронту.'''
    new_user_id = User.create_user(nickname)
    new_room = Room.create_room(game_mode, bo_type, seed)
    new_result_id = Result.create_result(new_user_id, new_room['id'], seed)
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
    room_exist = bool(Room.query.filter_by(room_uuid=post_room_uuid).first())

    if room_exist == False:
        raise RoomDoesNotExist('This room does not exist in database')

    new_user_id = User.create_user(nickname=post_nickname)
    # Получаем id комнаты по uuid
    room = Room.query.filter_by(room_uuid=post_room_uuid).first()
    # TODO объединить в одну функцию
    # assign_team
    if room.seed == 1:
        team_id = 2
    elif room.seed == 2:
        team_id = 1
    else:
        # TODO бросаем exception, получены не верные данные из бд.
        pass

    new_result_id = Result.create_result(new_user_id, room.id, team_id)
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
def delete_room(room_uuid):
    '''Удаляет комнату и результат по заданным room_uuid'''
    # получаем вхождения которые надо удалить
    room = Room.get_room(room_uuid=room_uuid)
    if not room:
        print('Nothing to delete')
        return True
    elif room.rel_results:
        for result in room.rel_results:
            try:
                db.session.delete(result)
                db.session.commit()
            except:
                db.session.rollback()
                raise
    
    room.delete_room(room_uuid=room_uuid)
    return True

#req = engine.execute("select * from users")
#for r in req:
#    print(r)

# user = User.get_user('wilson')
# room = Room.get_room('dc3ad9c1-7452-40b6-99a1-e98ddc18a31e')
# result = Result.get_result(1)
# pass
