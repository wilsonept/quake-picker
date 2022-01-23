import unittest
from database import Objects



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







if __name__ == '__main__':
    unittest.main()