import pdb
import os

basedir = os.path.abspath(os.path.dirname(__file__))
class Config(object):
    DB_HOST = 'localhost'
    DB_USER = 'postgres'
    DB_PASS = 'temporary_password'
    DB_NAME = 'postgres'
    DEBUG = False
    TESTING = False
    IMAGE_DIRECTORY = os.path.join(basedir, os.pardir, 'gesture_recognition_images')
    MODEL_PATH = os.path.join(basedir, 'gesture_recognition\\current_model.h5')
    GESTURES_MAP_PATH = os.path.join(basedir, 'gesture_recognition\\gestures_map.json')
    # SECRET_KEY = os.environ.get('SECRET_KEY', '51f52814-0071-11e6-a247-000ec6c2372c')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', f'postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}/{DB_NAME}')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # REQUEST_STATS_WINDOW = 15
    # CELERY_CONFIG = {}
    # SOCKETIO_MESSAGE_QUEUE = os.environ.get('SOCKETIO_MESSAGE_QUEUE', os.environ.get('CELERY_BROKER_URL', 'redis://'))

    # figure information
    FIGURE_DIRECTORY = os.path.join(basedir, 'gesture_recognition\\figures')
    CR_FIGURE_NAMES = (
        "top_classification_report", 
        "middle_classification_report", 
        "bottom_classification_report", 
    )
    CM_FIGURE_NAMES = (
        "top_confusion_matrix", 
        "middle_confusion_matrix", 
        "bottom_confusion_matrix",
    )
    OTHER_FIGURE_NAMES = (
        "todays_user_activity", 
        "gesture_prediction_accuracy_by_date", 
        "total_user_usage_time_by_date", 
        "true_gesture_counts_by_date", 
    )

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    pass

class TestingConfig(Config):
    TESTING = True
    # CELERY_CONFIG = {'CELERY_ALWAYS_EAGER': True}
    # SOCKETIO_MESSAGE_QUEUE = None

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig
}