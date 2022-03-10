import datetime
from dataclasses import dataclass
from typing import List, Optional

from sqlalchemy.orm import relationship

from app import db


@dataclass(init=False)
class Author(db.Model):
    name: str

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)

    books = relationship("Book", secondary="book_author", back_populates="authors")


@dataclass(init=False)
class Book(db.Model):
    gid: int
    title: str
    publication_date: Optional[datetime.datetime]
    number_of_pages: Optional[int]
    language: str
    image_link: Optional[str]
    isbn_10: Optional[str]
    isbn_13: Optional[str]
    authors: Optional[List[Author]]

    id = db.Column(db.Integer, primary_key=True)
    gid = db.Column(db.String(50), nullable=False, unique=True)
    title = db.Column(db.String(300), nullable=False)
    publication_date = db.Column(db.DateTime, nullable=True)
    number_of_pages = db.Column(db.Integer, nullable=True)
    language = db.Column(db.String(10), nullable=False)
    image_link = db.Column(db.String(400), nullable=True)
    isbn_10 = db.Column(db.String(10), nullable=True, unique=True)
    isbn_13 = db.Column(db.String(13), nullable=True, unique=True)

    authors = relationship("Author", secondary="book_author", back_populates="books")


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
