import os
from celery import Celery
from dotenv import load_dotenv
from flask import Flask, g, session

from . import auth, chat
from .extensions import (
    db,
    ma,
    migrate,
    moment,
    socketio
)
from .models import *

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

    # Init extensions
    db.init_app(app)
    ma.init_app(app)
    migrate.init_app(app, db)
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

    return app