import os
from http import HTTPStatus

from flask import Blueprint, request, render_template, redirect, url_for, flash

from app import db
from app.forms import BookForm
from app.models import Book, Author
from app.utils import chunks, get_google_data, build_query, get_book_authors_from_form, none_if_empty

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
    return redirect(url_for("general.books_list"))


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


@blueprint.route("/book/add", methods=["GET", "POST"])
def add_book():
    form = BookForm()
    if request.method == "GET":
        return render_template("add_book.html", form=form)
    if not form.validate_on_submit():
        flash("Something went wrong", "danger")
        return render_template("add_book.html", form=form)
    gid = form.gid.data
    if Book.query.filter(Book.gid == gid).one_or_none() is not None:
        flash("Selected gid is taken, please choose another one", "danger")
        return render_template("add_book.html", form=form)
    book = Book(
        gid=gid,
        title=form.title.data,
        publication_date=form.publication_date.data,
        number_of_pages=form.number_of_pages.data,
        language=form.language.data,
        image_link=none_if_empty(form.image_link.data),
        isbn_10=none_if_empty(form.isbn_10.data),
        isbn_13=none_if_empty(form.isbn_13.data),
    )
    db.session.add(book)
    authors_string = form.authors.data
    if authors_string == "":
        db.session.commit()
        flash("Book has been added", "success")
        return redirect(url_for("general.books_list"))
    new_authors = get_book_authors_from_form(authors_string, db)
    book.authors.extend(new_authors)
    db.session.commit()
    flash("Book has been added", "success")
    return redirect(url_for("general.books_list"))


@blueprint.route("/book/edit/<int:book_id>", methods=["GET", "POST"])
def edit_book(book_id):
    form = BookForm()
    book = Book.query.filter(Book.id == book_id).one_or_none()
    if not book:
        return "Bad request", HTTPStatus.BAD_REQUEST
    if request.method == "GET":
        form.gid.data = book.gid
        form.title.data = book.title
        form.authors.data = ", ".join([author.name for author in book.authors])
        form.publication_date.data = book.publication_date if book.publication_date else None
        form.number_of_pages.data = book.number_of_pages
        form.language.data = book.language
        form.image_link.data = book.image_link
        form.isbn_10.data = book.isbn_10
        form.isbn_13.data = book.isbn_13
        return render_template("edit_book.html", form=form, book_id=book_id)
    if not form.validate_on_submit():
        flash("Something went wrong", "danger")
        return render_template("edit_book.html", form=form, book_id=book_id)
    new_gid = form.gid.data
    if Book.query.filter(Book.gid == new_gid).one_or_none() is not None and new_gid != book.gid:
        flash("Selected gid is taken, please choose another one", "danger")
        return render_template("edit_book.html", form=form, book_id=book_id)
    book.gid = new_gid
    book.title = form.title.data
    book.publication_date = form.publication_date.data
    book.number_of_pages = form.number_of_pages.data
    book.language = form.language.data
    book.image_link = none_if_empty(form.image_link.data)
    book.isbn_10 = none_if_empty(form.isbn_10.data)
    book.isbn_13 = none_if_empty(form.isbn_13.data)
    authors_string = form.authors.data
    if authors_string == "" and len(book.authors) == 0:
        db.session.commit()
        flash("Book has been edited", "success")
        return redirect(url_for("general.books_list"))
    new_authors = get_book_authors_from_form(authors_string, db)
    book.authors.extend(new_authors)
    db.session.commit()
    flash("Book has been edited", "success")
    return redirect(url_for("general.books_list"))


@blueprint.route("/books/import", methods=["GET", "POST"])
def import_books():
    if request.method == "GET":
        return render_template("import_books.html")
    query = request.form.get("q")
    authors_by_name = {author.name.lower(): author for author in Author.query.all()}
    already_imported_books_gid = [book.gid for book in Book.query.all()]
    new_books, new_authors, book_authors_by_gid, total_items = get_google_data(
        query, 0, already_imported_books_gid, authors_by_name
    )
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
    flash("New books have been imported", "success")
    return redirect(url_for("general.books_list"))
