import unittest
from database import Objects, create_room, delete_room



# ------------- Переменные -------------
MAPS_IN_SEASON = 7 # количество карт в сезоне.




# ------------- Таблицы -------------
class TableObjects(unittest.TestCase):
    """ Тестирует таблицу Objects """

    def test_objects_count(self):
        ''' Проверяем количество записей в таблице '''
        objects_list = Objects.query.all()
        current_season_objects = []
        for obj in objects_list:
            if obj.rel_current_season != []:
                current_season_objects.append(obj.rel_current_season)
            
        self.assertEqual(len(current_season_objects), MAPS_IN_SEASON)


# ------------- Функции -------------
class FunctionCreateRoom(unittest.TestCase):
    ''' Тестируем функцию полного цикла создания комнаты '''
    user = {
        "nickname": 'testuser',
        "game_mode": 1,
        "bo_type": 1,
        "seed": 1
    }

    def test_create_room(self, u=user):
        global entries
        entries = create_room(u['nickname'], u['game_mode'], u['bo_type'], u['seed'])
        if 'room_id' in entries and 'user_id' in entries and 'results_id' in entries and len(entries.keys()) == 3:
            result = True
        else:
            result = False
        self.assertEqual(result, True)

    def test_delete_room(self):
        result = delete_room(entries['room_id'], entries['user_id'], entries['results_id'])
        self.assertEqual(result, True)
        

if __name__ == '__main__':
    unittest.main()