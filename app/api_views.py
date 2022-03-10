from http import HTTPStatus

from flask import Blueprint, request, jsonify

from app.utils import build_query

api_blueprint = Blueprint("api", __name__)


@api_blueprint.route("/v1/books", methods=["GET"])
def books_list():
    allowed_parameters = ["title", "author", "language", "from_date", "to_date", "page", "per_page"]
    for key in request.args.keys():
        if key not in allowed_parameters:
            return jsonify(
                error=True,
                message="Unexpected query string: %s" % key,
                items=[]
            ), HTTPStatus.UNAUTHORIZED
    page = request.args.get("page", 1, int)
    per_page = request.args.get("per_page", 20, int)
    query_string = dict(request.args)
    query_string.pop("page", None)
    query_string.pop("per_page", None)
    builder = build_query(query_string, api_request=True)
    if builder is None:
        return jsonify(
            error=True,
            message="Bad date format, expected YYYY-MM-DD",
            items=[]
        ), HTTPStatus.BAD_REQUEST
    data = builder.paginate(page=page, per_page=per_page)
    return jsonify(
        error=False,
        message="ok",
        items=data.items,
        total_items=data.total
    ), HTTPStatus.OK
