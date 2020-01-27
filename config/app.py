import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    DEBUG = False
    ENV = 'development'
    SECRET_KEY = os.getenv('SECRET_KEY', 'secret')
    SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']


class ProductionConfig(Config):
    ENV = 'production'


class StagingConfig(Config):
    DEBUG = True
    ENV = 'production'


class DevelopmentConfig(Config):
    DEBUG = True