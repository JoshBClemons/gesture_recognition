"""Gesture Recognition

This package launches a web-based application that returns predictions for a user's hand-gesture performed in front of their web camera

This package can also be imported as a module. The following functions are imported to other files:

    * featurizer.rotate - returns rotated versions (flipped, mirrored, and flipped+mirrored) of original image
"""

import pdb
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from flask_socketio import SocketIO
from config import config
from celery import Celery

db = SQLAlchemy()
socketio = SocketIO()
celery = Celery(__name__,
                broker=os.environ.get('CELERY_BROKER_URL', 'redis://'),
                backend=os.environ.get('CELERY_BROKER_URL', 'redis://'))
celery.config_from_object('celeryconfig')

# Import celery task so that it is registered with the Celery workers
from .tasks import run_flask_request  # noqa

# Import models so that they are registered with SQLAlchemy
from . import models 

# Import Socket.IO events so that they are registered with Flask-SocketIO
from . import events  

def create_app(config_name=None, main=True):
    """Initializes gesture recognition application

    Args:
        config_name (str): Configuration name. Application has configurations for testing, development, and production
        main (bool): If True, starting hosted application. If False, starting application used for running Celery tasks

    Returns:
        app (Flask application): Flask application
    """
    
    if config_name is None:
        config_name = os.environ.get('APP_CONFIG', 'development')
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # Initialize flask extensions
    db.init_app(app)
    if main:
        # Initialize socketio server and attach it to the message queue, so
        # that everything works even when there are multiple servers or
        # additional processes such as Celery workers wanting to access
        # Socket.IO
        socketio.init_app(app,
                          message_queue=app.config['SOCKETIO_MESSAGE_QUEUE'])
    else:
        # Initialize socketio to emit events through through the message queue
        # Note that since Celery does not use eventlet, we have to be explicit
        # in setting the async mode to not use it.
        socketio.init_app(None,
                          message_queue=app.config['SOCKETIO_MESSAGE_QUEUE'],
                          async_mode='threading')
    celery.conf.update(config[config_name].CELERY_CONFIG)

    # Register web application routes
    from .gesture_recognition import main as main_blueprint
    app.register_blueprint(main_blueprint)

    # Register API routes
    from .api import api as api_blueprint
    app.register_blueprint(api_blueprint, url_prefix='/api')

    # Register async tasks support
    from .tasks import tasks_bp as tasks_blueprint
    app.register_blueprint(tasks_blueprint, url_prefix='/tasks')

    return app