import os


class Config:
    SECRET_KEY = "I_am_very_secret"
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class TestingConfig(Config):
    SQLALCHEMY_DATABASE_URI = (
        "postgresql://sdawxqghbuigjs:9a742e28c8afeb5417506f0c1599f3c93444b1748d7062e5320228"
        "4a43ee7e28@ec2-34-206-148-196.compute-1.amazonaws.com:5432/d9i6b43829kk3l"
    )
    TESTING = True
    TRAP_BAD_REQUEST_ERRORS = True
    WTF_CSRF_ENABLED = False


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get("SQLALCHEMY_DATABASE_URI")


config = {"production": ProductionConfig, "testing": TestingConfig}
