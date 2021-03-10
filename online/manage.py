#!/usr/bin/env python
import pdb
import os
import subprocess
import sys
import eventlet
eventlet.monkey_patch()
from flask_script import Manager, Command, Server as _Server, Option
from gesture_recognition import create_app, db, socketio#, engine

manager = Manager(create_app)

class Server(_Server):
    help = description = 'Runs the Socket.IO web server'

    def get_options(self):
        options = (
            Option('-h', '--host',
                   dest='host',
                   default=self.host),
            Option('-p', '--port',
                   dest='port',
                   type=int,
                   default=self.port),
            Option('-o', '--online',
                   action='store_true',
                   dest='online',
                   help='run application in SSL context',
                   default=False),
        )
        return options

    def __call__(self, app, host, port, online):
        if online:
            basedir = os.path.abspath(os.path.dirname(__file__))
            certfile = os.path.join(basedir,'cert.pem')
            keyfile = os.path.join(basedir,'key.pem')
            socketio.run(
                app,
                host=host,
                port=port,
                keyfile=keyfile,
                certfile=certfile,
            )
        else:
            socketio.run(
                app,
                host=host,
                port=port,
            )
manager.add_command("runserver", Server())

@manager.command
def createdb(drop_first=False):
    """Creates the database."""
    from config import Config
    image_dir = Config.IMAGE_DIRECTORY
    fig_dir = Config.FIGURE_DIRECTORY
    if drop_first:
        import shutil
        # delete image directories
        if os.path.isdir(image_dir):
            shutil.rmtree(image_dir)
        # delete figure directory         
        if os.path.isdir(fig_dir):
            shutil.rmtree(fig_dir)
        # delete database tables
        db.drop_all()
        print(f'[INFO] Deleted all image and figure directories and database tables.')
                      
    # create image directories
    if os.path.isdir(image_dir) == False:
        os.mkdir(image_dir)
        print(f'[INFO] Created file storage system at {image_dir}.')
    else: 
        print(f'[INFO] File storage system already exists at {image_dir}.')
        
    orig_dir = os.path.join(image_dir, 'original')
    if os.path.isdir(orig_dir) == False:
        os.mkdir(orig_dir)
        print(f'[INFO] Created directory for original images at {orig_dir}.')
    else: 
        print(f'[INFO] Directory for original images already exists at {orig_dir}.')

    processed_dir = os.path.join(image_dir, 'processed')
    if os.path.isdir(processed_dir) == False:
        os.mkdir(processed_dir)
        print(f'[INFO] Created directory for processed images at {processed_dir}.')
    else: 
        print(f'[INFO] Directory for processed images already exists at {processed_dir}.')

    # create figure directory
    if os.path.isdir(fig_dir) == False:
        os.mkdir(fig_dir)
        print(f'[INFO] Created figure directory at {fig_dir}.')
    else: 
        print(f'[INFO] Figure directory already exists at {fig_dir}.')
            
    db.create_all()
    print(f'[INFO] Created database tables.')

@manager.command
def test():
    import os 
    """Runs unit tests."""
    tests = os.system('python tests.py')
    sys.exit(tests)

if __name__ == '__main__':
    if sys.argv[1] == 'test':
        # ensure that Flask-Script uses the testing configuration
        os.environ['FLACK_CONFIG'] = 'testing'
    manager.run()