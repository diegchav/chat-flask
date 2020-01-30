from flask_login import LoginManager
from flask_marshmallow import Marshmallow
from flask_migrate import Migrate
from flask_moment import Moment
from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
login = LoginManager()
ma = Marshmallow()
migrate = Migrate()
moment = Moment()
socketio = SocketIO()