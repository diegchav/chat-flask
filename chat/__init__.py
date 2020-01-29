import os
from celery import Celery
from dotenv import load_dotenv
from flask import Flask, g, session
from flask_marshmallow import Marshmallow
from flask_moment import Moment
from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy

from config.app import Config

# Load environment variables from .env file
load_dotenv()

celery = Celery(__name__, broker=Config.CELERY_BROKER_URL)

db = SQLAlchemy()
ma = Marshmallow()
moment = Moment()
socketio = SocketIO()

def create_app():
    app = Flask(__name__)
    app.config.from_object(os.environ['APP_SETTINGS'])
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    celery.conf.update(app.config)

    db.init_app(app)
    ma.init_app(app)
    moment.init_app(app)
    socketio.init_app(app)

    with app.app_context():
        # Models
        from .models import User

        # Blueprints
        from . import auth, chat
        app.register_blueprint(auth.bp)
        app.register_blueprint(chat.bp)

        @app.before_request
        def load_logged_in_user():
            user_id = session.get('user_id')

            if user_id is None:
                g.user = None
            else:
                user = User.query.filter_by(id=user_id).first()
                g.user = user

        # Create db models
        db.create_all()

        return app