import pdb
import binascii
import os
from flask import g
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from .utils import timestamp

class User(db.Model):
    """The User model

    Attributes:
        __tablename__ (str): Table name for user model in database 
        id (SQLAlchemy table column, int): User ID 
        created_at (SQLAlchemy table column, int): Timestamp at which user was first created 
        updated_at (SQLAlchemy table column, int): Timestamp of last time user profile was updated
        last_seen_at (SQLAlchemy table column, int): Timestamp of last time user was active
        username (SQLAlchemy table column, str): User username 
        password_hash (SQLAlchemy table column, str): User password hash string
        token (SQLAlchemy table column, str): User authentication token 
        online (SQLAlchemy table column, bool): Boolean that captures whether user is online
        num_logins (SQLAlchemy table column, int): Number of user logins to page
        frames (SQLAlchemy table relationship): Relationship property linking "user" model table to this one
    """
    
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.Integer, default=timestamp)
    updated_at = db.Column(db.Integer, default=timestamp, onupdate=timestamp)
    last_seen_at = db.Column(db.Integer, default=timestamp)
    username = db.Column(db.String(32), nullable=False, unique=True)
    password_hash = db.Column(db.String(256), nullable=False)
    token = db.Column(db.String(64), nullable=True, unique=True)
    online = db.Column(db.Boolean, default=False)
    num_logins = db.Column(db.Integer, default=1)
    frames = db.relationship('Frame', lazy='dynamic', backref='user')

    @property
    def password(self):
        """Returns attribute error if user password is not readable"""

        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        """Generates password hash string and authentication token from user password

        Args:
            password (str): User password
        """

        self.password_hash = generate_password_hash(password)
        self.token = None  # if user is changing passwords, also revoke token

    def verify_password(self, password):
        """Verify password matches stored password hash string

        Args:
            password (str): Inputted user password

        Returns:
            (bool): True if password matches password hash string
        """
        
        return check_password_hash(self.password_hash, password)

    def generate_token(self):
        """Creates a 64 character long randomly generated token

        Returns:
            self.token (str): Generated token
        """

        self.token = binascii.hexlify(os.urandom(32)).decode('utf-8')
        return self.token

    def ping(self):
        """Marks the user as recently seen and online"""

        self.last_seen_at = timestamp()
        self.online = True

    def new_login(self):
        """Increments number of times user has logged in."""
                
        self.num_logins += 1

    @staticmethod
    def create(data):
        """Create a new user

        Args:
            data (dict): Dictionary containing user's username and password

        Returns:
            user (object): Newly created user 
        """
        
        user = User()
        user.from_dict(data)
        return user

    def from_dict(self, data):
        """Import user data from a dictionary

        Args:
            data (dict): Dictionary containing user's username and password
        """
        
        for field in ['username', 'password']:
            try:
                setattr(self, field, data[field])
            except KeyError:
                print(f'Key {key} not valid.')

    def to_dict(self):
        """Export user to a dictionary"""
       
        return {
            'username': self.username,
            'online': self.online,
        }

    @staticmethod
    def find_offline_users():
        """Find users that haven't been active and mark them as offline

        Returns:
            users (list): List of offline users
        """ 
        
        users = User.query.filter(User.last_seen_at < timestamp() - 60, User.online == True).all()  
        for user in users:
            user.online = False
            db.session.add(user)
        db.session.commit()
        return users


class Frame(db.Model):
    """The Frames model

    Attributes:
        __tablename__ (str): Table name for user model in database 
        instance (SQLAlchemy table column, str): Unique ID for processed frame 
        date (SQLAlchemy table column, datetime): Date that frame is processed 
        session_id (SQLAlchemy table column, int): User's login count 
        frame_count (SQLAlchemy table column, int): Frame number for user's current session
        ip_address (SQLAlchemy table column, str): User's IP address
        root_dir (SQLAlchemy table column, str): Root directory of user's image folder 
        raw_path (SQLAlchemy table column, str): Path for original image
        processed_path (SQLAlchemy table column, str): Path for processed image 
        true_gest (SQLAlchemy table column, str): Ground-truth gesture inputted by user
        pred_gest (SQLAlchemy table column, str): Predicted gesture
        pred_conf (SQLAlchemy table column, float): Prediction confidence, percent
        pred_time (SQLAlchemy table column, float): Prediction time, seconds 
        user_id (SQLAlchemy table column, int): User ID 
    """
    
    __tablename__ = 'frames'
    instance = db.Column(db.String(), primary_key=True, nullable=False)
    date = db.Column(db.DateTime(), nullable=False)
    session_id = db.Column(db.Integer(), nullable=False)
    frame_count = db.Column(db.Integer(), nullable=False)
    ip_address = db.Column(db.String())
    root_dir = db.Column(db.String(), nullable=False)
    raw_path = db.Column(db.String(), nullable=False)
    processed_path = db.Column(db.String())
    true_gest = db.Column(db.String(), nullable=False)
    pred_gest = db.Column(db.String(), nullable=False)
    pred_conf = db.Column(db.Numeric(), nullable=False)
    pred_time = db.Column(db.Numeric(), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    @staticmethod
    def create(data, user=None):
        """Create a new frame. The user is obtained from the context unless provided explicitly.

        Args:
            data (dict): Dictionary containing values for some or all class attributes listed above

        Returns:
            frame (object): Newly generated frame
        """
        
        frame = Frame(user=user or g.current_user)
        frame.from_dict(data)
        return frame

    def from_dict(self, data):
        """Import frame data from a dictionary

        Args:
            data (dict): Dictionary containing values for some or all class attributes listed above
        """
        
        for key in list(data.keys()):
            try:
                setattr(self, key, data[key])
            except KeyError:
                print(f'Key {key} not valid.')