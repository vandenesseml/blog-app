import logging
import os
from logging.handlers import RotatingFileHandler, SMTPHandler
from werkzeug.utils import secure_filename
from flask import Flask
from flask_bootstrap import Bootstrap
from flask_login import LoginManager
from flask_mail import Mail
from flask_migrate import Migrate
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy

from config import Config

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login = LoginManager(app)
mail = Mail(app)
bootstrap = Bootstrap(app)
moment = Moment(app)
login.login_view = 'login'
if not os.path.exists('logs'):
    os.mkdir('logs')
file_handler = RotatingFileHandler(
    'logs/blog.log', maxBytes=10240, backupCount=10)
file_handler.setFormatter(
    logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
file_handler.setLevel(logging.INFO)
app.logger.addHandler(file_handler)

app.logger.setLevel(logging.INFO)
app.logger.info('blog startup')
from app import errors, models, routes
