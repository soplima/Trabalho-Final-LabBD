import os


class Config:
    SQLALCHEMY_DATABASE_URI = "postgresql://admin:admin@localhost:5432/spotify_db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
