#  -*- coding: utf-8 -*-
#
# yamoda, (c) 2012, see AUTHORS.  Licensed under the GNU GPL.
"""The accesscontrol module handles the user access control

Classes:
--------
User  -- Handles the usernames, passwords and login status
Group -- Used for unix-style access control

Functions:
----------
load_user -- User loader callback neccessary for flask-login

"""
from sqlalchemy.ext.hybrid import hybrid_property
from flask.ext.login import UserMixin
import bcrypt

from yamoda.server import db, login_manager


_usergroup_table = db.Table('usergroup_table', db.metadata,
    db.Column('user_id',  db.Integer, db.ForeignKey('user.id')),
    db.Column('group_id', db.Integer, db.ForeignKey('group.id')))


class User(db.Model, UserMixin):
    """Handles the usernames, passwords and the login status"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(60), nullable=False, unique=True)
    _hashed_pw = db.Column(db.String(60), nullable=False)

    @hybrid_property
    def password(self):
        return self._hashed_pw

    @password.setter
    def password(self, value):
        self._hashed_pw = bcrypt.hashpw(value, bcrypt.gensalt())

    def valid_password(self, password):
        return self._hashed_pw == bcrypt.hashpw(password, self._hashed_pw)

    def __repr__(self):
        return '<User({0},{1})>'.format(self.id, self.name)


class Group(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(60), nullable=False)
    users = db.relationship('User', secondary=_usergroup_table,
                            backref='groups')

    def __repr__(self):
        return '<Group({0},{1})>'.format(self.id, self.name)


@login_manager.user_loader
def load_user(userid):
    """User loader callback neccessary for flask-login"""
    return User.query.filter_by( id=int(userid) ).first()
