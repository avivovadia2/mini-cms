import os


class Config:
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", "postgresql+psycopg2://localhost:5432/mini_cms"
    )
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-only-secret")


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "TEST_DATABASE_URL", "postgresql+psycopg2://localhost:5432/mini_cms_test"
    )
    SECRET_KEY = "test-secret"
