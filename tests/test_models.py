import datetime
import unittest
from app import create_app, db
from app.models import Book, Author, Language


class ModelsTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.app = create_app("testing")
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_book_single_author(self):
        language = Language(name="pl")
        db.session.add(language)
        db.session.commit()
        author = Author(name="Jan Kowalski")
        db.session.add(author)
        db.session.commit()
        book = Book(
            title="abcd",
            publication_date=datetime.datetime.utcnow(),
            number_of_pages=100,
            language_id=language.id,
            isbn_10="1111111111",
        )
        db.session.add(book)
        db.session.commit()
        book.authors.append(author)
        self.assertEqual(book.language.name, "pl")
        self.assertEqual(book.number_of_pages, 100)
        self.assertEqual(book.title, "abcd")
        self.assertEqual(book.isbn_10, "1111111111")
        self.assertListEqual(book.authors, [author])

    def test_book_multiple_authors(self):
        language = Language(name="pl")
        db.session.add(language)
        db.session.commit()
        author1 = Author(name="Jan Kowalski")
        author2 = Author(name="Rafał Masiakiewicz")
        db.session.add(author1)
        db.session.add(author2)
        db.session.commit()
        book = Book(
            title="abcd",
            publication_date=datetime.datetime.utcnow(),
            number_of_pages=100,
            language_id=language.id,
            isbn_10="1111111111",
        )
        db.session.add(book)
        db.session.commit()
        book.authors.extend([author1, author2])
        self.assertListEqual(book.authors, [author1, author2])

    def test_author_multiple_books(self):
        language = Language(name="pl")
        db.session.add(language)
        db.session.commit()
        author = Author(name="Jan Kowalski")
        db.session.add(author)
        db.session.commit()
        book1 = Book(
            title="abcd",
            publication_date=datetime.datetime.utcnow(),
            number_of_pages=100,
            language_id=language.id,
            isbn_10="1111111111",
        )
        book2 = Book(
            title="ddddd",
            publication_date=datetime.datetime.utcnow(),
            number_of_pages=100,
            language_id=language.id,
            isbn_10="2222222222",
        )
        db.session.add(book1)
        db.session.add(book2)
        db.session.commit()
        author.books.extend([book1, book2])
        self.assertEqual(len(author.books), 2)
