from sqlalchemy.orm import relationship

from app import db


class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    publication_date = db.Column(db.DateTime, nullable=False)
    number_of_pages = db.Column(db.Integer, nullable=False)
    language_id = db.Column(db.Integer, db.ForeignKey("language.id"), nullable=False)
    preview_link = db.Column(db.String(100), nullable=True)
    isbn_10 = db.Column(db.String(10), nullable=True)
    isbn_13 = db.Column(db.String(13), nullable=True)

    language = relationship("Language")
    authors = relationship("Author", secondary="book_author", back_populates="books")


class Author(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

    books = relationship("Book", secondary="book_author", back_populates="authors")


class Language(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)


book_author = db.Table(
    "book_author",
    db.Column(
        "author_id",
        db.Integer,
        db.ForeignKey("author.id"),
        primary_key=True,
    ),
    db.Column(
        "book_id",
        db.Integer,
        db.ForeignKey("book.id"),
        primary_key=True,
    ),
)