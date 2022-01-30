import random

from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import text as sa_text

from exceptions import RoomDoesNotExist
from application import _DB as db


# TODO Переименовать этот файл в Models.py. Чисто в целях стандартизации.
# Так как в большинстве просмотренных видео, этот файл назвают именно так.

# TODO Привести в порядок свойства отношений моделей. Что бы названия
# соответствовали типам связей между таблицами.




# ------ Модели ---------------------------------------------------------------

class User(db.Model):
    '''Таблица пользователей.'''
    __tablename__ = 'users'

    id = db.Column(db.Integer, nullable=False, unique=True, primary_key=True, autoincrement=True)
    nickname = db.Column(db.String(40), nullable=False)
    is_persistent = db.Column(db.Boolean, nullable=False, default=False)

    rel_results = db.relationship("Result", back_populates="rel_users")
    rel_rooms = db.relationship("Room", back_populates="rel_users")

    @classmethod
    def get_user(cls, nickname):
        '''Поиск пользователя по имени, возвращает объект класса User.'''
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
        '''Создает пользователя в таблице если необходимо и возвращает
        id пользователя.'''
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
    '''Таблица комнат'''
    __tablename__ = 'rooms'

    id = db.Column(db.Integer, nullable=False, unique=True, primary_key=True, autoincrement=True)
    room_uuid = db.Column(UUID(as_uuid=True),nullable=True, server_default=sa_text("uuid_generate_v4()")) 
    bo_type_id = db.Column(db.Integer,db.ForeignKey('bo_types.id'), nullable=False)
    game_mode_id = db.Column(db.Integer,db.ForeignKey('game_modes.id'), nullable=False)
    current_user_id = db.Column(db.Integer, db.ForeignKey('users.id') ,nullable=False, default = 4)
    current_action_id = db.Column(db.Integer, db.ForeignKey('actions.id') ,nullable=False, default = 4)

    # Указывает какой игрок начинает игру, выбирается через форму создания комнаты
    seed = db.Column(db.Integer, nullable=False)

    rel_results = db.relationship("Result", back_populates="rel_rooms")
    rel_game_modes = db.relationship("Game_mode", back_populates="rel_rooms")
    rel_bo_types = db.relationship("Bo_type", back_populates="rel_rooms")
    rel_actions = db.relationship("Action", back_populates="rel_rooms")
    rel_users = db.relationship("User", back_populates="rel_rooms")

    @classmethod
    def get_room(cls, room_uuid):
        '''Ищет комнату в таблице по uuid.'''
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

        # создаем комнату
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
    def init_current_user(cls):
        '''Обновляет запись активного игрока в комнате.'''
        if cls.seed == 0:
            team = 1
        elif cls.seed == 1:
            team = 2
        else:
            team = random.choice([1,2])

        try:
            for result in cls.rel_results:
                '''NOTE Будет работать только с двумя Тимами!!!'''
                if result.team_id == team:
                    cls.current_user_id = result.user_id
                    db.session.commit()
        except:
            # отменяем транзакцию в случае ошибки.
            db.session.rollback()
            raise

    @classmethod
    def delete_room(cls):
        '''Удаляет комнату текущего класса.'''
        room_to_delete = cls.room_uuid
        try:
            db.session.delete(room_to_delete)
            db.session.commit()
        except:
            db.session.rollback()
            raise
        return True


class Result(db.Model):
    '''Таблица результатов.'''
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
    def get_result(cls, room_id, **kwargs):
        '''Ищет результаты игроков по id комнаты, так же принимает **kwargs
        для дополнительной фильтрации'''
        try:
            requested_result = cls.query.filter_by(room_id=room_id, **kwargs).all()
            db.session.commit()
        except:
            # отменяем транзакцию в случае ошибки.
            db.session.rollback()
            raise
        return requested_result

    @classmethod
    def create_result(cls, new_user_id, new_room_id, team_id) -> int:
        '''Создает результат в таблице results и
        возвращает id результата.'''
        # TODO Проверяем заполнена ли комната
        # в случае если комната заполнена, выбрасываем exception, хз какой правда.

        new_results = cls(
            room_id = new_room_id,
            user_id = new_user_id,
            # TODO Сделать так что бы seed в таблице могло принимать значения
            # только 1, 2. Где 1 это синяие, 2 это красные.
            team_id = team_id
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
    '''Таблица действий. Ban, pick, wait, end. Wait необходим для того
    что бы сказать фронту что нужно подождать второго игрока. End для того
    что бы закончить игру и вывести результат'''
    __tablename__ = 'actions'

    id = db.Column(db.Integer, nullable=False, unique=True, primary_key=True, autoincrement=True)
    name = db.Column(db.String(30), nullable=False)

    rel_rooms = db.relationship("Room", back_populates="rel_actions")


class Bo_type(db.Model):
    '''Таблица типов игр по колическу карт в матче.
    Содержит bo1, bo3, bo5, bo7'''
    __tablename__ = 'bo_types'
    
    id = db.Column(db.Integer, nullable=False, unique=True, primary_key=True, autoincrement=True)
    name = db.Column(db.String(40), nullable=False)

    rel_rooms = db.relationship("Room", back_populates="rel_bo_types")


class Current_season(db.Model):
    '''Таблица карт доступных в текущем сезоне.'''
    __tablename__ = 'current_season'

    id = db.Column(db.Integer, nullable=False, unique=True, primary_key=True, autoincrement=True)
    object_id = db.Column(db.Integer,db.ForeignKey('objects.id'), nullable=False)

    rel_objects = db.relationship("Object", back_populates="rel_current_season")


class Game_mode(db.Model):
    '''Таблица режимов игры. Содержит duel и tdm.'''
    __tablename__ = 'game_modes'

    id = db.Column(db.Integer, nullable=False, unique=True, primary_key=True, autoincrement=True)
    name = db.Column(db.String(40), nullable=False)
    player_count = db.Column(db.Integer, nullable=False, unique=False)

    rel_rooms = db.relationship("Room", back_populates="rel_game_modes")


class Object_type(db.Model):
    '''Таблица типов объектов. Содержит в себе 2 типа: карты и чемпионы'''
    __tablename__ = 'object_types'

    id = db.Column(db.Integer, nullable=False, unique=True, primary_key=True, autoincrement=True)
    name = db.Column(db.String(40), nullable=False)

    rel_objects = db.relationship("Object", back_populates="rel_object_types")


class Object(db.Model):
    '''Таблица объектов. Содержит в себе все карты и всех чемпионов.'''
    __tablename__ = 'objects'

    id = db.Column(db.Integer, nullable=False, unique=True, primary_key=True, autoincrement=True)
    type = db.Column(db.Integer,db.ForeignKey('object_types.id'), nullable=False)
    name = db.Column(db.String(40), nullable=False)
    shortname = db.Column(db.String(10), nullable=False)
    img_url = db.Column(db.String(300), nullable=False)

    rel_current_season = db.relationship("Current_season", back_populates="rel_objects")
    rel_object_types = db.relationship("Object_type", back_populates="rel_objects")


class Team(db.Model):
    '''Таблица команд. Пока только blue и red.'''
    __tablename__ = 'teams'

    id = db.Column(db.Integer, nullable=False, unique=True, primary_key=True, autoincrement=True)
    name = db.Column(db.String(40), nullable=False)

    rel_results = db.relationship("Result", back_populates="rel_teams")




# ------ Функции основные -----------------------------------------------------

def start_game(nickname, game_mode, bo_type, seed) -> dict:
    ''' Создает пользователя если необходимо, создает комнату и результат
    для пользователя создавшего комнату. Возвращает словарь основных
    параметров игры для передачи его фронту.'''
    new_user_id = User.create_user(nickname)
    new_room = Room.create_room(game_mode, bo_type, seed)
    new_result_id = Result.create_result(new_user_id, new_room['id'], team_id=1)
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

def join_room(nickname, room_uuid) -> dict:
    '''Создает пользователя если необходимо, проверяет существование комнаты
    создает результат для подключающегося пользователя. Возвращает словарь
    основных параметров игры для передачи его фронту.'''
    # Проверка на существование комнаты
    room_exist = bool(Room.query.filter_by(room_uuid=room_uuid).first())
    if not room_exist:
        raise RoomDoesNotExist('This room does not exist in database')

    # Создаем пользователя
    new_user_id = User.create_user(nickname=nickname)
    
    # Получаем комнату по uuid
    room = Room.query.filter_by(room_uuid=room_uuid).first()
    
    # Создаем результат подключающегося пользователя
    # NOTE будет работать только при условии что команд всего две.
    new_result_id = Result.create_result(new_user_id, room.id, team_id=2)
    
    # Инициализируем текущего активного игрока в комнате
    Room.init_current_user()

    # Готовим вывод
    game_params = {
        'nickname': nickname,
        'user_id': new_user_id,
        # TODO Сделать так что бы seed в таблице могло принимать значения
        # только 1, 2. Где 1 это синие, 2 это красные.
        'seed': room.seed,
        'result_id': new_result_id
    }
    return game_params




# ------ Функции вспомогательные ----------------------------------------------

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
