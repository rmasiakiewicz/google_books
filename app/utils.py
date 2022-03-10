import datetime
import json
import re
import urllib.parse
from datetime import datetime
from typing import List, Tuple, Generator, Optional

import requests
import sqlalchemy
from flask_sqlalchemy import SQLAlchemy

from app.models import Author, Book


def chunks(l: list, n: int) -> Generator:
    current_chunk = []
    for i in l:
        current_chunk.append(i)
        if len(current_chunk) == n:
            yield current_chunk
            current_chunk = []
    if len(current_chunk) > 0:
        yield current_chunk


def get_google_data(
    query: str, start_index: int, imported_gid: List[str], authors_by_name: dict
) -> Tuple[List[Book], List[Author], dict, int]:
    google_response = requests.get(
        "https://www.googleapis.com/books/v1/volumes?q={}&maxResults=40&startIndex={}".format(
            urllib.parse.quote_plus(query), start_index
        )
    )
    google_json = json.loads(google_response.content)
    new_books, new_authors, book_authors_by_gid = parse_google_json(
        google_json, imported_gid, authors_by_name
    )
    return new_books, new_authors, book_authors_by_gid, google_json.get("totalItems")


def parse_google_json(
    google_json: dict, imported_gid: List[str], authors_by_name: dict) -> Tuple[List[Book], List[Author], dict]:
    new_books = []
    new_authors = []
    book_authors_by_gid = {}
    for item in google_json.get("items", []):
        gid = item.get("id")
        if gid in imported_gid:
            continue
        item = item.get("volumeInfo")
        title = item.get("title")
        if title is None:
            continue  # empty title example TwlpDwAAQBAJ
        raw_publication_date = item.get("publishedDate")
        if raw_publication_date is None:
            publication_date = None
        elif re.search(r"^\d{4}$", raw_publication_date) is not None:
            publication_date = datetime.strptime(raw_publication_date, "%Y")
        elif re.search(r"^\d{4}-\d{1,2}$", raw_publication_date) is not None:
            publication_date = datetime.strptime(raw_publication_date, "%Y-%m")
        elif re.search(r"^\d{4}-\d{1,2}-\d{1,2}$", raw_publication_date) is not None:
            publication_date = datetime.strptime(raw_publication_date, "%Y-%m-%d")
        else:
            publication_date = None
        language = item.get("language").lower()
        isbn_10 = None
        isbn_13 = None
        for industry_identifier in item.get("industryIdentifiers", []):
            if industry_identifier.get("type") == "ISBN_10":
                isbn_10 = industry_identifier.get("identifier")
            elif industry_identifier.get("type") == "ISBN_13":
                isbn_13 = industry_identifier.get("identifier")
        image_link = item.get("imageLinks", {}).get("thumbnail") or item.get(
            "imageLinks", {}
        ).get("smallThumbnail")
        book = Book(
            gid=gid,
            title=title,
            publication_date=publication_date,
            number_of_pages=item.get("pageCount"),
            language=language,
            image_link=image_link,
            isbn_10=isbn_10,
            isbn_13=isbn_13,
        )
        new_books.append(book)
        book_authors = []
        for item_author in item.get("authors", []):
            author = authors_by_name.get(item_author.lower())
            if author is None:
                author = Author(name=item_author)
                new_authors.append(author)
                authors_by_name[item_author.lower()] = author
            book_authors.append(author)
        book_authors_by_gid[book.gid] = book_authors
        imported_gid.append(book.gid)
    return new_books, new_authors, book_authors_by_gid


def build_query(query_dict: dict, api_request=False):
    allowed_parameters = ["title", "author", "language", "from_date", "to_date"]
    builder = Book.query
    for key in query_dict:
        if key not in allowed_parameters:
            continue
        value = query_dict.get(key)
        if value == "":
            continue
        if key == "author":
            builder = builder.join(Book.authors).filter(
                Author.name.ilike("%" + value + "%")
            )
            continue
        if key == "from_date":
            from_date = check_date(value, api_request)
            if from_date is None:
                return None
            builder = builder.filter(Book.publication_date >= from_date)
            continue
        if key == "to_date":
            to_date = check_date(value, api_request)
            if to_date is None:
                return None
            builder = builder.filter(Book.publication_date <= to_date)
            continue
        builder = builder.filter(getattr(Book, key).ilike("%" + value + "%"))
    return builder


def check_date(raw_date: str, api_request=False) -> datetime.date:
    regex = r"^\d{4}/\d{1,2}/\d{1,2}$"
    date_format = "%Y/%m/%d"
    if api_request:
        regex = r"^\d{4}-\d{1,2}-\d{1,2}$"
        date_format = "%Y-%m-%d"
    if re.search(regex, raw_date) is None:
        return None
    try:
        return datetime.strptime(raw_date, date_format)
    except ValueError:
        return None


def get_book_authors_from_form(authors_string: str, db: SQLAlchemy) -> List[Author]:
    form_authors_by_lower_name = {author.strip().lower(): author.strip() for author in authors_string.split(",")}
    db_authors_by_lower_name = {
        author.name.lower(): author
        for author in Author.query.filter(sqlalchemy.func.lower(Author.name).in_(form_authors_by_lower_name.keys()))
    }
    authors = []
    for key, value in form_authors_by_lower_name.items():
        author = db_authors_by_lower_name.get(key)
        if author is None:
            author = Author(name=value)
            db.session.add(author)
        authors.append(author)
    db.session.commit()
    return authors


def none_if_empty(text: str) -> Optional[str]:
    return None if text == "" else text
