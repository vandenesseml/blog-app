import logging
import os
from logging.handlers import RotatingFileHandler, SMTPHandler
from werkzeug.utils import secure_filename
from flask import Flask
from flask_bootstrap import Bootstrap
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy

from config import Config

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login = LoginManager(app)
bootstrap = Bootstrap(app)
moment = Moment(app)
login.login_view = 'login'

from app import errors, models, routes

