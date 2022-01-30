import unittest
import requests

from main import app


# ------ Маршруты APP ---------------------------------------------------------

class RouteHome(unittest.TestCase):
    """ Тестирует домашнюю страницу """

    def test_home(self):
        tester = app.test_client(self)
        response = tester.get('/', content_type='html/text')
        self.assertEqual(response.status_code, 200)

    def test_home_content(self):
        tester = app.test_client(self)
        response = tester.get('/', content_type='html/text')
        self.assertTrue(b'hello world' in response.data)

class RouteCreate(unittest.TestCase):
    """ Тестирует форму создания комнаты """

    def test_create(self):
        tester = app.test_client(self)
        response = tester.get('/create', content_type='html/text')
        self.assertEqual(response.status_code, 200)

    def test_create_content(self):
        tester = app.test_client(self)
        response = tester.get('/create', content_type='html/text')
        self.assertTrue(b'Create match' in response.data)

class RouteJoin(unittest.TestCase):
    """ Тестирует форму подключения к комнате """

    def test_join(self):
        tester = app.test_client(self)
        response = tester.get('/123412341234/join', content_type='html/text')
        self.assertEqual(response.status_code, 200)

    def test_join_content(self):
        tester = app.test_client(self)
        response = tester.get('/123412341234/join', content_type='html/text')
        self.assertTrue(b'Join match' in response.data)



# ------ Маршруты API ---------------------------------------------------------

class TestAPI(unittest.TestCase):
    '''Тестируем API endpoint'ы'''
    
    URI = 'http://localhost:5000/api'

    def test_greet(self):
        json = {
            "jsonrpc": "2.0",
            "method": "app.greet",
            "params": {},
            "id": 1
        }
        headers = {
            "Content-Type": "application/json",
        }

        response = requests.post(self.URI, json=json, headers=headers)
        response.raise_for_status()
        r = response.json()
        self.assertEqual(r, {'id': 1, 'jsonrpc': '2.0', 'result': 'Welcome to Flask JSON-RPC'})

if __name__ == '__main__':
    unittest.main()
