from flask import Flask, g, session
from flask_sqlalchemy import SQLAlchemy
import sqlite3
import middleware

# configuration
DATABASE = '/tmp/alayatodo.db'
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + DATABASE
SQLALCHEMY_TRACK_MODIFICATIONS = False
DEBUG = True
SECRET_KEY = 'development key'
USERNAME = 'admin'
PASSWORD = 'default'

app = Flask(__name__)
app.config.from_object(__name__)
db = SQLAlchemy(app)

import alayatodo.views
from alayatodo.models import User

@app.before_request
def before_request():
    g.user = User.query.get(session['user_id']) if session.get('user_id', None) is not None else None

app.wsgi_app = middleware.MethodRewriteMiddleware(app.wsgi_app)