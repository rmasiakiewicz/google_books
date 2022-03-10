import unittest

from app import create_app, db


class AppTestCase(unittest.TestCase):
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

    def test_api_response_no_query_strings(self):
        response = self.client.get("/v1/books")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.is_json)
        self.assertFalse(response.json["error"])

    def test_api_response_with_allowed_query_strings(self):
        response = self.client.get(
            "/v1/books?title=a&author=b&&language=c&from_date=2000-10-10&to_date=2001-10-10"
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.is_json)
        self.assertFalse(response.json["error"])

    def test_api_response_with_not_allowed_query_string(self):
        response = self.client.get("/v1/books?abc=bcd")
        self.assertEqual(response.status_code, 401)
        self.assertTrue(response.is_json)
        self.assertTrue(response.json["error"])

    def test_api_response_bad_date_format(self):
        response = self.client.get("/v1/books?from_date=2000/10/10")
        self.assertEqual(response.status_code, 400)
        self.assertTrue(response.is_json)
        self.assertTrue(response.json["error"])
