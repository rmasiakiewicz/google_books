import os
from http import HTTPStatus

from flask import Blueprint

blueprint = Blueprint("general", __name__)


@blueprint.route("/health_check", methods=["GET"])
def health_check():
    status = {"status": "ok", "deployment": "local"}
    release_version = os.environ.get("HEROKU_RELEASE_VERSION")
    status["deployment"] = "heroku" if release_version else "local"
    status["release_version"] = release_version or "n/a"
    return status, HTTPStatus.OK
