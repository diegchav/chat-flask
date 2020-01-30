import os
from celery import Celery
from dotenv import load_dotenv
from flask import Flask

from . import auth, chat
from .extensions import (
    db,
    login,
    ma,
    migrate,
    moment,
    socketio
)

def make_celery():
    app = Flask(__name__)
    app.config.from_object(os.environ['APP_SETTINGS'])

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
    login.init_app(app)
    login.login_view = 'auth.login'
    ma.init_app(app)
    migrate.init_app(app, db)
    moment.init_app(app)
    socketio.init_app(app, message_queue=os.environ['MESSAGE_QUEUE'])

    # Register blueprints
    app.register_blueprint(auth.bp)
    app.register_blueprint(chat.bp)

    return app