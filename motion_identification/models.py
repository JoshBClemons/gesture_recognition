import pdb
import binascii
import os
from flask import g
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from .utils import timestamp#, url_for


class User(db.Model):
    """The User model."""
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.Integer, default=timestamp)
    updated_at = db.Column(db.Integer, default=timestamp, onupdate=timestamp)
    last_seen_at = db.Column(db.Integer, default=timestamp)
    username = db.Column(db.String(32), nullable=False, unique=True)
    password_hash = db.Column(db.String(256), nullable=False)
    token = db.Column(db.String(64), nullable=True, unique=True)
    online = db.Column(db.Boolean, default=False)
    last_instance = db.Column(db.Integer, default=0)
    frames = db.relationship('Frame', lazy='dynamic', backref='user')

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)
        self.token = None  # if user is changing passwords, also revoke token

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_token(self):
        """Creates a 64 character long randomly generated token."""
        self.token = binascii.hexlify(os.urandom(32)).decode('utf-8')
        return self.token

    # def ping(self):
    #     """Marks the user as recently seen and online."""
    #     self.last_seen_at = timestamp()
    #     last_online = self.online
    #     self.online = True
    #     return last_online != self.online

    @staticmethod
    def create(data):
        """Create a new user."""
        user = User()
        user.from_dict(data)
        return user

    def from_dict(self, data):
        """Import user data from a dictionary."""
        for field in ['username', 'password']:
            try:
                setattr(self, field, data[field])
            except KeyError:
                print(f'Key {key} not valid.')

    # def to_dict(self):
    #     """Export user to a dictionary."""
    #     return {
    #         'id': self.id,
    #         'created_at': self.created_at,
    #         'updated_at': self.updated_at,
    #         'nickname': self.nickname,
    #         'last_seen_at': self.last_seen_at,
    #         'online': self.online,
    #         '_links': {
    #             'self': url_for('api.get_user', id=self.id),
    #             'messages': url_for('api.get_messages', user_id=self.id),
    #             'tokens': url_for('api.new_token')
    #         }
    #     }

    @staticmethod
    def find_offline_users():
        """Find users that haven't been active and mark them as offline."""
        users = User.query.filter(User.last_seen_at < timestamp() - 60,
                                  User.online == True).all()  # noqa
        for user in users:
            user.online = False
            db.session.add(user)
        db.session.commit()
        return users

class Frame(db.Model):
    __tablename__ = 'frames'
    instance = db.Column(db.String(), primary_key=True, nullable=False)
    date = db.Column(db.Date(), nullable=False)
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
         
    def __repr__(self):
        return "hi there"

    @staticmethod
    def create(data, user=None):
        """Create a new message. The user is obtained from the context unless
        provided explicitly.
        """
        frame = Frame(user=user or g.current_user)
        frame.from_dict(data)
        return frame

    def from_dict(self, data):
        """Import frame data from a dictionary."""
        for key in list(data.keys()):
            try:
                setattr(self, key, data[key])
            except KeyError:
                print(f'Key {key} not valid.')