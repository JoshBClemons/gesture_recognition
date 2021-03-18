import pdb
import os

basedir = os.path.abspath(os.path.dirname(__file__))
class Config(object):
    """Class that stores conifguration information for default gesture recognition application""" 

    DB_HOST = 'localhost'
    DB_USER = 'postgres'
    DB_PASS = 'temporary_password'
    DB_NAME = 'testing'
    DEBUG = False
    TESTING = False
    IMAGE_DIRECTORY = os.path.join(basedir, 'images')
    MODEL_PATH = os.path.join(basedir, 'gesture_recognition', 'current_model.h5')
    GESTURES_MAP_PATH = os.path.join(basedir, 'gesture_recognition', 'gestures_map.json')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', f'postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}/{DB_NAME}')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # celery
    REQUEST_STATS_WINDOW = 15
    CELERY_CONFIG = {}
    SOCKETIO_MESSAGE_QUEUE = os.environ.get('SOCKETIO_MESSAGE_QUEUE', os.environ.get('CELERY_BROKER_URL','redis://'))

    # tells orchestrator where to look for featurizer.py
    FEATURIZER_DIRECTORY = os.path.join(os.path.abspath(os.path.dirname(__file__)),'gesture_recognition', 'featurizer.py')
    
    # information for monitoring.py
    FIGURE_DIRECTORY = os.path.join(basedir, 'gesture_recognition', 'figures')
    STATS_MESSAGE_PATH = os.path.join(FIGURE_DIRECTORY, 'stats_message.txt')
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
    """Class that stores conifguration information for developing gesture recognition application""" 

    DEBUG = True

class ProductionConfig(Config):
    """Class that stores conifguration information for deploying gesture recognition application""" 

    pass

class TestingConfig(Config):
    """Class that stores conifguration information for testing gesture recognition application""" 

    TESTING = True

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig
}