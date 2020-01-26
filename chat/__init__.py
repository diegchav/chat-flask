import os
from dotenv import load_dotenv
from flask import Flask, g, session
from flask_moment import Moment
from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy

# Load environment variables from .env file
load_dotenv()

db = SQLAlchemy()
moment = Moment()
socketio = SocketIO()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.environ['SECRET_KEY']
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
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