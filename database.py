from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import text

from application import _DB as db


'''
Файл моделей и логики работы с БД.
'''

# TODO Переименовать этот файл в Models.py. Чисто в целях стандартизации.
# Так как в большинстве просмотренных видео, этот файл назвают именно так.

# TODO Привести в порядок свойства отношений моделей. Что бы названия
# соответствовали типам связей между таблицами.

''' TODO Продумать логику методов в классах. Пришла мысль о том что методы
создания результата логичнее расположить внутри класса Room.
'''

''' TODO Покрыть модели тестами'''

''' TODO Заполнить таблицу правилами 2v2.'''




# ------ Модели ---------------------------------------------------------------

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

        return new_user.id


class Room(db.Model):
    '''Таблица комнат'''
    __tablename__ = 'rooms'

    id = db.Column(db.Integer, nullable=False, unique=True, primary_key=True,
                   autoincrement=True)
    room_uuid = db.Column(UUID(as_uuid=True), nullable=True,
                          server_default=text("uuid_generate_v4()")) 
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
    def get_room(cls, room_uuid):
        '''Ищет комнату в таблице по uuid.'''
        requested_room = cls.query.filter_by(room_uuid=room_uuid).first()
        return requested_room

    @classmethod
    def create_room(cls, seed, current_step_id) -> dict:
        '''Создает комнату в таблице rooms и возвращает словарь содержащий
        id и uuid комнаты. На вход принимает только int
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

    def next_user(self):
        '''Меняет активного игрока в комнате. Работает пока только для двух
        игроков
        '''
        current_user_id = self.current_user_id
        for result in self.rel_results:
            if result.user_id != current_user_id:
                next_user_id = result.user_id

        self.current_user_id = next_user_id
        try:
            db.session.commit()
        except:
            db.session.rollback()
            raise

    def next_step(self):
        '''Меняет текущий шаг в комнате'''
        self.next_user()
        next_step = self.current_step_id + 1
        self.current_step_id = next_step
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
        '''Создает результат в комнате. Используется при создании комнаты
        и при подключении к ней. Воозвращает id нового результата.
        '''

        # Проверка на заполненость комнаты
        results = self.get_results()
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
    map_picks = db.Column(db.String, nullable=True)
    map_bans = db.Column(db.String, nullable=True)
    champ_picks = db.Column(db.String, nullable=True)
    champ_bans = db.Column(db.String, nullable=True)
    team_id = db.Column(db.Integer,db.ForeignKey('teams.id'), nullable=False)

    rel_users = db.relationship("User", back_populates="rel_results")
    rel_rooms = db.relationship("Room", back_populates="rel_results")
    rel_teams = db.relationship("Team", back_populates="rel_results")


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


class Team(db.Model):
    '''Таблица команд. Пока только blue и red.'''
    __tablename__ = 'teams'

    id = db.Column(db.Integer, nullable=False, unique=True, primary_key=True,
                   autoincrement=True)
    name = db.Column(db.String(40), nullable=False)

    rel_results = db.relationship("Result", back_populates="rel_teams")
    rel_rooms = db.relationship("Room", back_populates="rel_teams")




# ------ Функции основные -----------------------------------------------------

def start_game(nickname, seed, current_step_id) -> dict:
    ''' Создает пользователя если необходимо, создает комнату и результат
    для пользователя создавшего комнату. Возвращает словарь основных
    параметров игры для передачи его фронту.
    '''
    new_user_id = User.create_user(nickname)
    new_room = Room.create_room(seed, current_step_id)
    # Создаем результат пользователя создавшего игру
    new_room.create_result(new_user_id, team_id=1)
    
    # Забираем из типа UUID только строковое представление этого uuid
    new_room_uuid = new_room.room_uuid.urn.split(':')[-1]

    return {'room_uuid': new_room_uuid, 'nickname': nickname}

def join_room(nickname, room_uuid) -> dict:
    '''Создает пользователя если необходимо, проверяет существование комнаты
    создает результат для подключающегося пользователя. True или False в
    в зависимости от успеха операции.
    '''
    # Получаем комнату по uuid
    room = Room.get_room(room_uuid)
    
    # Проверка на существование комнаты
    if not bool(room):
        raise Exception('Этой комнаты не существует в базе данных')

    # Создаем пользователя
    new_user_id = User.create_user(nickname=nickname)
    
    # Создаем результат подключающегося пользователя
    # NOTE будет работать только при условии что команд всего две.
    new_result_id = room.create_result(new_user_id, team_id=2)
    
    # Инициализируем текущего активного игрока в комнате
    room.init_current_user()

    room_uuid = room.room_uuid.urn.split(':')[-1]

    if new_result_id == None:
        return False

    return True




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


def generate_report(room_uuid):
    '''Генерируем полный отчет о состоянии игры в JSON формате'''
    # Получаем инфу по комнате и по доступным картам
    room = Room.get_room(room_uuid=room_uuid)

    # TODO сделать в виде метода экземпляра класса Room (get_champions)
    champions = Object.query.filter_by(type=2).all()
    # TODO сделать в виде метода экземпляра класса Room (get_maps)
    current_season = Current_season.query.all()
    season_maps = [item.rel_objects for item in current_season]
    results = room.rel_results

    # Генерим инфу по игрокам
    player_state = {}
    player_states = []
    current_game_state = {}
    for result in results:
        player_state['nickname'] = result.rel_users.nickname
        if result.map_picks != None:
            player_state['map_picks'] = [
                obj for obj in result.map_picks
            ]
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
        } for map in season_maps if map.type==1
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
