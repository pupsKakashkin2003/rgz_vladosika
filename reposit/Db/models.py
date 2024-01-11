from . import db
from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy


class users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), nullable=False, unique=True)
    password = db.Column(db.String(128), nullable=False)
    is_superuser = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f"id:{self.id}, username:{self.username}"

class book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    author = db.Column(db.String(255))
    pages = db.Column(db.Integer, nullable=True)
    publisher = db.Column(db.String(255))
    cover_url = db.Column(db.String(255))


    def __repr__(self):
        return f"title:{self.title}, author:{self.author}, pages:{self.pages}"


