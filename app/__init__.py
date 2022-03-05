from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from config import config

db = SQLAlchemy()


def create_app(config_type='production'):
    app = Flask(__name__)

    config_class = config.get(config_type)
    app.config.from_object(config_class)

    db.init_app(app)

    from app.views import blueprint
    app.register_blueprint(blueprint)

    return app
