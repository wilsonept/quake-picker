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

# TODO Привести в порядок свойства отношений моделей. Что бы названия
# соответствовали типам связей между таблицами.

# TODO Продумать логику методов в классах.
# Пришла мысль о том что методы создания результата логичнее расположить
# внутри класса Room.

# TODO Покрыть модели тестами

# TODO Обойти отсутствии поддержки uuid формата данный в SQLite.
# Сейчас для миграции на PostgreSQL потребуется править модели
# (при условии что мы хотим работать с нативным для PostgreSQL uuid).
# TODO Протестировать класс MimicUUID в работе с PostgreSQL.


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
        requested_user = cls.query.filter_by(nickname=nickname).first()
        return requested_user

    @classmethod
    def create_user(cls, nickname) -> int:
        """
        Создает пользователя в таблице если необходимо и возвращает
        id пользователя.
        """
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
    def create_room(cls, seed, current_step_id):
        """
        Создает комнату и возвращает ее инстанс.
        На вход принимает только int.
        """

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

    def init_current_user(self):
        """Создает запись активного игрока в комнате."""

        try:
            for session in self.rel_sessions:
                if session.team_id == self.seed:
                    self.current_user_id = session.user_id
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


    def next_step(self):
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
        Создает сессию подключения к комнате. Используется при создании комнаты
        и при подключении к ней. Воозвращает id нового результата.
        """

        # Проверка на заполненость комнаты.
        sessions = self.get_sessions()
        # TODO assert???
        if len(sessions) > 1:
            raise Exception("Комната уже заполнена.")

        # Создаем сессию.
        new_session = Session(user_id=user_id, room_id=self.id,
                              team_id=team_id)
        
        try:
            db.session.add(new_session)
            db.session.commit()
        except:
            # Отменяем транзакцию в случае ошибки.
            db.session.rollback()
            raise
        return new_session.id

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


    def save_choice(self, nickname, action, object_type, choice, map_name=None):
        """Вносит в базу выбор игрока."""

        # Проверяем валидность игрока.
        if nickname != self.rel_users.nickname:
            raise Exception("Ваша очередь еще не наступила.")
        
        current_object_type = self.rel_rules.rel_object_types
        current_action = self.rel_rules.rel_actions

        # Проверяем совпадение активного действия в комнате.
        if current_action.name != action:
            raise Exception(f"Вы выполняете не верное действие: {action}")

        # Проверяем совпадение активного типа в комнате.
        if current_object_type.name != object_type:
            raise Exception((
                "Вы запрашиваете действие над не верным типом объекта: "
                f'{current_object_type}'
            ))
        
        # Определяем id выбранного объекта.
        if object_type == "map":
            choices = self.rel_map_choices
        elif object_type == "champ":
            choices = self.rel_champ_choices
        object_id = [obj.id for obj in choices if obj.shorname == choice][0]

        # Определяем id сессии.
        for session in self.rel_sessions:
            if session.rel_users.nickname == nickname:
                session_id = session.id
            else:
                raise Exception(
                    "Сессии для указанного имени игрока не существует."
                )

        new_choice = None
        if current_object_type.name == "map":
            # Вставляем значения в таблицу map_choices.
            new_choice = Map_choice(
                room_id = self.id,
                object_id = object_id,
                action_id = self.rel_rules.rel_actions.id,
                session_id = session_id
            )

        elif current_object_type.name == "champ":
            # Определяем id карты для которой производился выбор.
            for map_choice in self.rel_map_choices:
                if map_choice.shortname == map_name:
                    map_id = map_choice.id
                else:
                    raise Exception(
                        f"{map_name} отсутствует в таблице выбранных карт."
                    )
            # Вставляем значения в таблицу champ_choices.
            new_choice = Champ_choice(
                room_id = self.id,
                object_id = object_id,
                action_id = self.rel_rules.rel_actions.id,
                map_choice_id = map_id,
                session_id = session_id
            )

        if new_choice:
            db.session.add(new_choice)
            try:
                db.session.commit()
            except:
                db.session.rollback()
                raise
            return True


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
    Таблица типов игр по колическу карт в матче.
    Содержит bo1, bo3, bo5, bo7
    """
    __tablename__ = "bo_types"
    
    id = db.Column(db.Integer, nullable=False, unique=True, primary_key=True,
                   autoincrement=True)
    name = db.Column(db.String(40), nullable=False)

    # Отношения многие к одному.
    rel_rules = db.relationship("Rule", back_populates="rel_bo_type")


class Current_season(db.Model):
    """Таблица карт доступных в текущем сезоне."""
    __tablename__ = "current_season"

    id = db.Column(db.Integer, nullable=False, unique=True, primary_key=True,
                   autoincrement=True)
    object_id = db.Column(db.Integer,db.ForeignKey("objects.id"),
                          nullable=False)

    # Отношения один ко многим.
    rel_object = db.relationship("Object",
                                 back_populates="rel_current_season")


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
    shortname = db.Column(db.String(10), nullable=False)
    img_url = db.Column(db.String(300), nullable=False)

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

def start_game(nickname, seed, current_step_id) -> dict:
    """
    Создает пользователя если необходимо, создает комнату и сессию
    пользователя создавшего комнату. Возвращает словарь с room_uuid и
    nickname.
    """

    # Создаем пользователя.
    user = User.create_user(nickname=nickname)
    
    # Создаем комнату.
    room = Room.create_room(seed=seed, current_step_id=current_step_id)

    # Создаем сессию пользователя создавшего игру.
    room.create_session(user_id=user.id, team_id=1)
    
    # Забираем из типа UUID только строковое представление этого uuid.
    # NOTE Закомментировано так как sqlite не поддерживает данный тип данных.
    # room_uuid = room.room_uuid.urn.split(':')[-1]
    room_uuid = room.room_uuid

    return {"room_uuid": room_uuid, "nickname": nickname}

def join_room(nickname, room_uuid) -> dict:
    """
    Создает пользователя если необходимо, проверяет существование
    комнаты создает сессию подключающегося пользователя.
    True или False в зависимости от успеха операции.
    """

    # Получаем комнату по uuid.
    # NOTE При переходе на postgresql функцию str надо убрать.
    room_uuid = str(room_uuid)
    room = db.session.query(Room).filter_by(room_uuid=room_uuid).first()
    
    # Проверка на существование комнаты.
    if not room:
        raise Exception("Этой комнаты не существует в базе данных.")

    # Создаем пользователя.
    user = User.create_user(nickname=nickname)
    
    # Создаем результат подключающегося пользователя.
    session_id = room.create_session(user_id=user.id, team_id=2)
    
    # Инициализируем текущего активного игрока в комнате.
    room.init_current_user()

    # Забираем из типа UUID только строковое представление этого uuid.
    # NOTE Закомментировано так как sqlite не поддерживает данный тип данных.
    # room_uuid = room.room_uuid.urn.split(':')[-1]
    room_uuid = room.room_uuid

    if session_id == None:
        return False

    return True




# ------ Функции вспомогательные ---------------------------------------

def delete_room(room_uuid):
    """Удаляет комнату и результат по заданным room_uuid."""
    
    # получаем вхождения которые надо удалить
    room = db.session.query(Room).filter_by(room_uuid=room_uuid).first()

    if not room:
        print("Нечего удалять.")
        return True
    elif room.rel_sessions:
        for session in room.rel_sessions:
            try:
                db.session.delete(session)
                db.session.commit()
            except:
                db.session.rollback()
                raise
    
    room.delete_room(room_uuid=room_uuid)
    return True


def generate_report(room_uuid):
    """Генерирут полный отчет о состоянии игры в JSON формате."""
    
    # Получаем инфу по комнате и по доступным картам.
    room = db.session.query(Room).filter_by(room_uuid=room_uuid).first()

    # Получаем список доступных героев.
    condition = {"type": 2}
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
                "img_url": map.img_url,
                "short_name": map.shortname
            } for map in maps
        ]

        actual_champs = [
            {
                "champ_name": champ.name,
                "img_url": champ.img_url,
                "short_name": champ.shortname,
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

    def get_champ_choice_report(champ_name, short_name, img_url, map_name):
        return {
            "champ_name": champ_name,
            "img_url": img_url,
            "short_name": short_name,
            "map_name": map_name
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
            },
            "champ_choices": {
                "bans": [],
                "picks": []
            }
        }

    # Проверка на наличие текущего игрока в комнате.
    if not room.rel_users:
        raise Exception(
            "Текущий игрок еще не определен. Ожидаем второго игрока."
        )

    report = get_room_report(
        room_uuid = room_uuid,
        current_action = room.rel_rules.rel_actions.name,
        current_player = room.rel_users.nickname,
        current_object = room.rel_rules.rel_object_types.name,
        seed = room.seed,
        maps = maps,
        champs = champs
    )

    map_choices = room.rel_map_choices
    champ_choices = room.rel_champ_choices

    player_reports = []
    for session in room.rel_sessions:

        map_picks = []
        map_bans = []
        # Получаем выбранные и забаненые карты.
        for map_choice in session.rel_map_choices:
            map_choice_report = get_map_choice_report(
                map_choice.rel_objects.name,
                map_choice.rel_objects.shortname,
                map_choice.rel_objects.img_url,
            )
            # Добавляем к списку выбранных карт.
            if map_choice.action_id == 1:
                map_picks.append(map_choice_report)
            # Добавляем к списку забанены карт.
            elif map_choice.action_id == 2:
                map_bans.append(map_choice_report)

        champ_picks = []
        champ_bans = []
        # Получаем выбранного и забаненого чемпиона.
        if session.rel_champ_choices:
            for champ_choice in session.rel_champ_choices:
                # Получаем название карты для которой был выбран чемпион.
                if champ_choice.rel_map_choices:
                    for map_choice in champ_choice.rel_map_choices:
                        champ_choice_report = get_champ_choice_report(
                            champ_choice.rel_objects.name,
                            champ_choice.rel_objects.shortname,
                            champ_choice.rel_objects.img_url,
                            map_choice.shortname
                        )
                        # Добавляем к списку выбранных чемпионов.
                        if champ_choice.action_id == 1:
                            champ_picks.append(champ_choice_report)
                        # Добавляем к списку выбранных чемпионов.
                        elif champ_choice.action_id == 2:
                            champ_bans.append(champ_choice_report)
                else:
                    map_choice = db.session.query(Object).filter_by(
                        id=champ_choice.map_choice_id).first()
                    champ_choice_report = get_champ_choice_report(
                        champ_choice.rel_objects.name,
                        champ_choice.rel_objects.shortname,
                        champ_choice.rel_objects.img_url,
                        map_choice.shortname
                    )
                    # Добавляем к списку выбранных чемпионов.
                    if champ_choice.action_id == 1:
                        champ_picks.append(champ_choice_report)
                    # Добавляем к списку выбранных чемпионов.
                    elif champ_choice.action_id == 2:
                        champ_bans.append(champ_choice_report)

        # Склеиваем отчет для одного игрока.
        player_report = get_player_report(
            session.rel_users.nickname,
            session.rel_teams.name
        )
        player_report["map_choices"]["picks"] = map_picks
        player_report["map_choices"]["bans"] = map_bans
        player_report["champ_choices"]["picks"] = champ_picks
        player_report["champ_choices"]["bans"] = champ_bans
        
        # Добавляем в список отчетов игроков.
        player_reports.append(player_report)

    report["players"] = player_reports
    return report


# Функции самотестирования.
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
        User.create_user("wilson")
        User.create_user("bulkin")
        
        room = db.session.query(Room).filter_by(id=1).first()
        if not room:
            room = Room.create_room(seed=1, current_step_id=1)

        champ_choice = db.session.query(Champ_choice).filter_by(id=1).first()
        pprint(generate_report(room.room_uuid))