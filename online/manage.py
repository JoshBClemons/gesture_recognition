#!/usr/bin/env python
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
        )
        return options

    def __call__(self, app, host, port):
        socketio.run(app,
                    host=host,
                    port=port,
        )
manager.add_command("runserver", Server())

@manager.command
def createdb(drop_first=True):
    """Creates the database."""
    if drop_first:
        db.drop_all()
        print(f'[INFO] Dropped all database tables.')
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