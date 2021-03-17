import pdb
from flask import g, jsonify, session
from flask_httpauth import HTTPBasicAuth, HTTPTokenAuth
from . import db
from .models import User

# Authentication objects for username/password auth, token auth, and a token optional auth that is used for open endpoints.
basic_auth = HTTPBasicAuth()
token_auth = HTTPTokenAuth('Bearer')

@basic_auth.verify_password
def verify_password(username, password):
    """Password verification callback

    Args:
        username (str): Client user name
        password (str): Client password

    Returns:
        (boolean): True if successful password verification. False otherwise or if blank credentials entered. 
    """
    
    if not username or not password or username == "''" or password == "''":
        return False
    user = User.query.filter_by(username=username).first()

    # if not a user, create the user 
    if user is None: 
        user_dict = {'username': username, 'password': password}
        user = User.create(user_dict)
    elif not user.verify_password(password):
        return False
    else:
        user.new_login()       

    # mark user as online   
    user.ping() 
    db.session.add(user)
    db.session.commit()
    g.current_user = user

    return True

@basic_auth.error_handler
def password_error():
    """Return a 401 error to the client

    Returns:
        (Response): Serialized error message
    """

    return (jsonify({'error': 'authentication required'}), 401,{'WWW-Authenticate': 'Bearer realm="Authentication Required"'})

@token_auth.verify_token
def verify_token(token, add_to_session=False):
    """Token verification callback

    Args:
        token (str): Client token
        add_to_session (boolean): Determines whether to store client information in session 

    Returns:
        (boolean): True if successful token verification. False if user does not exist 
    """

    if add_to_session:
        # clear the session in case auth fails
        if 'username' in session:
            del session['username']
    user = User.query.filter_by(token=token).first()
    if user is None:
        return False

    # mark the user as online 
    user.ping()
    db.session.add(user)
    db.session.commit()
    g.current_user = user

    # store username in client session
    if add_to_session:
        session['username'] = user.username

    return True

@token_auth.error_handler
def token_error():
    """Return a 401 error to the client

    Returns:
        (Response): Serialized error message
    """
    
    return (jsonify({'error': 'authentication required'}), 401, {'WWW-Authenticate': 'Bearer realm="Authentication Required"'})