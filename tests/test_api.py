import unittest

from app import create_app, db


class ApiTestCase(unittest.TestCase):

    def setUp(self) -> None:
        self.app = create_app("testing")
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.client = self.app.test_client()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_import_books(self):
        response = self.client.post('/books/import', data={"q": "tolkien"})
        self.assertEqual(response.status_code, 200)
