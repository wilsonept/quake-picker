import random
import sys
from pprint import pprint

# NOTE Закомментировано так как sqlite не поддерживает данный тип данных.
#from sqlalchemy.dialects.postgresql import UUID
#from sqlalchemy import text
from sqlalchemy.types import CHAR, TypeDecorator
from sqlalchemy.dialects.postgresql import UUID
import uuid

from application import _DB as db, conf

"""
Файл моделей и логики работы с БД.
"""


# ------ Вспомогательные классы ----------------------------------------

class MimicUUID(TypeDecorator):
    """
    Прикидывается типом postgresql UUID или CHAR в
    зависимости от конфигурации приложения. 
    Небходим для совместимости приложения с PostgreSQL и SQLite.
    """

    impl = CHAR
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            return dialect.type_descriptor(UUID())
        else:
            return dialect.type_descriptor(CHAR(32))

    def process_bind_param(self, value, dialect) -> None:
        """Выполняется когда мы берем из базы значение."""
        if value == None:
            return value
        elif dialect.name =="postgresql":
            return str(value)
        else:
            if not isinstance(value, uuid.UUID):
                # Используем встроенную библиотеку uuid для получения
                # числового представления uuid для дальнейшего форматирования.
                return "{uuid:32x}".format(uuid=uuid.UUID(value).int)
            else:
                return "{uuid:32x}".format(uuid=value.int)

    def process_result_value(self, value, dialect) -> None:
        """Выполняется когда мы кладем значение в базу."""
        if value == None:
            return value
        elif not isinstance(value, uuid.UUID):
            return uuid.UUID(value)
        else:
            return value
 

# ------ Модели --------------------------------------------------------

class User(db.Model):
    """Таблица пользователей."""
    __tablename__ = "users"

    id = db.Column(db.Integer, nullable=False, unique=True, primary_key=True,
                   autoincrement=True)
    nickname = db.Column(db.String(40), nullable=False)
    is_persistent = db.Column(db.Boolean, nullable=False, default=False)

    # Отношения многие к одному.
    rel_sessions = db.relationship("Session", back_populates="rel_user")
    rel_rooms = db.relationship("Room", back_populates="rel_user")

    @classmethod
    def get_user(cls, nickname):
        """Поиск пользователя по имени, возвращает объект класса User."""
        return cls.query.filter_by(nickname=nickname).first()

    @classmethod
    def create_user(cls, nickname) -> int:
        """
        Создает пользователя в таблице если необходимо и возвращает
        объект класса User.
        """
        # Проверяем пользователя в базе
        user = cls.get_user(nickname)
        if not user:
            # Создаем пользователя
            user = cls(nickname=nickname)
            try:
                db.session.add(user)
                db.session.commit()
            except:
                # отменяем транзакцию в случае ошибки.
                db.session.rollback()
                raise
        return user


class Room(db.Model):
    """Таблица комнат."""
    __tablename__ = "rooms"

    id = db.Column(db.Integer, nullable=False, unique=True, primary_key=True,
                   autoincrement=True)
    room_uuid = db.Column(MimicUUID(), nullable=False, unique=True,
                          default=str(uuid.uuid4()))
    # NOTE Закомментировано так как sqlite не поддерживает данный тип данных.
    # room_uuid = db.Column(UUID(as_uuid=True), server_default=text("uuid_generate_v4()")) 
    current_user_id = db.Column(db.Integer, db.ForeignKey("users.id"),
                                nullable=True)
    current_step_id = db.Column(db.Integer, db.ForeignKey("rules.id"),
                                nullable=False)
    seed = db.Column(db.Integer, db.ForeignKey("teams.id"), nullable=False)

    # Отношения один ко многим.
    rel_rule = db.relationship("Rule", back_populates="rel_rooms")
    rel_user = db.relationship("User", back_populates="rel_rooms")
    rel_team = db.relationship("Team", back_populates="rel_rooms")
    # Отношения многие к одному.
    rel_sessions = db.relationship("Session", back_populates="rel_room")
    rel_map_choices = db.relationship("Map_choice", back_populates="rel_room")
    rel_champ_choices = db.relationship("Champ_choice", back_populates="rel_room")

    @classmethod
    def get_room(cls, room_uuid):
        """Находит комнату по uuid. Возвращает экземпляр класса Room."""
        room = db.session.query(cls).filter_by(room_uuid=room_uuid).first()
        # Проверка на существование комнаты.
        if not room:
            raise Exception(
                f"Комнаты с uuid:{room_uuid} не существует.")

        return room

    @classmethod
    def create_room(cls, seed, current_step_id):
        """
        Создает комнату и возвращает ее экземпляр.
        На вход принимает только int.
        """
        room = cls(seed=seed, current_step_id=current_step_id)
        try:
            db.session.add(room)
            db.session.commit()
        except:
            # отменяем транзакцию в случае ошибки.
            db.session.rollback()
            raise

        return room

    def init_current_user(self):
        """Создает запись активного игрока в комнате."""
        for session in self.rel_sessions:
            if session.team_id == self.seed:
                self.current_user_id = session.user_id

                try:
                    db.session.commit()
                    break
                except:
                    # отменяем транзакцию в случае ошибки.
                    db.session.rollback()
                    raise

    def _next_user(self):
        """Возвращает id следующего активного игрока."""
        current_user_id = self.current_user_id
        for session in self.rel_sessions:
            if session.user_id != current_user_id:
                next_user_id = session.user_id

        return next_user_id

    def _next_step(self):
        """Меняет текущий шаг в комнате."""
        next_user_id = self._next_user()
        next_step = self.current_step_id + 1

        self.current_step_id = next_step
        self.current_user_id = next_user_id
        try:
            db.session.commit()
        except:
            db.session.rollback()
            raise

    def create_session(self, user_id, team_id):
        """
        Создает сессию подключения к комнате в таблице sessions.
        Используется при создании комнаты и при подключении к ней.
        Воозвращает экземпляр класса Session.
        """
        # Проверка на заполненость комнаты.
        sessions = self.get_sessions()

        # TODO assert???
        if len(sessions) > 1:
            raise Exception("Комната уже заполнена.")

        # Создаем сессию.
        session = Session(user_id=user_id, room_id=self.id,
                              team_id=team_id)
        try:
            db.session.add(session)
            db.session.commit()
        except:
            # Отменяем транзакцию в случае ошибки.
            db.session.rollback()
            raise
        return session

    def get_sessions(self):
        """Возвращает список сессий комнаты."""
        sessions = [session for session in self.rel_sessions]
        return sessions

    def get_session(self, user_id):
        """
        Ищет результат в комнате по id игрока.
        Возвращает экземпляр класса Session.
        """
        for session in self.rel_sessions:
            if session.user_id == user_id:
                return session

    def save_choice(self, nickname: str, action: str, object_type: str,
                    choice_sname: str, map_sname: str=None):
        """
        Вносит в базу выбор игрока.
            Параметры:
                :str:`nickname`: ник игрока сделавшего выбор.
                :str:`action`: действие которое совершает игрок.
                :str:`object_type`: тип объекта над которым совершается действие.
                :str:`choice`: короткое имя объекта (short_name)
                :str:`map_name`: имя карты для которой выбирается чемпион.
        """

        # Проверяем валидность игрока.
        if nickname != self.rel_user.nickname:
            raise Exception(f"Очередь игрока '{nickname}' еще не наступила.")
        
        current_object_type = self.rel_rule.rel_object_type
        current_action = self.rel_rule.rel_action

        # Проверяем совпадение активного действия в комнате.
        if current_action.name != action:
            raise Exception(f"Вы выполняете не верное действие: '{action}'")

        # Проверяем совпадение активного типа в комнате.
        if current_object_type.name != object_type:
            raise Exception((
                "Вы запрашиваете действие над не верным типом объекта: "
                f"'{current_object_type}'"
            ))
        
        # Значения в БД хранятся в uppercase.
        choice_sname = choice_sname.upper()

        # Определяем id выбранного объекта.
        object_id = Object.get_obj_by_sname(choice_sname).id

        # Определяем id сессии.
        for session in self.rel_sessions:
            if session.rel_user.nickname == nickname:
                session_id = session.id
                break
            else:
                session_id = None

        if not session_id:
            raise Exception(
                "Сессии для указанного имени игрока не существует.")

        choice = None
        if current_object_type.name == "map":
            # Вставляем значения в таблицу map_choices.
            choice = Map_choice(
                room_id = self.id,
                object_id = object_id,
                action_id = self.rel_rule.rel_action.id,
                session_id = session_id
            )

        elif current_object_type.name == "champ":
            map_sname = map_sname.upper()
            # Определяем id карты для которой производился выбор.
            for map_choice in self.rel_map_choices:
                if map_choice.rel_object.short_name == map_sname:
                    map_id = map_choice.id
                    break
                else:
                    map_id = None

            if not map_id:
                raise Exception(
                    f"'{map_sname}' отсутствует в таблице выбранных карт,"
                )
            # Вставляем значения в таблицу champ_choices.
            choice = Champ_choice(
                room_id = self.id,
                object_id = object_id,
                action_id = self.rel_rule.rel_action.id,
                map_choice_id = map_id,
                session_id = session_id
            )

        if choice:
            db.session.add(choice)
            try:
                db.session.commit()
            except:
                db.session.rollback()
                raise

        # Добавляем шаг ходу игры.
        self._next_step()


class Session(db.Model):
    """Таблица результатов."""
    __tablename__ = "sessions"

    id = db.Column(db.Integer, nullable=False, unique=True, primary_key=True,
                   autoincrement=True)
    room_id = db.Column(db.Integer,db.ForeignKey("rooms.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    team_id = db.Column(db.Integer,db.ForeignKey("teams.id"), nullable=False)

    # Отношения один ко многим.
    rel_room = db.relationship("Room", back_populates="rel_sessions")
    rel_user = db.relationship("User", back_populates="rel_sessions")
    rel_team = db.relationship("Team", back_populates="rel_sessions")
    # Отношения многие к одному.
    rel_map_choices = db.relationship("Map_choice",
                                      back_populates="rel_session")
    rel_champ_choices = db.relationship("Champ_choice",
                                        back_populates="rel_session")


class Rule(db.Model):
    """Таблица правил."""
    __tablename__ = "rules"

    id = db.Column(db.Integer, nullable=False, unique=True, primary_key=True,
                   autoincrement=True)
    step = db.Column(db.Integer, nullable=False) # Порядковый номер шага игры
    game_mode_id = db.Column(db.Integer, db.ForeignKey("game_modes.id"),
                             nullable=False)
    bo_type_id = db.Column(db.Integer, db.ForeignKey("bo_types.id"),
                           nullable=False)
    action_id = db.Column(db.Integer, db.ForeignKey("actions.id"),
                          nullable=False)
    object_type_id = db.Column(db.Integer, db.ForeignKey("object_types.id"),
                               nullable=False)

    # Отношения один ко многим.
    rel_game_mode = db.relationship("Game_mode", back_populates="rel_rules")
    rel_bo_type = db.relationship("Bo_type", back_populates="rel_rules")
    rel_action = db.relationship("Action", back_populates="rel_rules")
    rel_object_type = db.relationship("Object_type",
                                      back_populates="rel_rules")
    # Отношения многие к одному.
    rel_rooms = db.relationship("Room", back_populates="rel_rule")


class Action(db.Model):
    """
    Таблица действий. Ban, pick, wait, end. Wait необходим для того что бы
    сказать фронту что нужно подождать второго игрока. End что бы
    закончить игру и вывести результат.
    """
    __tablename__ = "actions"

    id = db.Column(db.Integer, nullable=False, unique=True, primary_key=True,
                   autoincrement=True)
    name = db.Column(db.String(30), nullable=False)

    # Отношения многие к одному.
    rel_rules = db.relationship("Rule", back_populates="rel_action")
    rel_map_choices = db.relationship("Map_choice",
                                      back_populates="rel_action")
    rel_champ_choices = db.relationship("Champ_choice",
                                        back_populates="rel_action")


class Bo_type(db.Model):
    """
    Таблица типов игр по колическу карт,в матче.
    Содержит bo1, bo3, bo5, bo7
    """
    __tablename__ = "bo_types"
    
    id = db.Column(db.Integer, nullable=False, unique=True, primary_key=True,
                   autoincrement=True)
    name = db.Column(db.String(40), nullable=False)

    # Отношения многие к одному.
    rel_rules = db.relationship("Rule", back_populates="rel_bo_type")


class Current_season(db.Model):
    """Таблица карт,доступных в текущем сезоне."""
    __tablename__ = "current_season"

    id = db.Column(db.Integer, nullable=False, unique=True, primary_key=True,
                   autoincrement=True)
    object_id = db.Column(db.Integer,db.ForeignKey("objects.id"),
                          nullable=False)

    # Отношения один ко многим.
    rel_object = db.relationship("Object",
                                 back_populates="rel_current_season")

    @classmethod
    def get_objects(cls):
        """
        Возвращает список карт (список экземпляров класса Object), 
        относящиеся к текущему сезону.
        """
        season_maps = db.session.query(Current_season).all()
        objects = [map.rel_object for map in season_maps]
        return objects


class Game_mode(db.Model):
    """Таблица режимов игры. Содержит duel и tdm."""
    __tablename__ = "game_modes"

    id = db.Column(db.Integer, nullable=False, unique=True, primary_key=True,
                   autoincrement=True)
    name = db.Column(db.String(40), nullable=False)
    player_count = db.Column(db.Integer, nullable=False, unique=False)

    # Отношения многие к одному.
    rel_rules = db.relationship("Rule", back_populates="rel_game_mode")


class Object_type(db.Model):
    """Таблица типов объектов. Содержит в себе 2 типа: карты и чемпионы."""
    __tablename__ = "object_types"

    id = db.Column(db.Integer, nullable=False, unique=True, primary_key=True,
                   autoincrement=True)
    name = db.Column(db.String(40), nullable=False)

    # Отношения многие к одному.
    rel_objects = db.relationship("Object", back_populates="rel_object_type")
    rel_rules = db.relationship("Rule", back_populates="rel_object_type")


class Object(db.Model):
    """
    Таблица объектов. Содержит в себе все карты и всех чемпионов.
    """
    __tablename__ = "objects"

    id = db.Column(db.Integer, nullable=False, unique=True, primary_key=True,
                   autoincrement=True)
    type = db.Column(db.Integer, db.ForeignKey("object_types.id"),
                     nullable=False)
    name = db.Column(db.String(40), nullable=False)
    short_name = db.Column(db.String(10), nullable=False)
    img_url = db.Column(db.String(300), nullable=False)
    r_img_url = db.Column(db.String(300), nullable=True)

    # Отношения один ко многим.
    rel_object_type = db.relationship("Object_type",
                                      back_populates="rel_objects")
    rel_current_season = db.relationship("Current_season",
                                         back_populates="rel_object")
    rel_map_choices = db.relationship("Map_choice",
                                      back_populates="rel_object")
    # Отношения многие к одному.
    rel_champ_choices = db.relationship("Champ_choice",
                                        back_populates="rel_object")

    @classmethod
    def get_champs(cls):
        """Получает список чемпионов."""
        champs = db.session.query(cls).filter_by(type=2).all()
        return champs

    @classmethod
    def get_maps(cls):
        """Получает список чемпионов."""
        maps = Current_season.get_objects()
        return maps

    @classmethod
    def get_obj_by_sname(cls, short_name):
        """
        Получает экземпляр класса `Object` по короткому имени объекта.
        """
        obj = db.session.query(cls).filter_by(short_name=short_name).first()
        return obj


class Team(db.Model):
    """Таблица команд. Пока только blue и red."""
    __tablename__ = "teams"

    id = db.Column(db.Integer, nullable=False, unique=True, primary_key=True,
                   autoincrement=True)
    name = db.Column(db.String(40), nullable=False)

    # Отношения многие к одному.
    rel_sessions = db.relationship("Session", back_populates="rel_team")
    rel_rooms = db.relationship("Room", back_populates="rel_team")


class Map_choice(db.Model):
    """Таблица выбора игроков."""
    __tablename__ = "map_choices"

    id = db.Column(db.Integer, nullable=False, unique=True, primary_key=True,
                   autoincrement=True)
    session_id = db.Column(db.Integer, db.ForeignKey("sessions.id"),
                          nullable=False)
    object_id = db.Column(db.Integer, db.ForeignKey("objects.id"),
                          nullable=False)
    action_id = db.Column(db.Integer, db.ForeignKey("actions.id"),
                          nullable=False)
    room_id = db.Column(db.Integer, db.ForeignKey("rooms.id"),
                        nullable=False)

    # Отношения один ко многим.
    rel_session = db.relationship("Session", back_populates="rel_map_choices")
    rel_object = db.relationship("Object", back_populates="rel_map_choices")
    rel_action = db.relationship("Action", back_populates="rel_map_choices")
    rel_room = db.relationship("Room", back_populates="rel_map_choices")
    # Отношения многие к одному.
    rel_champ_choices = db.relationship("Champ_choice",
                                        back_populates="rel_map_choice")


class Champ_choice(db.Model):
    """Таблица выбора игроков."""
    __tablename__ = "champ_choices"

    id = db.Column(db.Integer, nullable=False, unique=True, primary_key=True,
                   autoincrement=True)
    session_id = db.Column(db.Integer, db.ForeignKey("sessions.id"),
                          nullable=False)
    object_id = db.Column(db.Integer, db.ForeignKey("objects.id"),
                          nullable=False)
    action_id = db.Column(db.Integer, db.ForeignKey("actions.id"),
                          nullable=False)
    room_id = db.Column(db.Integer, db.ForeignKey("rooms.id"),
                        nullable=False)
    map_choice_id = db.Column(db.Integer, db.ForeignKey("map_choices.id"),
                              nullable=False)

    # Отношения один ко многим.
    rel_session = db.relationship("Session", back_populates="rel_champ_choices")
    rel_object = db.relationship("Object", back_populates="rel_champ_choices")
    rel_action = db.relationship("Action", back_populates="rel_champ_choices")
    rel_room = db.relationship("Room", back_populates="rel_champ_choices")
    rel_map_choice = db.relationship("Map_choice",
                                     back_populates="rel_champ_choices")


# ------ Функции основные ----------------------------------------------

def start_game(nickname: str, seed: str, game_mode: str=None,
               bo_type: str=None) -> dict:
    """
    Создает пользователя если необходимо, создает комнату и сессию
    пользователя создавшего комнату. Возвращает экземпляр класса Room.
    """

    # Приводим seed к числу.
    if seed == "Opponent":
        seed == 2
    elif seed == "You":
        seed == 1
    else:
        seed = random.choice([1, 2])

    # Создаем пользователя.
    try:
        user = User.create_user(nickname=nickname)
    except:
        pass
    
    # Создаем комнату.
    room = Room.create_room(seed=seed, current_step_id=1)

    # Создаем сессию пользователя создавшего игру.
    room.create_session(user_id=user.id, team_id=1)
    
    # Забираем из типа UUID только строковое представление этого uuid.
    # NOTE Закомментировано так как sqlite не поддерживает данный тип данных.
    # room_uuid = room.room_uuid.urn.split(':')[-1]
    # room_uuid = room.room_uuid

    return room


def join_game(nickname, room_uuid) -> dict:
    """
    Создает пользователя если необходимо, проверяет существование
    комнаты создает сессию подключающегося пользователя.
    True или False в зависимости от успеха операции.
    """

    # Получаем комнату по uuid.
    # NOTE При переходе на postgresql функцию str надо убрать.
    room_uuid = str(room_uuid)
    room = Room.get_room(room_uuid)

    # Создаем пользователя.
    user = User.create_user(nickname=nickname)
    
    # Создаем результат подключающегося пользователя.
    session_id = room.create_session(user_id=user.id, team_id=2).id
    
    # Инициализируем текущего активного игрока в комнате.
    room.init_current_user()

    # Забираем из типа UUID только строковое представление этого uuid.
    # NOTE Закомментировано так как sqlite не поддерживает данный тип данных.
    # room_uuid = room.room_uuid.urn.split(':')[-1]
    room_uuid = room.room_uuid

    if not session_id:
        return False
    return True


def generate_report(room_uuid):
    """Генерирут полный отчет о состоянии игры в JSON формате."""
    # Получаем инфу по комнате и по доступным картам.
    room = Room.get_room(room_uuid)

    # Получаем список доступных героев.
    champs = Object.get_champs()
    # Получаем список доступных карт,
    maps = Object.get_maps()
    # Получаем список выбранных карт,
    map_choices = room.rel_map_choices
    # Получаем список выбранных чемпионов.
    champ_choices = room.rel_champ_choices
    # Получаем список активных сессий.
    sessions = room.rel_sessions

    # Получаем тело отчета.
    report = {
        "room_uuid": str(room.room_uuid),
        "current_action": room.rel_rule.rel_action.name,
        "current_player": None,
        "current_object_type": room.rel_rule.rel_object_type.name,
        "seed": room.seed,
        "maps": objects_to_dict(maps),
        "champs": objects_to_dict(champs),
        "map_choices": map_choices_to_dict(map_choices),
        "champ_choices": champ_choices_to_dict(champ_choices),
        "players": sessions_to_dict(sessions),
    }

    # Проверяем если текущий игрок определен, добавляем его в отчет.
    if room.rel_user:
       report["current_player"] = room.rel_user.nickname

    return report


# ------ Функции вспомогательные ---------------------------------------

def champ_choices_to_dict(champ_choices) -> dict:
    """Форматирует список экземпляров класса Champ_choice в отчет."""
    choices = []
    for champ_choice in champ_choices:
        choices.append({
            "action": champ_choice.rel_action.name,

            "champ_name": champ_choice.rel_object.name,
            "champ_short_name": champ_choice.rel_object.short_name,
            "img_url": champ_choice.rel_object.img_url,
            "r_img_url": champ_choice.rel_object.r_img_url,

            "map_name": champ_choice.rel_map_choice.rel_object.name,
            "map_short_name": champ_choice.rel_map_choice.rel_object.short_name,
            "map_img_url": champ_choice.rel_map_choice.rel_object.img_url,

            "nickname": champ_choice.rel_session.rel_user.nickname,
            "team": champ_choice.rel_session.rel_team.name,
        })
    return choices

def map_choices_to_dict(map_choices) -> dict:
    """Форматирует сприсок экземпляров класса Map_choice в отчет."""
    choices = []
    for map_choice in map_choices:
        choices.append({
            "map_name": map_choice.rel_object.name,
            "img_url": map_choice.rel_object.img_url,
            "map_short_name": map_choice.rel_object.short_name,
            "nickname": map_choice.rel_session.rel_user.nickname,
            "action": map_choice.rel_action.name,
        })
    return choices

def sessions_to_dict(sessions) -> dict:
    """Форматирует список экземпляров класса Session в отчет."""
    players = []
    for session in sessions:
        players.append({
            "nickname": session.rel_user.nickname,
            "team": session.rel_team.name,
        })
    return players

def objects_to_dict(objects) -> dict:
    """Форматирует список экземпляров класса Object в отчет."""
    obj_report = [
        {
            "name": obj.name,
            "img_url": obj.img_url,
            "short_name": obj.short_name,
        } for obj in objects
    ]
    return obj_report


# ------ Функции самотестирования. -------------------------------------

def self_db_rebuild(force=False):
    """Удаляет все таблицы базы данных и создает их заново."""
    if not force:
        answer = input(
            (
                "Это действие приведет к полной потере данных."
                "Вы действительно хотите перестроить все таблицы? [N]/Y "
            ) or "N"
        )
        if answer.capitalize() != "Y":
            print("Прервано пользователем.")
            exit()

    # NOTE на postgresql пока не тестировалось поэтому такое условие, 
    # после тестирования на postgres его можно удалить.
    if conf["db_engine"] == "sqlite":
        print("[ DROP ] Удаляю все таблицы.")
        db.drop_all()
        print("[ CREATE ] Создаю таблицы.")
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
            print(f"[ INSERT ] Заполняю таблицу {table[1].__tablename__}")
            for row in table[0]:
                db.session.add(table[1](**row))
                db.session.commit()


if __name__ == "__main__":
    if "rebuild" in sys.argv:
        if "force" in sys.argv:
            self_db_rebuild(force=True)
        else:
            self_db_rebuild()
    else:

        # TODO может добавить сюда выполнение unittest'ов?
        
        """Эмитация игры."""

        print("-------------------------------------------------------")
        print("Запуск Эмитации игры.")
        print("-------------------------------------------------------")

        player1 = "wilson"
        player2 = "bulkin"

        # Первый игрок запускает игру и присоединяется к комнате.
        print(f"[ START ] игрок {player1} начинает игру.")
        room = start_game(player1, 1)

        # Второй игрок присоединяется к комнате.
        print(f"[ JOIN ] игрок {player2} присоединяется к игре.")
        join_game(player2, room.room_uuid)

        # Процедура выбора карт.
        print(f"[ MAP_PICKING ] Этап выбора карт.")
        room.save_choice(player1, "ban", "map", "awoken")
        room.save_choice(player2, "ban", "map", "ck")
        room.save_choice(player1, "pick", "map", "molten")
        room.save_choice(player2, "pick", "map", "vale")
        room.save_choice(player1, "ban", "map", "de")
        room.save_choice(player2, "ban", "map", "ruins")
        room.save_choice(player1, "pick", "map", "exile")

        # Процедура выбора чемпионов.
        print(f"[ CHAMP_PICKING ] Этап выбора чемпионов.")
        room.save_choice(player2, "ban", "champ", "anarki", "molten")
        room.save_choice(player1, "pick", "champ", "athena", "molten")
        room.save_choice(player2, "pick", "champ", "bj", "molten")
        room.save_choice(player1, "ban", "champ", "clutch", "vale")
        room.save_choice(player2, "pick", "champ", "dk", "vale")
        room.save_choice(player1, "pick", "champ", "doom", "vale")
        room.save_choice(player2, "ban", "champ", "eisen", "exile")
        room.save_choice(player1, "pick", "champ", "galena", "exile")
        room.save_choice(player2, "pick", "champ", "keel", "exile")

        print(f"[ RESULT ] Вывод отчета:")
        pprint(generate_report(room.room_uuid))