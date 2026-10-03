"""Application configuration for all environments."""

import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    """Base configuration."""
    SECRET_KEY = os.environ.get("SECRET_KEY", os.urandom(32).hex())
    DATABASE_PATH = os.path.join(basedir, "database.db")
    DATASET_PATH = os.path.join(basedir, "dataset", "Superstore.csv")
    UPLOAD_FOLDER = os.path.join(basedir, "uploads")
    EXPORT_FOLDER = os.path.join(basedir, "exports")
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024
    SESSION_TYPE = "filesystem"
    LOG_LEVEL = "INFO"


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False
    SECRET_KEY = os.environ.get("SECRET_KEY", "change-me-in-production")


class TestingConfig(Config):
    TESTING = True
    DATABASE_PATH = os.path.join(basedir, "test_database.db")


config_by_name = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
}
