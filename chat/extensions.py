from flask_marshmallow import Marshmallow
from flask_moment import Moment
from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
ma = Marshmallow()
moment = Moment()
socketio = SocketIO()