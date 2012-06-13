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
from sqlalchemy.orm.util import _entity_descriptor
from sqlalchemy.sql import and_, or_
from flask import _request_ctx_stack
from flask.ext.login import UserMixin, current_user
from flask.ext.sqlalchemy import BaseQuery
import bcrypt

from yamoda.server import db, login_manager


class PermissionError(Exception):
    """Raised when a row level access is denied."""
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)

def _bit_property(bit, name='permission'):
    """creates hybrid property to set and get a *name* col."""
    #: Helper fn to bypass Accesscontrol.__getattribute__
    attr = lambda self: object.__getattribute__(self, name)

    #: Helper fn to bypass Accesscontrol.__setattr__
    set_attr = lambda self, value: object.__setattr__(self, name, value)

    def _get(self):
        """Gets the *bit* bit."""
        return bool(attr(self) & (1 << bit))

    def _exp(self):
        """Gets the bit on DB side.(SQLAlchemy treats *&* as logical *and*)"""
        return attr(self).op('&')(1 << bit) != 0

    def _set(self, value):
        """Sets the *bit* bit dependant on value."""
        if value: #set bit
            set_attr(self, attr(self) | (1 << bit))
        else: #clear bit
            set_attr(self, attr(self) & (~(1 << bit)))
    return hybrid_property( _get, _set, expr=_exp)


class AccessControlledQuery(BaseQuery):
    """Custom query class, allowing access control filtered queries.

    The AccessControlledQuery class enhances the flask-sqlalchemy query class
    with several access control filtered queries. Since the access control is
    checked on the database side, checks on the python side aren't neccessary
    anymore.
    
    """

    def _filter(self,access):
        """filter the query.

        _filter filters the query the same way the AccessControl
        class does inside the readable()/writeable() function. But the
        filtering is done on the DB side.

        """
        if access == 'read':
            (usr, grp, all) = ('user_readable', 'group_readable',
                               'all_readable')
        elif access == 'write':
            (usr, grp, all) = ('user_writeable', 'group_writeable',
                               'all_writeable')
        else:
            raise ValueError

        clause = lambda name: _entity_descriptor(self._joinpoint_zero(), name)
        cu_grps = [current_user.group_id]+[g.id for g in current_user.groups]
        return self.filter( or_(
            and_(clause(usr)==True, clause('user_id') == current_user.id),
            and_((grp) ==  True, clause('group_id').in_(cu_grps)),
            and_(clause(all)==True)))

    def all_readable(self):
        return self._filter('read').all()

    def all_writeable(self):
        return self._filter('write').all()

    def first_readable(self):
        return self._filter('read').first()

    def first_writeable(self):
        return self._filter('write').first()

    def get_readable(self, ident):
        """gets the row if it's readable, returns None otherwise"""
        row = self.query.get(ident)
        return row if row.readable() else None

    def get_writeable(self, ident):
        """gets the row if it's writeable, returns None otherwise"""
        row = self.query.get(ident)
        return row if row.writeable() else None


class AccessControl(object):
    """Mixin class, adding row level security to the database model.

    The AccessControl mixin adds row level security to a sqlalchemy database
    model inside the request context. The permission is tested hierarchically.
    First the *user*, second the *group* and finally the *all* permission
    level is tested.

    Note:
    -----
    The AccessControl Mixin should be the first baseclass, otherwise it's not
    guaranteed that the __init__ method is called.

    """
    #: Custom query class, allowing access control filtered queries.
    query_class = AccessControlledQuery

    def __init__(self, *args, **kw):
        """AccessControl constructor.

        Constructs the AccessControl mixin. The permission is set to 0b011111,
        which corresponds to user/group/all readable and user/group writeable.

        Note:
        -----
        The AccessControl constructor uses the cooperative multiple 
        inheritance pattern to call the next initializer.

        """
        self.permission = kw.pop('permission',0b011111)    
        super(AccessControl, self).__init__(*args, **kw)

    @declared_attr
    def permission(cls):
        """Stores User/Group/All read & write permissions.

        The Permission column stores read and write permissions for User,
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
        return db.Column(db.Integer, nullable=False)

    @declared_attr
    def user_id(cls):
        """Stores the id of the owning user"""
        return db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    @declared_attr
    def user(cls):
        """Relation with the owning user"""
        return db.relationship('User')

    @declared_attr
    def group_id(cls):
        """Stores the id of the owning group"""
        return db.Column(db.Integer, db.ForeignKey('group.id'), nullable=False)

    @declared_attr
    def group(cls):
        """Relation with the owning group"""
        return db.relationship('Group')

    def access(self, access='read'):
        """calculates the read/write access of the current user.

        The access member function determines the read/write access of the 
        current user. It is evaluated in a hirarchical fashion, first the
        *user*, followed by the *group* and finally the *all* access. Outside
        of a request context complete access is granted.
        
        Keyword arguments:
        ------------------
        :access: Determines if read or write permission is calculated. Valid
                 values are "read" or "write".

        """
        if access == 'read':
            (usr, grp, all) = ('user_readable', 'group_readable',
                               'all_readable')
        elif access == 'write':
            (usr, grp, all) = ('user_writeable', 'group_writeable',
                               'all_writeable')
        else:
            raise ValueError
        if _request_ctx_stack.top is None:
            return True
        get = lambda x: object.__getattribute__(self, x)
        user = object.__getattribute__(self, 'user')
        group = object.__getattribute__(self, 'group')
        cu_groups = [current_user.primary_group] + current_user.groups

        if ((get(usr) and user == current_user) or 
            (get(grp) and group in cu_groups) or get(all)):
            return True
        return False

    def readable(self):
        """Return the read access of the current user."""
        return self.access('read')

    def writeable(self):
        """Return the write access of the current user."""
        return self.access('write')

    def __getattribute__(self,name):
        """Intercepts column read access."""
        get = lambda x: object.__getattribute__(self, x)
        if _request_ctx_stack.top:
            columns = get('__table__').columns.keys()
            if name in columns and not get('readable')():
                raise PermissionError('read access denied: {0}'.format(name))

        return object.__getattribute__(self, name)

    def __setattr__(self, name, value):
        """Intercepts column write access."""
        get = lambda x: object.__getattribute__(self, x)
        if _request_ctx_stack.top:
            columns = get('__table__').columns.keys()
            if name in columns and not get('writeable')():
                raise PermissionError('write access denied: {0}'.format(name))
        object.__setattr__(self, name, value)

    #: Hybrid property, wrapping the user_readable bit.
    user_readable = _bit_property(0)

    #: Hybrid property, wrapping the group_readable bit.
    group_readable = _bit_property(1)

    #: Hybrid property, wrapping the all_readable bit.
    all_readable = _bit_property(2)

    #: Hybrid property, wrapping the user_writeable bit.
    user_writeable = _bit_property(3)

    #: Hybrid property, wrapping the user_writeable bit.
    group_writeable = _bit_property(4)

    #: Hybrid property, wrapping the all_writeable bit.
    all_writeable = _bit_property(5)


#: Helper table, neccessary for User-Group relationship.
_usergroup_table = db.Table('usergroup_table', db.metadata,
    db.Column('user_id',  db.Integer, db.ForeignKey('user.id')),
    db.Column('group_id', db.Integer, db.ForeignKey('group.id')))


class User(db.Model, UserMixin):
    """Handles the usernames, passwords and the login status."""
    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.Integer, db.ForeignKey('group.id'), nullable=False)
    name = db.Column(db.String(60), nullable=False, unique=True)
    _hashed_pw = db.Column(db.String(60), nullable=False)

    primary_group = db.relationship('Group')

    @hybrid_property
    def password(self):
        """Returns the stored bcrypt hash."""
        return self._hashed_pw

    @password.setter
    def password(self, value):
        """Calculates the bcrypt hash and stores it."""
        self._hashed_pw = bcrypt.hashpw(value, bcrypt.gensalt())

    def valid_password(self, password):
        """Compares the bcrypt hash of password with the stored hash."""
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
