#  -*- coding: utf-8 -*-
#
# yamoda, (c) 2012, see AUTHORS.  Licensed under the GNU GPL.

"""
The database module contains all database models.

Classes:
--------
User  -- Handles the usernames, passwords and login status
Group -- Used for unix-style access control
Set   -- Used to group Datas
Data  -- represents a Datafile
Entry -- Contains a single information of a Datafile, e.g the Sample
         Temperature
Context   -- The Context class is used to group several parameters
Parameter -- Describes a Entry instance
DescriptionMixin -- Mixin class, which adds a brief and a long description column

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


_set_to_data = db.Table('set_to_data', db.Model.metadata,
    db.Column('set_id',  db.Integer, db.ForeignKey('set.id')),
    db.Column('data_id', db.Integer, db.ForeignKey('data.id')))


_set_to_set = db.Table('set_to_set', db.Model.metadata,
    db.Column('child_id' , db.Integer, db.ForeignKey('set.id'), primary_key=True),
    db.Column('parent_id', db.Integer, db.ForeignKey('set.id'), primary_key=True))


class Set(db.Model):
    """The Set class is used to group Datas and other Sets"""
    id = db.Column(db.Integer, primary_key=True)
    datas = db.relationship('Data', secondary=_set_to_data, backref='sets')
    children = db.relationship('Set', secondary=_set_to_set,
                               primaryjoin=id==_set_to_set.c.child_id,
                               secondaryjoin=id==_set_to_set.c.parent_id)

    def __repr__(self):
        return '<DataSet({0})>'.format(self.id)


class Data(db.Model):
    """A Data is a collection of Entries"""
    id = db.Column(db.Integer, primary_key=True)
    entries = db.relationship('Entry', backref='data')

    def __repr__(self):
        return '<Data({0})>'.format(self.id)


class Entry(db.Model):
    """And Entry is a single bit of information (scalar or array) in a Data"""
    id = db.Column(db.Integer, primary_key=True)
    data_id = db.Column(db.Integer, db.ForeignKey('data.id'))
    parameter_id = db.Column(db.Integer, db.ForeignKey('parameter.id'), nullable=False)
    value = db.Column(db.PickleType)

    parameter = db.relationship('Parameter')

    #def __init__(self, value, parameter_id):
    #    self.value = value
    #    self.parameter_id = parameter_id

    def __repr__(self):
        return '<Entry({0},{1},{2})>'.format(self.id,self.value,self.parameter_id)


class DescriptionMixin(object):
    """Mixin class, which adds a brief and a long description column"""
    brief = db.Column(db.String(80))
    description = db.Column(db.Text)


# TODO: add hierarchical structure to Parameters (e.g. groups)
class Context(db.Model, DescriptionMixin):
    """The Context class is used to group several parameters"""
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(60))
    name = db.Column(db.String(60))

    parameters = db.relationship('Parameter', backref='context')

    __mapper_args_ = {
        'polymorphic_identity': 'context',
        'polymorphic_on': type,
    }


class Parameter(db.Model, DescriptionMixin):
    """Describes a Entry instance"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(60))
    context_id = db.Column(db.Integer, db.ForeignKey('context.id'))
    visible = db.Column(db.Boolean)
    unit = db.Column(db.String(60))  # TODO: decide on a Unit table
