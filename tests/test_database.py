import unittest
import sqlalchemy


from models import Object, User, Result, Room, delete_room, db, Map_choice


# ------ Константы ------------------------------------------------------------

MAPS_IN_SEASON = 7 # количество карт в сезоне.
ROOM_UUID = '11111111-ffff-8888-aaaa-cccccccccccc'
SEED = 1


# ------ Вспомогательные классы -----------------------------------------------

class ModelTestCase(unittest.TestCase):
    '''
    Класс расширяющий стандартный unittest.TestCase базовыми тестами для
    классов моделей базы данных.
    '''
    def is_int(self, model, col_name, col_value):
        '''Проверяем указанное поле на int'''

        filter_query = {col_name: col_value}
        model_entry = db.session.query(model).filter_by(**filter_query).first()

        # Проверяем текущее значение на соответствие типа данных
        super().assertIsInstance(model_entry.__dict__[col_name], int)

        # Сохраняем исходное значение
        starting_value = model_entry.__dict__[col_name]

        # Проверяем можно ли вписать строку в указанное поле. Использование
        # чисел даже в виде строк без дополнительных символов не допускается.
        # Они будут конвертированы в числа на уровне БД.
        for char in ['a', '/', '*', 'pr1vet']:
            with super().assertRaises(sqlalchemy.exc.DataError):
                try:
                    # Обновляем поле вставляя строку.
                    db.session.query(model).filter_by(**filter_query).update({
                        col_name: char
                    })

                    # В случае успеха возвращаем исходное значение.
                    db.session.query(model).filter_by(**filter_query).update({
                        col_name: starting_value
                    })

                # Так как поле должно принимать только int будет выброшена
                # ошибка sqlalchemy.exc.DataError, обрабатываем ее путем отката
                # изменений. После бросаем ее же что бы тест прошел хорошо.
                except sqlalchemy.exc.DataError:
                    db.session.rollback()
                    raise
        
    def is_str(self, model, col_name, col_value):
        '''Проверяем указанное поле на str'''

        filter_query = {col_name:col_value}
        model_entry = db.session.query(model).filter_by(**filter_query).first()

        # Проверяем текущее значение на соответствие типа данных
        self.assertIsInstance(model_entry.__dict__[col_name], str)

        # Сохраняем исходное значение.
        starting_value = model_entry.__dict__[col_name]

        short_strings = [
            'ThisIsMyRifle',
            'ThisIsMyGun',
            'ThisIsForFight',
            'AndThisIsForFun'
        ]
        for short_string in short_strings:
            # Пробуем имена меньше 40 символов.
            db.session.query(model).filter_by(**filter_query).update({
                col_name: short_string
            })
        
        # Возвращаем исходное значение.
        db.session.query(model).filter_by(**filter_query).update({
            col_name: starting_value
        })

        long_strings = [
            'ThisIsmyRifleThisIsMyGun,ThisIsForFightAndThisIsForFun',
            'ThisIsMyLongestNicknameIHaveEverCameUpWith'
        ]

        for long_string in long_strings:
            with self.assertRaises(sqlalchemy.exc.DataError):
                try:
                    # Пробуем строки больше 40 символов.
                    db.session.query(model).filter_by(**filter_query).update({
                        col_name: long_string
                    })

                    # В случае успеха возвращаем исходное значение.
                    db.session.query(model).filter_by(**filter_query).update({
                        col_name: starting_value
                    })

                except sqlalchemy.exc.DataError:
                    db.session.rollback()
                    raise

    def is_bool(self):
        pass

    def is_nullable(self):
        pass

    def is_uuid_v4(self, model, col_name, col_value):

        filter_query = {col_name:col_value}
        model_entry = db.session.query(model).filter_by(**filter_query).first()

        pattern = '[0-9A-F]{8}-[0-9A-F]{4}-[4][0-9A-F]{3}-[89AB][0-9A-F]{3}-[0-9A-F]{12}$'
        super().assertRegex(str(model_entry.__dict__[col_name]).upper(), pattern)






# ------ Модели ---------------------------------------------------------------
class TestUser(ModelTestCase):
    '''Тесты класса User'''

    params = [
        {
            'id': 1,
            'nickname': 'TestUser01',
            'is_persistent': True
        },
        {
            'id': 2,
            'nickname': 'TestUser02',
            'is_persistent': True
        }
    ]
    
    def test_id(self, param=params[0]):
        self.is_int(model=User, col_name='id', col_value=param['id'])

    
    def test_nickname(self, param=params[0]):
        self.is_str(model=User, col_name='nickname', col_value=param['nickname'])

    def test_is_persistent(self):
        # self.is_bool(...)
        pass

    def test_relations(self):
        # ???
        pass

    def test_create_user(self, params=params):
        '''Тестируем возможность создать пользователя.'''

        for param in params:
            # Удаляем существующего пользователя
            db.session.query(User).filter_by(id = param['id']).delete()
            db.session.commit()

            # Создаем нового пользователя
            new_user = User(
                id=param['id'],
                nickname=param['nickname'],
                is_persistent=param['is_persistent']
            )
            db.session.add(new_user)
            db.session.commit()

            # new_user = db.session.query(User).filter_by(id = param['id']).first()

            self.assertEqual(new_user.id, param['id'])
            self.assertEqual(new_user.nickname, param['nickname'])
            self.assertEqual(new_user.is_persistent, param['is_persistent'])




class TestRoom(ModelTestCase):

    params = {
        'id': 1,
        'nickname': 'TestUser02',
        'is_persistent': True,
        'room_uuid': '87c4a4db-90ad-4d34-9ba1-50bfa3496323'
    }

    # --------------- Тесты свойств ---------------
    def test_id(self, params=params):
        self.is_int(model=Room, col_name='id', col_value=params['id'])
        # nullable?
    
    def test_room_uuid(self, params=params):
        self.is_uuid_v4(model=Room, col_name='room_uuid', col_value=params['room_uuid'])

    def test_current_user_id(self):
        pass

    def test_current_step_id(self):
        pass

    def test_seed(self):
        pass

    def test_relations(self):
        # ???
        pass

    # --------------- Тесты методов ---------------

    def test_create_room(self):
        Room.create_room(seed=1, current_step_id=1)

    def test_init_current_user(self):
        pass

    def test_next_step(self):
        pass

    def test_create_result(self, params=params):
        pass

    def test_update_result(self):
        pass

    """ Методы под вопросом существования.
    def get_result(self, params=params):
        pass

    def get_results(self):
        pass
    """



class TestMapChoice(unittest.TestCase):
    '''Тестируем MapChoice класс'''

    # Тестируем поля таблицы
    def test_map_choice(self):

        id = 1
        result_id = 1
        object_id = 1
        action_id = 2

        map_choice = Map_choice()

        map_choice.id = id
        map_choice.result_id = result_id
        map_choice.object_id = object_id
        map_choice.action_id = action_id

        # Создаем запись.
        db.session.add(map_choice)
        db.session.commit()

        # Проверяем запись в таблице на соответствие
        self.assertEqual(map_choice.id, id)
        self.assertEqual(map_choice.result_id, result_id)
        self.assertEqual(map_choice.object_id, object_id)
        self.assertEqual(map_choice.action_id, action_id)

        # Удаляем созданную запись.
        db.session.delete(
            db.session.query(Map_choice).filter(Map_choice.id == id).first()
        )
        db.session.commit()




# ------ Функции --------------------------------------------------------------

class TestFunctions(unittest.TestCase):
    '''Тестируем функции'''

    params = {
        "nickname": "TestUser02",
        "room_uuid": "87c4a4db-90ad-4d34-9ba1-50bfa3496323"
    }

    def test_join_room(self):
        pass



# ------ Запуск тестов --------------------------------------------------------

if __name__ == '__main__':
    unittest.main()
