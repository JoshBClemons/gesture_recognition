#!/usr/bin/env python
import os
import subprocess
import sys

import eventlet
eventlet.monkey_patch()

from flask_script import Manager, Command, Server as _Server, Option
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Numeric, Date
from motion_identification import create_app, db#, engine

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
        app.run(
                host='0.0.0.0',
                port=5000,
                debug=False,
        )

manager.add_command("runserver", Server())

@manager.command
def createdb(drop_first=True):
    """Creates the database."""
    if drop_first:
        db.drop_all()
    db.create_all()

if __name__ == '__main__':
    manager.run()