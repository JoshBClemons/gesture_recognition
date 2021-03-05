import pdb
from flask import request, abort, jsonify, g

from .. import db
from ..auth import token_auth, token_optional_auth
from ..models import User
# from ..utils import url_for

from . import api


@api.route('/users', methods=['GET'])
def get_users():
    """
    Return list of users.
    This endpoint is publicly available, but if the client has a token it
    should send it, as that indicates to the server that the user is online.
    """
    users = User.query.order_by(User.updated_at.asc(), User.username.asc())
    return jsonify({'users': [user.to_dict() for user in users.all()]})

@api.route('/users', methods=['POST'])
def new_user():
    """
    Register a new user.
    This endpoint is publicly available.
    """
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


# @api.route('/users/<id>', methods=['GET'])
# @token_optional_auth.login_required
# def get_user(id):
#     """
#     Return a user.
#     This endpoint is publicly available, but if the client has a token it
#     should send it, as that indicates to the server that the user is online.
#     """
#     return jsonify(User.query.get_or_404(id).to_dict())


# @api.route('/users/<id>', methods=['PUT'])
# @token_auth.login_required
# def edit_user(id):
#     """
#     Modify an existing user.
#     This endpoint is requires a valid user token.
#     Note: users are only allowed to modify themselves.
#     """
#     user = User.query.get_or_404(id)
#     if user != g.current_user:
#         abort(403)
#     user.from_dict(request.get_json() or {})
#     db.session.add(user)
#     db.session.commit()
#     return '', 204
