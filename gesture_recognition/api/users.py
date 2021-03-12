import pdb
from flask import request, abort, jsonify, g
from .. import db
from ..auth import token_auth
from ..models import User
from . import api

@api.route('/users', methods=['GET'])
def get_users():
    """Return list of users. This endpoint is publicly available, but if the client has a token it should send it, as that indicates to the server that the user is online."""
    users = User.query.order_by(User.updated_at.asc(), User.username.asc())
    return jsonify({'users': [user.to_dict() for user in users.all()]})

@api.route('/users', methods=['POST'])
def new_user():
    """Register a new user. This endpoint is publicly available."""
    creds = request.get_json()
    if creds['username'] == '' or creds['username'] == None or creds['password'] == '' or creds['password'] == None:
        abort(400)
    user = User.create(creds or {})
    if User.query.filter_by(username=user.username).first() is not None:
        abort(400)
    user.generate_token()
    db.session.add(user)
    db.session.commit()
    return jsonify({'token': user.token})
