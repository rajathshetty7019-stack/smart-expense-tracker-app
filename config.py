import os


class Config:
    """Application configuration."""

    SECRET_KEY = os.environ.get(
        "SECRET_KEY",
        "dev-secret-key-change-this-later"
    )

    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        "sqlite:///expense_tracker.db"
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False