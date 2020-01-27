import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    DEBUG = False
    SECRET_KEY = 'secret'
    SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']


class ProductionConfig(Config):
    SECRET_KEY = os.environ['SECRET_KEY']


class StagingConfig(Config):
    SECRET_KEY = os.environ['SECRET_KEY']


class DevelopmentConfig(Config):
    DEBUG = True