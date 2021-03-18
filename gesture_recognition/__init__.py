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

db = SQLAlchemy()
socketio = SocketIO()

# Import models so that they are registered with SQLAlchemy
from . import models 

def create_app(config_name=None):
    """Initializes gesture recognition application

    Args:
        config_name (str): Configuration name. Application has configurations for testing, development, and production

    Returns:
        app (Flask application): Flask application
    """
    
    # Import Socket.IO events so that they are registered with Flask-SocketIO
    from . import events  

    if config_name is None:
        config_name = os.environ.get('APP_CONFIG', 'development')
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # Initialize flask extensions
    db.init_app(app)
    socketio.init_app(app)

    # Register web application routes
    from .gesture_recognition import main as main_blueprint
    app.register_blueprint(main_blueprint)

    # Register API routes
    from .api import api as api_blueprint
    app.register_blueprint(api_blueprint, url_prefix='/api')

    return app