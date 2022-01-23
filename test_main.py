import unittest
from main import app
from database import db


# ------------------------------
# Маршруты
# ------------------------------
class RouteHome(unittest.TestCase):
    """A base test case for flask-tracking."""

    def test_home(self):
        tester = app.test_client(self)
        response = tester.get('/', content_type='html/text')
        self.assertEqual(response.status_code, 200)

    def test_home_content(self):
        tester = app.test_client(self)
        response = tester.get('/', content_type='html/text')
        self.assertTrue(b'hello world' in response.data)

class RouteCreate(unittest.TestCase):
    """A base test case for flask-tracking."""

    def test_create(self):
        tester = app.test_client(self)
        response = tester.get('/create', content_type='html/text')
        self.assertEqual(response.status_code, 200)

    def test_create_content(self):
        tester = app.test_client(self)
        response = tester.get('/create', content_type='html/text')
        self.assertTrue(b'Create match' in response.data)

class RouteJoin(unittest.TestCase):
    """A base test case for flask-tracking."""

    def test_join(self):
        tester = app.test_client(self)
        response = tester.get('/123412341234/join', content_type='html/text')
        self.assertEqual(response.status_code, 200)

    def test_join_content(self):
        tester = app.test_client(self)
        response = tester.get('/123412341234/join', content_type='html/text')
        self.assertTrue(b'Join match' in response.data)




if __name__ == '__main__':
    unittest.main()