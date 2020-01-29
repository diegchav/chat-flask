from celery import Celery
from flask_marshmallow import Marshmallow
from flask_moment import Moment
from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy

from config.app import Config

celery = Celery(__name__, broker=Config.CELERY_BROKER_URL)

db = SQLAlchemy()
ma = Marshmallow()
moment = Moment()
socketio = SocketIO()