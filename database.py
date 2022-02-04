import random
import json

from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import text as sa_text

from exceptions import RoomDoesNotExist
from application import _DB as db


# TODO Переименовать этот файл в Models.py. Чисто в целях стандартизации.
# Так как в большинстве просмотренных видео, этот файл назвают именно так.

# TODO Привести в порядок свойства отношений моделей. Что бы названия
# соответствовали типам связей между таблицами.

'''TODO Функция или Класс преобразования данных полученных из формы в
удобоваримые для классов моделей БД. Принимает str, возвращает int
'''


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
        id пользователя.
        '''
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
    room_uuid = db.Column(UUID(as_uuid=True), nullable=True, server_default=sa_text("uuid_generate_v4()")) 
    bo_type_id = db.Column(db.Integer,db.ForeignKey('bo_types.id'), nullable=False)
    game_mode_id = db.Column(db.Integer,db.ForeignKey('game_modes.id'), nullable=False)
    current_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    current_action_id = db.Column(db.Integer, db.ForeignKey('actions.id'), nullable=False, default = 4)
    current_step_id = db.Column(db.Integer, db.ForeignKey('object_types.id'), nullable=False, default = 1)
    seed = db.Column(db.Integer, db.ForeignKey('teams.id'), nullable=False)

    rel_object_types = db.relationship("Object_type", back_populates="rel_rooms")
    rel_game_modes = db.relationship("Game_mode", back_populates="rel_rooms")
    rel_bo_types = db.relationship("Bo_type", back_populates="rel_rooms")
    rel_results = db.relationship("Result", back_populates="rel_rooms")
    rel_actions = db.relationship("Action", back_populates="rel_rooms")
    rel_users = db.relationship("User", back_populates="rel_rooms")
    rel_teams = db.relationship("Team", back_populates="rel_rooms")

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
        '''Создает комнату в таблице rooms и возвращает словарь содержащий
        id и uuid комнаты. На вход принимает только int
        '''

        room_params = {
            "game_mode_id": game_mode,
            "bo_type_id": bo_type,
            "seed": seed,
            # TODO Поля ниже должны заполнятся на основе конфига или класса
            # который описывает определенные game_mod'ы и bo_typ'ы
            "current_action_id": 2,
            "current_step_id": 1
        }

        # создаем комнату
        new_room = cls(**room_params)

        try:
            db.session.add(new_room)
            db.session.commit()
        except:
            # отменяем транзакцию в случае ошибки.
            db.session.rollback()
            raise
        return {'id': new_room.id, 'uuid': new_room.room_uuid}

    @classmethod
    def init_current_user(cls):
        '''Создает запись активного игрока в комнате.'''

        try:
            for result in cls.rel_results:
                if result.team_id == cls.seed:
                    cls.current_user_id = result.user_id
                    db.session.commit()
                    break
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
    map_picks = db.Column(db.String, nullable=True)
    map_bans = db.Column(db.String, nullable=True)
    champ_picks = db.Column(db.String, nullable=True)
    champ_bans = db.Column(db.String, nullable=True)
    team_id = db.Column(db.Integer,db.ForeignKey('teams.id'), nullable=False)

    rel_users = db.relationship("User", back_populates="rel_results")
    rel_rooms = db.relationship("Room", back_populates="rel_results")
    rel_teams = db.relationship("Team", back_populates="rel_results")

    @classmethod
    def get_result(cls, room_id, **kwargs):
        '''Ищет результаты игроков по id комнаты, так же принимает **kwargs
        для дополнительной фильтрации
        '''

        requested_result = cls.query.filter_by(room_id=room_id, **kwargs).all()

        return requested_result

    @classmethod
    def create_result(cls, user_id, room_id, team_id) -> int:
        '''Создает результат в таблице results и
        возвращает id результата.
        '''
        # TODO Проверяем заполнена ли комната
        # в случае если комната заполнена, выбрасываем exception, хз какой правда.

        result_params = {
            "user_id": user_id,
            "room_id": room_id,
            "team_id": team_id
        }

        # создаем результат
        new_results = cls(**result_params)
        
        try:
            db.session.add(new_results)
            db.session.commit()
        except:
            # отменяем транзакцию в случае ошибки.
            db.session.rollback()
            raise
        return new_results.id


    @classmethod
    def update_result(cls, room_id, action, user_id, choice):
        '''Вносит в базу выбор игрока'''
        result = cls.get_result(room_id=room_id, user_id=user_id)[0]
        if not result:
            # если нет такой комнаты или пользователя
            raise ValueError

        current_step = result.rel_rooms.current_step
        current_action = result.rel_rooms.rel_actions
        if current_action.name != action:
            raise ValueError

        if action == 'ban':
            # TODO Добавить проверку на совпадения в существующем списке банов
            # TODO Найти элегантное решение вместо этого колхоза.
            # NOTE Этот кусок кода нужен что бы создать совершенно новый список
            # Если этого не сделать, а просто добавить значение к result.bans
            # или result.picks, то изменения в базе не применятся.
            bans = []
            if current_step == 'map':
                for ban in result.map_bans:
                    bans.append(ban)
                bans.append(choice)
                result.map_bans = bans
            else:
                for ban in result.champ_bans:
                    bans.append(ban)
                bans.append(choice)
                result.champ_bans = bans
        else:
            # TODO Добавить проверку на совпадения в существующем списке пиков
            # TODO Найти элегантное решение вместо этого колхоза.
            # NOTE Этот кусок кода нужен что бы создать совершенно новый список
            # Если этого не сделать, а просто добавить значение к result.bans
            # или result.picks, то изменения в базе не применятся.
            picks = []
            if current_step == 'map':
                for pick in result.map_picks:
                    picks.append(pick)
                picks.append(choice)
                result.map_picks = picks
            else:
                for pick in result.champ_picks:
                    picks.append(pick)
                picks.append(choice)
                result.champ_picks = picks

        try:
            db.session.add(result)
            db.session.commit()
        except:
            # отменяем транзакцию в случае ошибки.
            db.session.rollback()
            raise

        return True

class Action(db.Model):
    '''Таблица действий. Ban, pick, wait, end. Wait необходим для того
    что бы сказать фронту что нужно подождать второго игрока. End для того
    что бы закончить игру и вывести результат
    '''
    __tablename__ = 'actions'

    id = db.Column(db.Integer, nullable=False, unique=True, primary_key=True, autoincrement=True)
    name = db.Column(db.String(30), nullable=False)

    rel_rooms = db.relationship("Room", back_populates="rel_actions")


class Bo_type(db.Model):
    '''Таблица типов игр по колическу карт в матче.
    Содержит bo1, bo3, bo5, bo7
    '''
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
    rel_rooms = db.relationship("Room", back_populates="rel_object_types")


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
    rel_rooms = db.relationship("Room", back_populates="rel_teams")




# ------ Функции основные -----------------------------------------------------

def start_game(nickname, game_mode, bo_type, seed) -> dict:
    ''' Создает пользователя если необходимо, создает комнату и результат
    для пользователя создавшего комнату. Возвращает словарь основных
    параметров игры для передачи его фронту.
    '''
    new_user_id = User.create_user(nickname)
    new_room = Room.create_room(game_mode, bo_type, seed)
    new_result_id = Result.create_result(new_user_id, new_room['id'], team_id=1)
    game_params = {
        'nickname': nickname,
        'user_id': new_user_id,
        'room_uuid': new_room['uuid'],
        'game_mode': game_mode,
        'bo_type': bo_type,
        'seed': seed,
        'result_id': new_result_id,
        'map_picks': [],
        'map_bans': [],
        'champ_picks': [],
        'cahmp_bans': []
    }
    return game_params

def join_room(nickname, room_uuid) -> dict:
    '''Создает пользователя если необходимо, проверяет существование комнаты
    создает результат для подключающегося пользователя. Возвращает словарь
    основных параметров игры для передачи его фронту.
    '''
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

def generate_report(room_uuid):
    '''Генерируем полный отчет о состоянии игры в JSON формате'''
    # Получаем инфу по комнате и по доступным картам
    room = Room.get_room(room_uuid=room_uuid)
    champions = Object.query.filter_by(type=2).all()
    current_season = Current_season.query.all()
    season_maps = [item.rel_objects for item in current_season]
    results = room.rel_results

    # Генерим инфу по игрокам
    player_state = {}
    player_states = []
    current_game_state = {}
    for result in results:
        player_state['nickname'] = result.rel_users.nickname
        player_state['map_picks'] = [
            obj for obj in result.map_picks
        ]
        player_state['map_bans'] = [
            obj for obj in result.map_bans
        ]
        player_state['champ_picks'] = [
            obj for obj in result.champ_picks
        ]
        player_state['champ_bans'] = [
            obj for obj in result.champ_bans
        ]
        player_states.append(player_state)
        player_state = {}

    # Генерим инфу по комнате
    current_game_state['current_action'] = room.rel_actions.name
    current_game_state['players'] = player_states
    current_game_state['room_uuid'] = room_uuid
    current_game_state['seed'] = room.seed

    current_game_state['maps'] = [
        map.name for map in season_maps if map.type==1
    ]
    current_game_state['champs'] = [
        champ.name for champ in champions
    ]

    if room.rel_users != None:
        current_game_state['current_player'] = room.rel_users.nickname
    else:
        current_game_state['current_player'] = ''

    return json.dumps(current_game_state)


class IJoinForm():
    '''Интерфейс формы подключения к комнате
    Принимает на вход строковое значени room_uuid
    Возвращает room_id
    '''
    
    def __init__(self, room_uuid):
        self.room_id = Room.query.filter_by(room_uuid=room_uuid).first().id
    
    def __repr__(self):
        return self.room_id


class ICreateForm():
    '''Интерфейс формы создания комнаты
    Принимает на вход строковые значения:
        * game_mode
        * bo_type
        * seed
    Возвращает словарь id:
        * game_mode_id
        * bo_type_id
        * seed
        NOTE seed указывает на team_id
    '''

    def __init__(self, game_mode, bo_type, seed):
        self.game_mode_id = Game_mode.query.filter_by(name=game_mode).first().id
        self.bo_type_id = Bo_type.query.filter_by(name=bo_type).first().id

        if seed == 'Opponent':
            self.seed = 2
        elif seed == 'You':
            self.seed = 1
        else:
            self.seed = random.choice([1,2])
    
    def __repr__(self):
        return {
            'game_mode_id': self.game_mode_id,
            'bo_type_id': self.bo_type_id,
            'seed': self.seed
        }
