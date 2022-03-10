from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from config import config

db = SQLAlchemy()
migrate = Migrate(compare_type=True)

from app import models


def create_app(config_type="production"):
    app = Flask(__name__)

    config_class = config.get(config_type)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)

    from app.views import blueprint
    from app.api_views import api_blueprint

    app.register_blueprint(blueprint)
    app.register_blueprint(api_blueprint)

    return app
