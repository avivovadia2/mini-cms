import os


class Config:
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", "postgresql+psycopg2://localhost:5432/mini_cms"
    )
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-only-secret")
