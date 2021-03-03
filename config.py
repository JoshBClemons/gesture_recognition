import pdb
import os

basedir = os.path.abspath(os.path.dirname(__file__)) # current directory

class Config(object):
    DB_HOST = 'localhost'
    DB_USER = 'postgres'
<<<<<<< HEAD
    DB_PASS = 'temporary_password'
=======
    DB_PASS = 'temp_pass'
>>>>>>> 3952c3d486fbf2bf12304b497484301cf9de415d
    DB_NAME = 'postgres'
    DEBUG = False
    TESTING = False
    SECRET_KEY = os.environ.get('SECRET_KEY', '51f52814-0071-11e6-a247-000ec6c2372c')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///' + os.path.join(basedir, 'db.sqlite'))
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    REQUEST_STATS_WINDOW = 15
    CELERY_CONFIG = {}
    SOCKETIO_MESSAGE_QUEUE = os.environ.get('SOCKETIO_MESSAGE_QUEUE', os.environ.get('CELERY_BROKER_URL', 'redis://'))

class DevelopmentConfig(Config):
    DEBUG = True

config = {
    'development': DevelopmentConfig,
}