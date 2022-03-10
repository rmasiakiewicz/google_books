import unittest

from app import create_app, db
from app.models import Book, Author


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

    def test_import_books(self):
        response = self.client.post("/books/import", data={"q": "tolkien"}, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"New books have been imported", response.data)

    def test_books_list(self):
        response = self.client.get("/books")
        self.assertEqual(response.status_code, 200)
        self.assertGreater(response.content_length, 1000)

    def test_add_new_book_no_authors(self):
        response = self.client.post(
            "/book/add", data=dict(gid="12345", title="test book", language="pl", authors=""), follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Book has been added", response.data)

    def test_add_new_book_with_authors(self):
        author = Author(name="Jan Kowalski")
        db.session.add(author)
        db.session.commit()
        response = self.client.post(
            "/book/add", data=dict(gid="12345", title="test book", language="pl", authors="Jan Kowalski, Piotr Nowak"),
            follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Book has been added", response.data)

    def test_add_new_book_missing_required_field_fail(self):
        response = self.client.post(
            "/book/add", data=dict(gid="12345", language="pl", authors=""), follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Something went wrong", response.data)

    def test_add_another_book_with_same_gid_fail(self):
        self.client.post("/book/add", data=dict(gid="12345", language="pl", title="book 1", authors=""), follow_redirects=True)
        response = self.client.post(
            "/book/add", data=dict(gid="12345", language="pl", title="book 2", authors=""), follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Selected gid is taken, please choose another one", response.data)

    def test_edit_book_success(self):
        book = Book(gid="1234", title="book 1", language="pl")
        db.session.add(book)
        db.session.commit()
        response = self.client.post(
            "/book/edit/{}".format(book.id),
            data=dict(gid=book.gid, title="book 2", language=book.language, authors=""),
            follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(book.title, "book 2")
        self.assertIn(b"Book has been edited", response.data)

