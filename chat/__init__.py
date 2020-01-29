import os
from celery import Celery
from dotenv import load_dotenv
from flask import Flask, g, session

from . import auth, chat
from .extensions import (
    db,
    ma,
    moment,
    socketio
)
from .models import User

def make_celery(app=None):
    app = app or create_app()

    celery = Celery(
        app.import_name,
        backend=app.config['CELERY_RESULT_BACKEND'],
        broker=app.config['CELERY_BROKER_URL']
    )
    celery.conf.update(app.config)

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery

def create_app():
    # Load environment variables from .env file
    load_dotenv()

    app = Flask(__name__)
    app.config.from_object(os.environ['APP_SETTINGS'])
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    with app.app_context():
        # Init extensions
        db.init_app(app)
        ma.init_app(app)
        moment.init_app(app)
        socketio.init_app(app)

        # Register blueprints
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