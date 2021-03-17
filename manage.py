#!/usr/bin/env python
import pdb
import os
import subprocess
import sys
import eventlet
eventlet.monkey_patch()
from config import Config
from flask_script import Manager, Command, Server as _Server, Option
from gesture_recognition import create_app, db, socketio
from offline import reset_tables

manager = Manager(create_app)

def grab_and_save_model():
    """Grab highest ranking model and corresponding gestures map from database and save them locally."""
    
    # grab model and gestures map   
    import psycopg2
    import psycopg2.extras
    import json
    conn = psycopg2.connect(host=Config.DB_HOST, database=Config.DB_NAME, user=Config.DB_USER, password=Config.DB_PASS)
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    table = 'model_scores'
    query = f"SELECT model_name FROM {table} WHERE rank = 1;"
    cur.execute(query)
    conn.commit()
    model_name = cur.fetchone()[0]
    table = 'models'
    query = f"SELECT model, gestures_map FROM {table} WHERE model_name = '{model_name}'"
    cur.execute(query)
    conn.commit()
    data = cur.fetchone()
    model = data[0]
    gestures_map = data[1]
    cur.close()

    # save model and gestures map locally
    write_model = open(Config.MODEL_PATH, 'wb')
    write_model.write(model)
    write_model.close()
    with open(Config.GESTURES_MAP_PATH, 'w') as fp:
        json.dump(gestures_map, fp)

@manager.command
def createdb(drop_first=False):
    """Creates all application database tables, image directories, and figure directories

    Args:
        drop_first (bool): Boolean that indicates whether to drop all database tables and directories before creating them 
    """

    image_dir = Config.IMAGE_DIRECTORY
    fig_dir = Config.FIGURE_DIRECTORY
    if drop_first:
        import shutil

        # delete image directories
        if os.path.isdir(image_dir):
            shutil.rmtree(image_dir)

        # delete statistics figures directory         
        if os.path.isdir(fig_dir):
            shutil.rmtree(fig_dir)

        # delete database tables
        db.drop_all()
        print(f'[INFO] Deleted all image and figure directories and database tables.')          

    # create main image directory
    if os.path.isdir(image_dir) == False:
        os.mkdir(image_dir)
        print(f'[INFO] Created file storage system at {image_dir}.')
    else: 
        print(f'[INFO] File storage system already exists at {image_dir}.')

    # create original images sub-directory
    orig_dir = os.path.join(image_dir, 'original')
    if os.path.isdir(orig_dir) == False:
        os.mkdir(orig_dir)
        print(f'[INFO] Created directory for original images at {orig_dir}.')
    else: 
        print(f'[INFO] Directory for original images already exists at {orig_dir}.')

    # create processed images sub-directory
    processed_dir = os.path.join(image_dir, 'processed')
    if os.path.isdir(processed_dir) == False:
        os.mkdir(processed_dir)
        print(f'[INFO] Created directory for processed images at {processed_dir}.')
    else: 
        print(f'[INFO] Directory for processed images already exists at {processed_dir}.')

    # create statistics figures directory
    if os.path.isdir(fig_dir) == False:
        os.mkdir(fig_dir)
        print(f'[INFO] Created figure directory at {fig_dir}.')
    else: 
        print(f'[INFO] Figure directory already exists at {fig_dir}.')

    # create database tables
    db.create_all()
    print(f'[INFO] Created database tables.')

class Server(_Server):
    help = description = 'Runs the Socket.IO web server'
    def get_options(self):
        options = (
            Option('-h', '--host',
                   dest='host',
                   default='0.0.0.0'),
            Option('-p', '--port',
                   dest='port',
                   type=int,
                   default=self.port), # or self.port
            Option('-o', '--online',
                   action='store_true',
                   dest='online',
                   help='run application in SSL context',
                   default=False),
            Option('-ro', '--reset-online',
                   action='store_true',
                   dest='reset_online',
                   help='reset application database tables and directories before running server',
                   default=False),
            Option('-rof', '--reset-offline',
                   action='store_true',
                   dest='reset_offline',
                   help='reset offline database tables before running server',
                   default=False),    
        )
        return options
    def __call__(self, app, host, port, online, reset_online, reset_offline): 
        """Creates all application database tables, image directories, and figure directories and starts server

        Args:
            app (Flask application): Flask application
            host (str): IP address that hosts Flask application
            port (int): Port Flask application binds to
            online (boolean): Boolean that indicates whether to run application with secure connection 
            reset_online (boolean): Boolean that indicates whether to reset application data tables and directories before starting server
            reset_offline (boolean): Boolean that indicates whether to reset database tables before starting server 
        """

        # create database tables. if drop_first set to True, all database tables will be deleted first
        if reset_online:
            with app.app_context():
                createdb(reset_online)
        print('[INFO] Starting server.')

        # run server with or without secure connection. Online instances must be ran with secure connection 
        if online:
            basedir = os.path.abspath(os.path.dirname(__file__))
            certfile = os.path.join(basedir, 'cert.pem')
            keyfile = os.path.join(basedir, 'key.pem')
            socketio.run(
                app,
                host=host,
                port=443,
                keyfile=keyfile,
                certfile=certfile,
                use_reloader=False,
            )
        else:
            socketio.run(
                app,
                host=host,
                port=80,
                use_reloader=False,
            )
manager.add_command("start", Server())

@manager.command
def reset_offline():
    """Reset database tables used for model storage and generation and analysis."""

    reset_tables.reset_tables()

@manager.command
def model_orchestrator():
    """Run model orchestrator to generate new model."""

    from offline import orchestrator
    orchestrator.orchestrator()

@manager.command
def test():
    """Run unit tests."""

    import os 
    tests = os.system('python app_tests.py')
    sys.exit(tests)

if __name__ == '__main__':
    if sys.argv[1] == 'test':
        # ensure that Flask-Script uses the testing configuration
        os.environ['FLACK_CONFIG'] = 'testing'
    elif "-rof" in sys.argv:
        # reset offline database tables. kind of hacky implementation. 
        reset_tables.reset_tables()     

    # pull best model from database and save locally
    grab_and_save_model()
    manager.run()