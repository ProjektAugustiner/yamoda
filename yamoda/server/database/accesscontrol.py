#  -*- coding: utf-8 -*-
#
# yamoda, (c) 2012, see AUTHORS.  Licensed under the GNU GPL.

"""
Handle user access control.

Classes:
--------
Permission      -- Stores User/Group/All read & write permissions.
PermissionError -- Raised when a row level access is denied
PermissionType  -- Simple TypeDecorator, wrapping the parameter class.
User            -- Handles the usernames, passwords and login status
Group           -- Used for unix-style access control
AccessControl   -- Mixin class, adding row level security to the DB model.

Functions:
----------
load_user -- User loader callback neccessary for flask-login

"""
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.ext.hybrid import hybrid_property
from flask import _request_ctx_stack
from flask.ext.login import UserMixin, current_user
import bcrypt

from yamoda.server import db, login_manager


class PermissionError(Exception):
    """Raised when a row level access is denied."""
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
    ----------------
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
            self.user_writeable = kw.get('user_writeable', True)
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


class AccessControl(object):
    """Mixin class, adding row level security to the database model.

    The AccessControl mixin adds row level security to a sqlalchemy database
    model inside the request context. The permission is tested hierarchically.
    First the *user*, second the *group* and finally the *all* permission
    level is tested.
    """
    @declared_attr
    def permission(cls):
        return db.Column(PermissionType, nullable=False, default=Permission())

    @declared_attr
    def user_id(cls):
        return db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    @declared_attr
    def user(cls):
        return db.relationship('User')

    @declared_attr
    def group_id(cls):
        return db.Column(db.Integer, db.ForeignKey('group.id'), nullable=False)

    @declared_attr
    def group(cls):
        return db.relationship('Group')

    def readable(self):
        """Return the read access of the current user."""
        user = object.__getattribute__(self, 'user')
        group = object.__getattribute__(self, 'group')
        permission = object.__getattribute__(self, 'permission')
        if user == current_user and permission.user_readable:
            return True
        if ((group == current_user.primary_group or
             group in current_user.groups) and
             permission.group_readable):
            return True
        if permission.all_readable:
            return True
        return False

    def writeable(self):
        """Return the write access of the current user."""
        user = object.__getattribute__(self, 'user')
        group = object.__getattribute__(self, 'group')
        permission = object.__getattribute__(self, 'permission')
        if user == current_user and permission.user_writeable:
            return True
        if ((group == current_user.primary_group or
             group in current_user.groups) and
             permission.group_writeable):
            return True
        if permission.all_writeable:
            return True
        return False

    def __getattribute__(self,name):
        """intercepts column read access."""
        get = lambda x: object.__getattribute__(self, x)
        if _request_ctx_stack.top:
            columns = object.__getattribute__(self, '__table__').columns.keys()
            if name in columns and not get('readable')():
                raise PermissionError('read access denied')
        return object.__getattribute__(self, name)

    def __setattr__(self, name, value):
        """intercepts column write access."""
        get = lambda x: object.__getattribute__(self, x)
        if _request_ctx_stack.top:
            columns = object.__getattribute__(self, '__table__').columns.keys()
            if name in columns and not get('writeable')():
                raise PermissionError('write access denied')
        object.__setattr__(self, name, value)


class User(db.Model, UserMixin):
    """Handles the usernames, passwords and the login status"""
    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.Integer, db.ForeignKey('group.id'), nullable=False)
    name = db.Column(db.String(60), nullable=False, unique=True)
    _hashed_pw = db.Column(db.String(60), nullable=False)

    primary_group = db.relationship('Group')

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
    """Used for unix-style access control."""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(60), nullable=False)
    users = db.relationship('User', secondary=_usergroup_table,
                            backref='groups')

    def __repr__(self):
        return '<Group({0},{1})>'.format(self.id, self.name)


@login_manager.user_loader
def load_user(userid):
    """User loader callback neccessary for flask-login"""
    return User.query.get(int(userid))
