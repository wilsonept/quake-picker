import sys
from pprint import pprint

# NOTE Закомментировано так как sqlite не поддерживает данный тип данных.
#from sqlalchemy.dialects.postgresql import UUID
#from sqlalchemy import text
from sqlalchemy.types import CHAR, TypeDecorator
from sqlalchemy.dialects.postgresql import UUID
import uuid

from application import _DB as db, conf


'''
Файл моделей и логики работы с БД.
'''

# TODO Привести в порядок свойства отношений моделей. Что бы названия
# соответствовали типам связей между таблицами.

# TODO Продумать логику методов в классах.
# Пришла мысль о том что методы создания результата логичнее расположить
# внутри класса Room.

# TODO Покрыть модели тестами

# TODO Обойти отсутствии поддержки uuid формата данный в SQLite.
# Сейчас для миграции на PostgreSQL потребуется править модели
# (при условии что мы хотим работать с нативным для PostgreSQL uuid).


class MimicUUID(TypeDecorator):
    '''
    Прикидывается типом postgresql UUID или CHAR в
    зависимости от конфигурации приложения. 
    Небходим для совместимости приложения с PostgreSQL и SQLite.
    '''

    impl = CHAR
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(UUID())
        else:
            return dialect.type_descriptor(CHAR(32))

    def process_bind_param(self, value, dialect) -> None:
        '''Выполняется когда мы берем из базы значение.'''
        if value == None:
            return value
        elif dialect.name =='postgresql':
            return str(value)
        else:
            if not isinstance(value, uuid.UUID):
                # Используем встроенную библиотеку uuid для получения
                # числового представления uuid для дальнейшего форматирования.
                return "{uuid:32x}".format(uuid=uuid.UUID(value).int)
            else:
                return "{uuid:32x}".format(uuid=value.int)

    def process_result_value(self, value, dialect) -> None:
        '''Выполняется когда мы кладем значение в базу.'''
        if value == None:
            return value
        elif not isinstance(value, uuid.UUID):
            return uuid.UUID(value)
        else:
            return value
        


# ------ Модели --------------------------------------------------------

class User(db.Model):
    '''Таблица пользователей.'''
    __tablename__ = 'users'

    id = db.Column(db.Integer, nullable=False, unique=True, primary_key=True,
                   autoincrement=True)
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

        return new_user


class Room(db.Model):
    '''Таблица комнат'''
    __tablename__ = 'rooms'

    id = db.Column(db.Integer, nullable=False, unique=True, primary_key=True,
                   autoincrement=True)
    room_uuid = db.Column(MimicUUID(), nullable=False, unique=True,
                          default=str(uuid.uuid4()))
    # NOTE Закомментировано так как sqlite не поддерживает данный тип данных.
    # room_uuid = db.Column(UUID(as_uuid=True), server_default=text("uuid_generate_v4()")) 
    current_user_id = db.Column(db.Integer, db.ForeignKey('users.id'),
                                nullable=True)
    current_step_id = db.Column(db.Integer, db.ForeignKey('rules.id'),
                                nullable=False)
    seed = db.Column(db.Integer, db.ForeignKey('teams.id'), nullable=False)

    rel_results = db.relationship("Result", back_populates="rel_rooms")
    rel_rules = db.relationship("Rule", back_populates="rel_rooms")
    rel_users = db.relationship("User", back_populates="rel_rooms")
    rel_teams = db.relationship("Team", back_populates="rel_rooms")

    @classmethod
    def create_room(cls, seed, current_step_id) -> dict:
        '''Создает комнату в таблице rooms и возвращает словарь
        содержащий id и uuid комнаты. На вход принимает только int
        '''

        # создаем комнату
        new_room = cls(seed=seed, current_step_id=current_step_id)

        try:
            db.session.add(new_room)
            db.session.commit()
        except:
            # отменяем транзакцию в случае ошибки.
            db.session.rollback()
            raise

        return new_room
        # return {'id': new_room.id, 'uuid': new_room.room_uuid}

    def init_current_user(self):
        '''Создает запись активного игрока в комнате.'''

        try:
            for result in self.rel_results:
                if result.team_id == self.seed:
                    self.current_user_id = result.user_id
                    db.session.commit()
                    break
        except:
            # отменяем транзакцию в случае ошибки.
            db.session.rollback()
            raise

    def _next_user(self):
        '''Возвращает id следующего активного игрока'''
        current_user_id = self.current_user_id
        for result in self.rel_results:
            if result.user_id != current_user_id:
                next_user_id = result.user_id

        return next_user_id


    def next_step(self):
        '''Меняет текущий шаг в комнате'''
        next_user_id = self._next_user()
        next_step = self.current_step_id + 1

        self.current_step_id = next_step
        self.current_user_id = next_user_id
        try:
            db.session.commit()
        except:
            db.session.rollback()
            raise

    def delete_room(self):
        '''Удаляет комнату текущего класса.'''
        try:
            db.session.delete(self.room_uuid)
            db.session.commit()
        except:
            db.session.rollback()
            raise
        return True

    def create_result(self, user_id, team_id):
        '''
        Создает результат в комнате. Используется при создании комнаты
        и при подключении к ней. Воозвращает id нового результата.
        '''

        # Проверка на заполненость комнаты
        results = self.get_results()
        
        # TODO assert???
        if len(results) > 1:
            raise Exception('Комната уже заполнена')

        # создаем результат
        new_result = Result(user_id=user_id, room_id=self.id,
                            team_id=team_id)
        
        try:
            db.session.add(new_result)
            db.session.commit()
        except:
            # отменяем транзакцию в случае ошибки.
            db.session.rollback()
            raise
        return new_result.id

    def get_results(self):
        '''Возвращает список всех результатов в комнате'''

        results = [result for result in self.rel_results]
        return results

    def get_result(self, user_id):
        '''Ищет результат в комнате по id игрока.
        Возвращает экземпляр класса Result
        '''

        for result in self.rel_results:
            if result.user_id == user_id:
                return result


    def update_result(self, action, object_type, choice):
        '''Вносит в базу выбор игрока'''

        result = self.get_result(user_id=self.current_user_id)

        if not result:
            # если нет такой комнаты или пользователя
            raise Exception('Запрошенного результата не существует.')

        current_object_type = self.rel_rules.rel_object_types
        current_action = self.rel_rules.rel_actions
        
        # Проверяем совпадение активного действия в комнате
        if current_action.name != action:
            raise Exception(f'Вы выполняете не верное действие: {action}')
        
        # Проверяем совпадение активного типа в комнате
        if current_object_type.name != object_type:
            raise Exception((
                'Вы запрашиваете действие над не верным типом объекта: '
                f'{current_object_type}'
            ))

        
        # Получаем название поля для изменения
        field_to_update = f"{object_type}_{action}s"

        # Поля которые нам может понадобиться изменять
        fields = {
            "map_bans": Result.map_bans,
            "map_picks": Result.map_picks,
            "champ_bans": Result.champ_bans,
            "champ_picks": Result.champ_picks
        }

        already_chosen = []
        if result.__dict__[field_to_update]:
            for item in result.__dict__[field_to_update]:
                already_chosen.append(item)
            
            # Добавляем новое значение
            already_chosen.append(choice)

            db.session.query(Result)\
                .filter(Result.id == result.id)\
                .update({fields[field_to_update]: already_chosen})
        else:
            db.session.query(Result)\
                .filter(Result.id == result.id)\
                .update({fields[field_to_update]: [choice]})

        try:
            db.session.commit()
        except:
            # отменяем транзакцию в случае ошибки.
            db.session.rollback()
            raise

        return True


class Result(db.Model):
    '''Таблица результатов.'''
    __tablename__ = 'results'

    id = db.Column(db.Integer, nullable=False, unique=True, primary_key=True,
                   autoincrement=True)
    room_id = db.Column(db.Integer,db.ForeignKey('rooms.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    team_id = db.Column(db.Integer,db.ForeignKey('teams.id'), nullable=False)

    rel_users = db.relationship("User", back_populates="rel_results")
    rel_rooms = db.relationship("Room", back_populates="rel_results")
    rel_teams = db.relationship("Team", back_populates="rel_results")
    rel_map_choices = db.relationship("Map_choice",
                                      back_populates="rel_results")
    rel_champ_choices = db.relationship("Champ_choice",
                                        back_populates="rel_results")


class Rule(db.Model):
    '''Таблица правил.'''
    __tablename__ = 'rules'

    id = db.Column(db.Integer, nullable=False, unique=True, primary_key=True,
                                 autoincrement=True)
    step = db.Column(db.Integer, nullable=False) # Порядковый номер шага игры
    game_mode_id = db.Column(db.Integer, db.ForeignKey('game_modes.id'),
                             nullable=False)
    bo_type_id = db.Column(db.Integer, db.ForeignKey('bo_types.id'),
                           nullable=False)
    object_type_id = db.Column(db.Integer, db.ForeignKey('object_types.id'),
                               nullable=False)
    action_id = db.Column(db.Integer, db.ForeignKey('actions.id'),
                          nullable=False)

    rel_game_modes = db.relationship("Game_mode", back_populates="rel_rules")
    rel_bo_types = db.relationship("Bo_type", back_populates="rel_rules")
    rel_actions = db.relationship("Action", back_populates="rel_rules")
    rel_rooms = db.relationship("Room", back_populates="rel_rules")
    rel_object_types = db.relationship("Object_type",
                                       back_populates="rel_rules")


class Action(db.Model):
    '''Таблица действий. Ban, pick, wait, end. Wait необходим для того что бы
    сказать фронту что нужно подождать второго игрока. End для того что бы
    закончить игру и вывести результат
    '''
    __tablename__ = 'actions'

    id = db.Column(db.Integer, nullable=False, unique=True, primary_key=True,
                   autoincrement=True)
    name = db.Column(db.String(30), nullable=False)

    rel_rules = db.relationship("Rule", back_populates="rel_actions")
    rel_map_choices = db.relationship("Map_choice",
                                      back_populates="rel_actions")
    rel_champ_choices = db.relationship("Champ_choice",
                                        back_populates="rel_actions")


class Bo_type(db.Model):
    '''Таблица типов игр по колическу карт в матче.
    Содержит bo1, bo3, bo5, bo7
    '''
    __tablename__ = 'bo_types'
    
    id = db.Column(db.Integer, nullable=False, unique=True, primary_key=True,
                   autoincrement=True)
    name = db.Column(db.String(40), nullable=False)

    rel_rules = db.relationship("Rule", back_populates="rel_bo_types")


class Current_season(db.Model):
    '''Таблица карт доступных в текущем сезоне.'''
    __tablename__ = 'current_season'

    id = db.Column(db.Integer, nullable=False, unique=True, primary_key=True,
                   autoincrement=True)
    object_id = db.Column(db.Integer,db.ForeignKey('objects.id'),
                          nullable=False)

    rel_objects = db.relationship("Object",
                                  back_populates="rel_current_season")


class Game_mode(db.Model):
    '''Таблица режимов игры. Содержит duel и tdm.'''
    __tablename__ = 'game_modes'

    id = db.Column(db.Integer, nullable=False, unique=True, primary_key=True,
                   autoincrement=True)
    name = db.Column(db.String(40), nullable=False)
    player_count = db.Column(db.Integer, nullable=False, unique=False)

    rel_rules = db.relationship("Rule", back_populates="rel_game_modes")


class Object_type(db.Model):
    '''Таблица типов объектов. Содержит в себе 2 типа: карты и чемпионы'''
    __tablename__ = 'object_types'

    id = db.Column(db.Integer, nullable=False, unique=True, primary_key=True,
                   autoincrement=True)
    name = db.Column(db.String(40), nullable=False)

    rel_objects = db.relationship("Object", back_populates="rel_object_types")
    rel_rules = db.relationship("Rule", back_populates="rel_object_types")



class Object(db.Model):
    '''
    Таблица объектов. Содержит в себе все карты и всех чемпионов.
    '''
    __tablename__ = 'objects'

    id = db.Column(db.Integer, nullable=False, unique=True, primary_key=True,
                   autoincrement=True)
    type = db.Column(db.Integer, db.ForeignKey('object_types.id'),
                     nullable=False)
    name = db.Column(db.String(40), nullable=False)
    shortname = db.Column(db.String(10), nullable=False)
    img_url = db.Column(db.String(300), nullable=False)

    rel_current_season = db.relationship("Current_season",
                                         back_populates="rel_objects")
    rel_object_types = db.relationship("Object_type",
                                       back_populates="rel_objects")
    rel_map_choices = db.relationship("Map_choice",
                                      back_populates="rel_objects")
    rel_champ_choices = db.relationship("Champ_choice",
                                        back_populates="rel_objects")



class Team(db.Model):
    '''Таблица команд. Пока только blue и red.'''
    __tablename__ = 'teams'

    id = db.Column(db.Integer, nullable=False, unique=True, primary_key=True,
                   autoincrement=True)
    name = db.Column(db.String(40), nullable=False)

    rel_results = db.relationship("Result", back_populates="rel_teams")
    rel_rooms = db.relationship("Room", back_populates="rel_teams")



class Map_choice(db.Model):
    '''Таблица выбора игроков'''
    __tablename__ = 'map_choices'

    id = db.Column(db.Integer, nullable=False, unique=True, primary_key=True,
                   autoincrement=True)
    result_id = db.Column(db.Integer, db.ForeignKey('results.id'),
                          nullable=False)
    object_id = db.Column(db.Integer, db.ForeignKey('objects.id'),
                          nullable=False)
    action_id = db.Column(db.Integer, db.ForeignKey('actions.id'),
                          nullable=False)

    rel_results = db.relationship("Result", back_populates="rel_map_choices")
    rel_objects = db.relationship("Object", back_populates="rel_map_choices")
    rel_actions = db.relationship("Action", back_populates="rel_map_choices")
    rel_champ_choices = db.relationship("Champ_choice",
                                        back_populates="rel_map_choices")



class Champ_choice(db.Model):
    '''Таблица выбора игроков'''
    __tablename__ = 'champ_choices'

    id = db.Column(db.Integer, nullable=False, unique=True, primary_key=True,
                   autoincrement=True)
    result_id = db.Column(db.Integer, db.ForeignKey('results.id'),
                          nullable=False)
    object_id = db.Column(db.Integer, db.ForeignKey('objects.id'),
                          nullable=False)
    action_id = db.Column(db.Integer, db.ForeignKey('actions.id'),
                          nullable=False)
    map_choice_id = db.Column(db.Integer, db.ForeignKey('map_choices.id'),
                              nullable=False)

    rel_results = db.relationship("Result", back_populates="rel_champ_choices")
    rel_objects = db.relationship("Object", back_populates="rel_champ_choices")
    rel_actions = db.relationship("Action", back_populates="rel_champ_choices")
    rel_map_choices = db.relationship("Map_choice",
                                      back_populates="rel_champ_choices")


# ------ Функции основные ----------------------------------------------

def start_game(nickname, seed, current_step_id) -> dict:
    '''Создает пользователя если необходимо, создает комнату и результат
    для пользователя создавшего комнату. Возвращает словарь основных
    параметров игры для передачи его фронту.
    '''

    # Создаем пользователя.
    user = User(nickname=nickname)
    db.session.add(user)
    db.session.commit()
    
    # Создаем комнату.
    room = Room(seed=seed, current_step_id=current_step_id)
    db.session.add(room)
    db.session.commit()

    # Создаем результат пользователя создавшего игру.
    room.create_result(user_id=user.id, team_id=1)
    
    # Забираем из типа UUID только строковое представление этого uuid.
    # NOTE Закомментировано так как sqlite не поддерживает данный тип данных.
    # room_uuid = room.room_uuid.urn.split(':')[-1]
    room_uuid = room.room_uuid

    return {'room_uuid': room_uuid, 'nickname': nickname}

def join_room(nickname, room_uuid) -> dict:
    '''Создает пользователя если необходимо, проверяет существование
    комнаты создает результат для подключающегося пользователя.
    True или False в зависимости от успеха операции.
    '''

    # Получаем комнату по uuid
    # NOTE При переходе на postgresql функцию str надо убрать.
    room_uuid = str(room_uuid)
    room = db.session.query(Room).filter_by(room_uuid=room_uuid).first()
    
    # Проверка на существование комнаты
    if not room:
        raise Exception('Этой комнаты не существует в базе данных')

    # Создаем пользователя
    user = User.create_user(nickname=nickname)
    
    # Создаем результат подключающегося пользователя
    result_id = room.create_result(user_id=user.id, team_id=2)
    
    # Инициализируем текущего активного игрока в комнате
    room.init_current_user()

    # Забираем из типа UUID только строковое представление этого uuid.
    # NOTE Закомментировано так как sqlite не поддерживает данный тип данных.
    # room_uuid = room.room_uuid.urn.split(':')[-1]
    room_uuid = room.room_uuid

    if result_id == None:
        return False

    return True




# ------ Функции вспомогательные ---------------------------------------

def delete_room(room_uuid):
    '''Удаляет комнату и результат по заданным room_uuid'''
    
    # получаем вхождения которые надо удалить
    room = db.session.query(Room).filter_by(room_uuid=room_uuid).first()

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

"""
def generate_report(room_uuid):
    '''Генерирут полный отчет о состоянии игры в JSON формате'''
    
    # Получаем инфу по комнате и по доступным картам.
    room = db.session.query(Room).filter_by(room_uuid=room_uuid).first()

    # Получаем список доступных героев.
    condition = {'type': 2}
    champions = db.session.query(Object).filter_by(**condition).all()
    
    # Получаем список доступных карт.
    season_maps = db.session.query(Current_season).all()
    maps = [map.rel_objects for map in season_maps]

    # Генерим инфу по игрокам
    player_state = {}
    player_states = []
    current_game_state = {}
    for result in room.rel_results:
        player_state['nickname'] = result.rel_users.nickname
        player_state['team'] = result.team_id
        if result.rel_map_choices != None:
            for map_choice in result.rel_map_choices:
                player_state['map_choices'] = {
                    "bans": [],
                    "picks": []
                }
                if map_choice.action_id == 2:
                    player_state['map_choices']['bans'].append(
                        {
                            'map_name': map_choice.rel_objects.name,
                            'img_url': map_choice.rel_objects.img_url,
                            'short_name': map_choice.rel_objects.short_name,
                            'champ_choices': []
                        }
                    )
                elif champ_choice.action_id == 1:
                    player_state['map_choices']['bans'].append(
                        {
                            'map_name': map_choice.rel_objects.name,
                            'img_url': map_choice.rel_objects.img_url,
                            'short_name': map_choice.rel_objects.short_name,
                            'champ_choices': {'bans', 'picks'}
                        }
                    )
                if map_choice.rel_champ_choices != None:
                    for champ_choice in map_choice.rel_champ_choices:
                        if champ_choice.action_id == 2:
                            player_state['map_choices']['bans']['champ_choices']['bans']
                        elif champ_choice.action_id == 1:
                            pass
                        
            # player_state['map_choices'] = [
            #     obj for obj in result.map_picks
            # ]
        else:
            player_state['map_picks'] = []

        if result.map_bans != None:
            player_state['map_bans'] = [
                obj for obj in result.map_bans
            ]
        else:
            player_state['map_bans'] = []

        if result.champ_picks != None:
            player_state['champ_picks'] = [
                obj for obj in result.champ_picks
            ]
        else:
            player_state['champ_picks'] = []

        if result.champ_bans != None:
            player_state['champ_bans'] = [
                obj for obj in result.champ_bans
            ]
        else:
            player_state['champ_bans'] = []

        player_states.append(player_state)
        player_state = {}

    # Генерим инфу по комнате
    current_game_state['current_action'] = room.rel_rules.rel_actions.name
    current_game_state['players'] = player_states
    current_game_state['room_uuid'] = room_uuid
    current_game_state['seed'] = room.seed

    current_game_state['maps'] = [
        {
            "name": map.name,
            "img_url": map.img_url
        } for map in maps if map.type==1
    ]
    current_game_state['champs'] = [
        {"name": champ.name, "img_url": champ.img_url} for champ in champions
    ]

    if room.rel_users != None:
        current_game_state['current_player'] = room.rel_users.nickname
    else:
        current_game_state['current_player'] = ''

    current_game_state['current_object'] = room.rel_rules.rel_object_types.name
    current_game_state['step'] = room.rel_rules.step

    return current_game_state
"""


def generate_report(room_uuid):
    '''Генерирут полный отчет о состоянии игры в JSON формате'''
    
    # Получаем инфу по комнате и по доступным картам.
    room = db.session.query(Room).filter_by(room_uuid=room_uuid).first()

    # Получаем список доступных героев.
    condition = {'type': 2}
    champs = db.session.query(Object).filter_by(**condition).all()
    
    # Получаем список доступных карт.
    season_maps = db.session.query(Current_season).all()
    maps = [map.rel_objects for map in season_maps]

    def get_room_report(room_uuid, current_action,
                        current_player, current_object,
                        seed, maps, champs):

        actual_maps = [
            {
                "map_name": map.name,
                "img_url": map.img_url
            } for map in maps
        ]

        actual_champs = [
            {
                "champ_name": champ.name,
                "img_url": champ.img_url
            } for champ in champs
        ]
        
        return {
            "room_uuid": room_uuid,
            "current_action": current_action,
            "current_player": current_player,
            "current_object": current_object,
            "seed": seed,
            "maps": actual_maps,
            "champs": actual_champs,
            "players": []
        }

    def get_champ_choice_report(champ_name, short_name, img_url):
        return {
            "champ_name": champ_name,
            "img_url": img_url,
            "short_name": short_name
        }

    def get_map_choice_report(map_name, short_name, img_url):
        return {
            "map_name": map_name,
            "img_url": img_url,
            "short_name": short_name,
            "champ_choices": {
                "bans": [],
                "picks": []
            }
        }

    def get_player_report(nickname, team):
        return {
            "nickname": nickname,
            "team": team,
            "map_choices": {
                "bans": [],
                "picks": []
            }
        }

    
    try:
        params = [
            room_uuid,
            room.rel_rules.rel_actions.name,
            room.rel_users.nickname,
            room.rel_rules.rel_object_types.name,
            room.seed,
            maps,
            champs
        ]
    except AttributeError:
        params = [
            room_uuid,
            room.rel_rules.rel_actions.name,
            None,
            room.rel_rules.rel_object_types.name,
            room.seed,
            maps,
            champs
        ] 
    
    report = get_room_report(*params)

    player_reports = []
    for result in room.rel_results:

        map_picks = []
        map_bans = []

        # Получаем выбранную или забаненую карту.
        for map_choice in result.rel_map_choices:

            champ_picks = []
            champ_bans = []
            
            # Если карта выбрана то смотрим еще и чемпионов.
            if map_choice.action_id == 1:

                # Получаем списки выбраных и забаненых персонажей для карты.                
                for champ_choice in map_choice.rel_champ_choices:

                    if champ_choice.action_id == 1:
                        champ_picks.append(get_champ_choice_report(
                            champ_choice.rel_objects.name,
                            champ_choice.rel_objects.img_url,
                            champ_choice.rel_objects.short_name
                        ))

                    elif champ_choice.action_id == 2:
                        champ_bans.append(get_champ_choice_report(
                            champ_choice.rel_objects.name,
                            champ_choice.rel_objects.img_url,
                            champ_choice.rel_objects.short_name
                        ))

                # Генерируем пик карты.
                map_choice_report = get_map_choice_report(
                    map_choice.rel_objects.name,
                    map_choice.rel_objects.img_url,
                    map_choice.rel_objects.shortname,
                )

                # Добавляем в отчет карты и чемпионов.
                map_choice_report["champ_choices"]["picks"] = champ_picks
                map_choice_report["champ_choices"]["bans"] = champ_bans

                # Добавляем к списку выбранных карт.
                map_picks.append(map_choice_report)


            # Если бан то выборка чемпионов не требуется.
            elif map_choice.action_id == 2:

                # Генерируем бан карты.
                map_choice_report = get_map_choice_report(
                    map_choice.rel_objects.name,
                    map_choice.rel_objects.img_url,
                    map_choice.rel_objects.shortname,
                )
            
                # Добавляем к списку забанены карт.
                map_bans.append(map_choice_report)

        # Склеиваем отчет для одного игрока.
        player_report = get_player_report(
            result.rel_users.nickname,
            result.rel_teams.name
        )
        player_report["map_choices"]["picks"] = map_picks
        player_report["map_choices"]["bans"] = map_bans
        
        # Добавляем в список отчетов игроков.
        player_reports.append(player_report)

    report["players"] = player_reports

    return report


# Функции самотестирования.
def self_db_rebuild(force=False):
    ''''''
    if not force:
        answer = input(
            (
                'Это действие приведет к полной потере данных.'
                'Вы действительно хотите перестроить все таблицы? [N]/Y '
            ) or 'N'
        )
        if answer.capitalize() != 'Y':
            print('Прервано пользователем.')
            exit()

    # NOTE на postgresql пока не тестировалось поэтому такое условие, 
    # после тестирования на postgres его можно удалить.
    if conf['db_engine'] == 'sqlite':
        print('[ DROP ] Удаляю все таблицы.')
        db.drop_all()
        print('[ CREATE ] Создаю таблицы.')
        db.create_all()

        import misc
        tables = (
            (misc.object_types, Object_type),
            (misc.objects, Object),
            (misc.current_season, Current_season),
            (misc.actions, Action),
            (misc.game_modes, Game_mode),
            (misc.bo_types, Bo_type),
            (misc.teams, Team),
            (misc.rules, Rule)
        )
        for table in tables:
            print(f'[ INSERT ] Заполняю таблицу {table[1].__tablename__}')
            for row in table[0]:
                db.session.add(table[1](**row))
                db.session.commit()


if __name__ == "__main__":

    if 'rebuild' in sys.argv:

        if 'force' in sys.argv:
            self_db_rebuild(force=True)
        
        self_db_rebuild()
        
    
    else:
        # TODO может добавить сюда выполнение unittest'ов?
        User.create_user('wilson')
        User.create_user('bulkin')
        
        room = db.session.query(Room).filter_by(id=1).first()
        if not room:
            room = Room.create_room(seed=1, current_step_id=1)
        
        pprint(generate_report(room.room_uuid))