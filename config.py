import os


class Config:
    SECRET_KEY = "I_am_very_secret"
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class TestingConfig(Config):
    SQLALCHEMY_DATABASE_URI = ""
    TESTING = True
    TRAP_BAD_REQUEST_ERRORS = True
    WTF_CSRF_ENABLED = False


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get("SQLALCHEMY_DATABASE_URI")


config = {"production": ProductionConfig, "testing": TestingConfig}
