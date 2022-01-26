import unittest
from database import Object, User, Result, Room, delete_room



# ------------- Константы -------------
MAPS_IN_SEASON = 7 # количество карт в сезоне.




# ------------- Таблицы -------------
class TableObject(unittest.TestCase):
    """ Тестирует таблицу Objects """

    def test_objects_count(self):
        ''' Проверяем количество записей в таблице '''
        objects_list = Object.query.all()
        current_season_objects = []
        for obj in objects_list:
            if obj.rel_current_season != []:
                current_season_objects.append(obj.rel_current_season)
            
        self.assertEqual(len(current_season_objects), MAPS_IN_SEASON)


# ------------- Функции -------------
class TestFunctions(unittest.TestCase):
    '''Тестируем функции'''
    
    room_uuid = 'ce351b96-8077-4b0c-b520-676539561313'
    
    def test_delete_room(self, room_uuid=room_uuid):
        result = delete_room(room_uuid)
        self.assertEqual(result, True)

# ------------- Классы -------------
class TestClasses(unittest.TestCase):
    '''Тестируем классы'''

    nickname = 'wilson'
    room_uuid = 'dc3ad9c1-7452-40b6-99a1-e98ddc18a31e'
    room_id = 1

    # тест метода класса User
    def test_get_user(self, nickname=nickname):
        user = User.get_user(nickname)
        self.assertEqual(user.nickname, nickname)

    def test_create_user(self, nickname='Petya'):
        new_user = User.create_user(nickname)
        user = User.get_user(nickname)
        self.assertEqual(user.id, new_user)

    # тест метода класса Room
    def test_get_room(self, room_uuid=room_uuid):
        room = Room.get_room(room_uuid)
        self.assertEqual(room.room_uuid.hex, room_uuid.replace('-',''))

    # тест метода класса Result
    def test_get_result(self, room_id=room_id):
        result = Result.get_result(room_id)
        for item in result:
            self.assertEqual(item.room_id, room_id)



if __name__ == '__main__':
    unittest.main()