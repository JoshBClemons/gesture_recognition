import pdb
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
# from flask_bootstrap import Bootstrap
from flask_socketio import SocketIO
# from celery import Celery
from config import config

# Flask extensions
db = SQLAlchemy()
# bootstrap = Bootstrap()
socketio = SocketIO()
# celery = Celery(__name__,
#                 broker=os.environ.get('CELERY_BROKER_URL', 'redis://'),
#                 backend=os.environ.get('CELERY_BROKER_URL', 'redis://'))
# celery.config_from_object('celeryconfig')

# Import models so that they are registered with SQLAlchemy
from . import models 

# Import celery task so that it is registered with the Celery workers
# from .tasks import run_flask_request  # noqa

image_directory = ''
def create_app(config_name=None, main=True):
    if config_name is None:
        config_name = os.environ.get('FLACK_CONFIG', 'development')
    
    # create image directories
    global image_directory
    image_directory = config[config_name].IMAGE_DIRECTORY
    if os.path.isdir(image_directory) == False:
        os.mkdir(image_directory)
        print(f'[INFO] Created file storage system at {image_directory}.')
    else: 
        print(f'[INFO] File storage system already exists at {image_directory}.')
    
    orig_dir = os.path.join(image_directory, 'original')
    if os.path.isdir(orig_dir) == False:
        os.mkdir(orig_dir)
        print(f'[INFO] Created directory for original images at {orig_dir}.')
    else: 
        print(f'[INFO] Directory for original images already exists at {orig_dir}.')
    
    processed_dir = os.path.join(image_directory, 'processed')
    if os.path.isdir(processed_dir) == False:
        os.mkdir(processed_dir)
        print(f'[INFO] Created directory for processed images at {processed_dir}.')
    else: 
        print(f'[INFO] Directory for processed images already exists at {processed_dir}.')

    # grab and save current model and gestures_map locally
    import psycopg2
    import psycopg2.extras
    import json
    conn = psycopg2.connect(host=config[config_name].DB_HOST, database=config[config_name].DB_NAME, user=config[config_name].DB_USER, password=config[config_name].DB_PASS)
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    query = "SELECT model, gestures_map FROM models WHERE rank = 1;"
    cur.execute(query)
    conn.commit()
    data = cur.fetchone()
    model = data[0]
    gestures_map = data[1]
    cur.close()

    # save files
    write_model = open(config[config_name].MODEL_PATH, 'wb')
    write_model.write(model)
    write_model.close()
    with open(config[config_name].GESTURES_MAP_PATH, 'w') as fp:
        json.dump(gestures_map, fp)

    # Import Socket.IO events so that they are registered with Flask-SocketIO
    from . import events  

    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # Initialize flask extensions
    db.init_app(app)
    # bootstrap.init_app(app)
    socketio.init_app(app)
    # if main:
    #     # Initialize socketio server and attach it to the message queue, so
    #     # that everything works even when there are multiple servers or
    #     # additional processes such as Celery workers wanting to access
    #     # Socket.IO
    #     socketio.init_app(app,
    #                       message_queue=app.config['SOCKETIO_MESSAGE_QUEUE'])
    # else:
    #     # Initialize socketio to emit events through through the message queue
    #     # Note that since Celery does not use eventlet, we have to be explicit
    #     # in setting the async mode to not use it.
    #     socketio.init_app(None,
    #                       message_queue=app.config['SOCKETIO_MESSAGE_QUEUE'],
    #                       async_mode='threading')
    # celery.conf.update(config[config_name].CELERY_CONFIG)

    # Register web application routes
    from .gesture_recognition import main as main_blueprint
    app.register_blueprint(main_blueprint)

    # Register API routes
    from .api import api as api_blueprint
    app.register_blueprint(api_blueprint, url_prefix='/api')

    # # Register async tasks support
    # from .tasks import tasks_bp as tasks_blueprint
    # app.register_blueprint(tasks_blueprint, url_prefix='/tasks')    

    return app