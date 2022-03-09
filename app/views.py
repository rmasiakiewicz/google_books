import logging
import math
import os
from datetime import datetime
from http import HTTPStatus

from flask import Blueprint, request, render_template, redirect, url_for, flash

from app import db
from app.forms import BookForm
from app.models import Book, Author
from app.utils import chunks, get_google_data, build_query

blueprint = Blueprint("general", __name__)
logging.basicConfig(level=logging.DEBUG)


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
    page = request.args.get("page", 1, int)
    query_string = dict(request.args)
    query_string.pop("page", None)
    builder = build_query(query_string)
    if builder is None:
        return "Bad date format", HTTPStatus.UNAUTHORIZED
    books = builder.paginate(page=page, per_page=20)
    authors_str_by_id = {}
    for book in books.items:
        authors_string = ", ".join([author.name for author in book.authors])
        authors_str_by_id[book.id] = authors_string
    next_url = (
        url_for("general.books_list", page=books.next_num, **query_string)
        if books.has_next
        else None
    )
    previous_url = (
        url_for("general.books_list", page=books.prev_num, **query_string)
        if books.has_prev
        else None
    )
    return render_template(
        "books_list.html",
        books=books,
        authors_by_id=authors_str_by_id,
        page_number=page,
        last_page=books.pages,
        author=request.args.get("author", ""),
        language=request.args.get("language", ""),
        title=request.args.get("title", ""),
        from_date=request.args.get("from_date", ""),
        to_date=request.args.get("to_date", ""),
        next_url=next_url,
        previous_url=previous_url,
    )


@blueprint.route("/books/add", methods=["POST"])
def add_book():
    pass


@blueprint.route("/books/edit/<int:book_id>", methods=["GET", "POST"])
def edit_book(book_id):
    form = BookForm()
    book = Book.query.filter(Book.id == book_id).one_or_none()
    if not book:
        return "Bad request", HTTPStatus.BAD_REQUEST
    form.gid.data = book.gid
    form.title.data = book.title
    form.authors.data = ", ".join([author.name for author in book.authors])
    form.publication_date.data = book.publication_date if book.publication_date else None
    form.number_of_pages.data = book.number_of_pages
    form.language.data = book.language
    form.image_link.data = book.image_link
    form.isbn_10.data = book.isbn_10
    form.isbn_13.data = book.isbn_13
    if request.method == "GET":
        return render_template("edit_book.html", form=form, book_id=book_id)
    if not form.validate_on_submit():
        flash("Something went wrong", "danger")
        return render_template("edit_book.html", form=form, book_id=book_id)
    new_gid = request.form.get("gid")
    if Book.query.filter(Book.gid == new_gid).one_or_none() is not None and new_gid != book.gid:
        flash("Selected gid is taken, please choose another one", "danger")
        return render_template("edit_book.html", form=form, book_id=book_id)
    book.gid = new_gid
    book.title = request.form.get("title")
    book.publication_date = (
        datetime.strptime(request.form.get("publication_date"), "%Y/%m/%d")
        if request.form.get("publication_date")
        else None
    )
    book.number_of_pages = request.form.get("number_of_pages")
    book.language = request.form.get("language")
    book.image_link = request.form.get("image_link")
    book.isbn_10 = request.form.get("isbn_10")
    book.isbn_13 = request.form.get("isbn_13")
    authors_string = request.form.get("authors", "")
    if authors_string == "" and len(book.authors) == 0:
        db.session.commit()
        flash("Book has been edited", "success")
        return redirect(url_for("general.books_list"))
    old_authors_by_names = {author.name.lower(): author for author in book.authors}
    new_authors = [author.strip().lower() for author in authors_string.split(",")]
    missing_old_authors = [
        old_authors_by_names.get(n)
        for n in list(set(old_authors_by_names.keys() - set(new_authors)))
    ]
    for missing_author in missing_old_authors:
        book.authors.remove(missing_author)
    for author in authors_string.split(","):
        name = author.strip().lower()
    return render_template("edit_book.html", form=form, book_id=book_id)


@blueprint.route("/books/import", methods=["GET", "POST"])
def import_books():
    if request.method == "GET":
        return render_template("import_books.html")
    query = request.form.get("q")
    if query is None:
        return "Unauthorized", HTTPStatus.UNAUTHORIZED
    authors_by_name = {author.name.lower(): author for author in Author.query.all()}
    already_imported_books_gid = [book.gid for book in Book.query.all()]
    new_books, new_authors, book_authors_by_gid, total_items = get_google_data(
        query, 0, already_imported_books_gid, authors_by_name
    )
    logging.info(
        "Found {} items, there should be around {} pages".format(
            total_items, math.ceil(total_items / 40)
        )
    )
    logging.info("Page 1 done, scraped books {}".format(len(new_books)))
    total_items -= 40
    pagination_index = 40
    page = 2
    while total_items > 0:
        (
            next_page_new_books,
            next_page_new_authors,
            next_page_book_authors_by_gid,
            _,
        ) = get_google_data(
            query, pagination_index, already_imported_books_gid, authors_by_name
        )
        new_books.extend(next_page_new_books)
        new_authors.extend(next_page_new_authors)
        logging.info(
            "Page {} done, scraped books {}".format(page, len(next_page_new_books))
        )
        book_authors_by_gid.update(next_page_book_authors_by_gid)
        total_items -= 40
        pagination_index += 40
        page += 1
    for rows_chunk in chunks(new_books + new_authors, 500):
        db.session.add_all(rows_chunk)
        db.session.commit()
    new_books_by_gid = {book.gid: book for book in new_books}
    for gid, authors in book_authors_by_gid.items():
        book = new_books_by_gid.get(gid)
        book.authors.extend(authors)
    db.session.commit()
    logging.info("Imported {} new books".format(len(new_books)))
    flash("New books have been imported", "success")
    return redirect(url_for("general.books_list"))
