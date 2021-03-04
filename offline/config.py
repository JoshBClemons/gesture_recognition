import os 
class Config(object):
    DB_HOST = 'localhost'
    DB_USER = 'postgres'
    DB_PASS = 'temporary_password'
    DB_NAME = 'postgres'
    FEATURIZER_DIRECTORY = os.path.join(os.path.abspath(os.path.dirname(__file__)), os.pardir, 'online' ,'gesture_recognition', 'featurizer.py')