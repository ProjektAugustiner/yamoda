#  -*- coding: utf-8 -*-
#
# yamoda, (c) 2012, see AUTHORS.  Licensed under the GNU GPL.
"""The accesscontrol module handles the user access control

Classes:
--------
Permission      -- Stores User/Group/All read & write permissions.
PermissionError -- Raised when a row level access is denied
User            -- Handles the usernames, passwords and login status
Group           -- Used for unix-style access control

Functions:
----------
load_user -- User loader callback neccessary for flask-login

"""
from sqlalchemy.ext.hybrid import hybrid_property
from flask.ext.login import UserMixin
import bcrypt

from yamoda.server import db, login_manager


class PermissionError(Exception):
    """Raised when a row level access is denied"""
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class Permission(object):
    """Stores User/Group/All read & write permissions.

    The Permission class stores read and write permissions for User,
    Group and All as binary flags of an integer. Unlike unix, the 
    first three bits represent the read permissions, followed by the
    write permissions.
    
    Bit - permission
    ---------------
      0 - User read permission
      1 - Group read permission
      2 - All read permission
      3 - User write permission
      4 - Group write permission
      5 - All write permission

    """
    def __init__(self, **kw):
        if 'permission' in kw:
            self.permission = kw['permission']
        else:            
            self.permission = 0
            self.user_readable = kw.get('user_readable', True)
            self.user_writeable = kw.get('user_readable', True)
            self.group_readable = kw.get('group_readable', True)
            self.group_writeable = kw.get('group_writeable', True)
            self.all_readable = kw.get('all_readable', True)
            self.all_writeable = kw.get('all_writeable', False)

    def __perm_getter__(i):
        def get(self): #get bit
            return bool(self.permission & (1 << i))
        return get

    def __perm_setter__(i):
        def set(self, value):
            if value: #set bit
                self.permission |= 1 << i
            else: #clear bit
                self.permission &= ~(1 << i)
        return set

    def __repr__(self):
        return '<Permission({0})>'.format(bin(self.permission))

    user_readable   = hybrid_property(__perm_getter__(0), __perm_setter__(0))
    group_readable  = hybrid_property(__perm_getter__(1), __perm_setter__(1))
    all_readable    = hybrid_property(__perm_getter__(2), __perm_setter__(2))

    user_writeable  = hybrid_property(__perm_getter__(3), __perm_setter__(3))
    group_writeable = hybrid_property(__perm_getter__(4), __perm_setter__(4))
    all_writeable   = hybrid_property(__perm_getter__(5), __perm_setter__(5))


_usergroup_table = db.Table('usergroup_table', db.metadata,
    db.Column('user_id',  db.Integer, db.ForeignKey('user.id')),
    db.Column('group_id', db.Integer, db.ForeignKey('group.id')))


class PermissionType(db.TypeDecorator):
    """Simple TypeDecorator, wrapping the parameter class."""
    impl = db.Integer

    def process_bind_param(self, value, dialect):
        if value is not None:
            value = value.permission
        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            value = Permission(permission=value)
        return value


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
