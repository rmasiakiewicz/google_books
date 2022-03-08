import json
import re
import urllib.parse
from datetime import datetime
from typing import List, Tuple, Optional, Generator

import requests

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
) -> Tuple[List[Optional[Book]], List[Optional[Author]], dict, int]:
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
    google_json: dict, imported_gid: List[str], authors_by_name: dict
) -> Tuple[List[Optional[Book]], List[Optional[Author]], dict]:
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
