from flask import Flask, Blueprint, render_template, request, make_response
from flask_sqlalchemy import SQLAlchemy
from Db import db
from Db.models import users
from flask_login import LoginManager
from main import main
app = Flask(__name__)
app.register_blueprint(main)

app.secret_key = '123'
user_db = "booblikoteka"
host_ip = "127.0.0.1"
host_port = "5432"
database_name = "bookshop"
password = "555666"

app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{user_db}:{password}@{host_ip}:{host_port}/{database_name}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

login_manager = LoginManager()
login_manager.login_view = "rgz"
login_manager.init_app(app)

@login_manager.user_loader
def load_users(user_id):
    try:
        user = users.query.get(int(user_id))
    except:
        return None
    return user
