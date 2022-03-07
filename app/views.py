import json
import os
import re
import urllib.parse
from datetime import datetime
from http import HTTPStatus
from typing import List, Optional

import requests
from flask import Blueprint, request, render_template, redirect, url_for, flash

from app import db
from app.models import Book, Author, Language
from app.utils import group_by

blueprint = Blueprint("general", __name__)


@blueprint.route("/health_check", methods=["GET"])
def health_check():
    status = {"status": "ok", "deployment": "local"}
    release_version = os.environ.get("HEROKU_RELEASE_VERSION")
    status["deployment"] = "heroku" if release_version else "local"
    status["release_version"] = release_version or "n/a"
    return status, HTTPStatus.OK


@blueprint.route("/", methods=["GET"])
def index():
    return render_template("index.html")


@blueprint.route("/books", methods=["GET"])
def books_list():
    title = request.args.get("title")
    author = request.args.get("title")
    language = request.args.get("language")
    from_date = request.args.get("from_date")
    to_date = request.args.get("to_date")
    # books = Book.query.select_all()
    return render_template("books_list.html")


@blueprint.route("/books/add", methods=["POST"])
def add_book():
    pass


@blueprint.route("/books/import", methods=["GET", "POST"])
def import_books():
    if request.method == "GET":
        return render_template("import_books.html")
    # allowed_form_names = ["q", "intitle", 'inauthor', "inpublisher", "subject", "isbn", "lccn", "oclc"]
    query = request.form.get("q")
    if query is None:
        return "Unauthorized", HTTPStatus.UNAUTHORIZED
    authors_by_name = group_by(lambda x: x.name.lower(), Author.query.all())
    languages_by_name = group_by(lambda x: x.name.lower(), Language.query.all())
    already_imported_books_gid = [book.gid for book in Book.query.all()]
    total_items = get_google_data(query, 0, already_imported_books_gid, authors_by_name, languages_by_name)
    total_items -= 40
    pagination_index = 40
    while total_items > 0:
        get_google_data(query, pagination_index, already_imported_books_gid, authors_by_name, languages_by_name)
        total_items -= 40
        pagination_index += 40
    flash("New books have been imported", 'success')
    return redirect(url_for('general.books_list'))


def get_google_data(
        query: str, start_index: int, imported_gid: List[str], authors_by_name: dict, languages_by_name: dict) -> int:
    google_response = requests.get(
        "https://www.googleapis.com/books/v1/volumes?q={}&maxResults=40&startIndex={}".format(
            urllib.parse.quote_plus(query), start_index))
    google_json = json.loads(google_response.content)
    parse_google_json(google_json, imported_gid, authors_by_name, languages_by_name)
    return google_json.get("totalItems")


def parse_google_json(
        google_json: dict, imported_gid: List[str], authors_by_name: dict, languages_by_name: dict) -> None:
    for item in google_json.get("items", []):
        gid = item.get("id")
        if gid in imported_gid:
            continue
        item = item.get("volumeInfo")
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
        raw_language = item.get("language").lower()
        language = languages_by_name.get(raw_language)
        if language is None:
            language = Language(name=raw_language)
            db.session.add(language)
            db.session.commit()
            languages_by_name[raw_language] = language
        isbn_10 = None
        isbn_13 = None
        for industry_identifier in item.get("industryIdentifiers", []):
            if industry_identifier.get("type") == "ISBN_10":
                isbn_10 = industry_identifier.get("identifier")
            elif industry_identifier.get("type") == "ISBN_13":
                isbn_13 = industry_identifier.get("identifier")
        book = Book(
            gid=gid,
            title=item.get("title"),
            publication_date=publication_date,
            number_of_pages=item.get("pageCount"),
            language_id=language.id,
            preview_link=item.get("previewLink"),
            isbn_10=isbn_10,
            isbn_13=isbn_13,
        )
        db.session.add(book)
        new_authors = []
        existed_authors = []
        for item_author in item.get("authors", []):
            author = authors_by_name.get(item_author.lower())
            if author is None:
                author = Author(name=item_author)
                new_authors.append(author)
                authors_by_name[item_author.lower()] = author
                continue
            existed_authors.append(author)
        db.session.add_all(new_authors)
        db.session.commit()
        book.authors.extend(new_authors + existed_authors)
        imported_gid.append(book.gid)
    return None
