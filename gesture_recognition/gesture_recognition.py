#!/usr/bin/env python
import pdb
from .models import Frame, User
from . import db
from flask import Blueprint, Response, current_app
import os
import threading
import time
from . import monitoring
from . import events

main = Blueprint('main', __name__)
dir_path = os.path.dirname(os.path.realpath(__file__))

@main.before_app_first_request
def before_first_request():
    """Start background threads that looks for users that leave and refresh monitoring page"""

    def find_offline_users(app):
        with app.app_context():
            while True:
                users = User.find_offline_users()
                db.session.remove() 
                time.sleep(30)
    def update_monitoring():
        while True:
            monitoring.update_stats()
            time.sleep(5)
    if not current_app.config['TESTING']:
        t1 = threading.Thread(target=find_offline_users, args=(current_app._get_current_object(),))
        t2 = threading.Thread(target=update_monitoring)
        t1.start()
        t2.start()

@main.after_request
def after_request(response):
    """Define acceptable response headers."""
    
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,POST')

    return response

@main.route('/')
def index():
    """Direct user to gesture recognition main page."""
    
    global dir_path
    path = os.path.join(dir_path,'static/local.html')
    
    return Response(open(path).read(), mimetype="text/html")

@main.route('/stats', methods=['GET'])
def get_stats():  
    """Direct user to statistics page."""
    
    global dir_path
    path = os.path.join(dir_path,'static/stats.html')

    return Response(open(path).read(), mimetype="text/html")