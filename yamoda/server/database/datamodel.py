#  -*- coding: utf-8 -*-
#
# yamoda, (c) 2012, see AUTHORS.  Licensed under the GNU GPL.

"""
The database module contains all database models.

Classes:
--------
Set   -- Used to group Datas
Data  -- represents a Datafile
Entry -- Contains a single information of a Datafile, e.g the Sample
         Temperature
Context   -- The Context class is used to group several parameters
Parameter -- Describes a Entry instance
DescriptionMixin -- Mixin class, which adds a brief and a long description column

"""

from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.sql.expression import func

from yamoda.server import db
from yamoda.server.database.accesscontrol import User, Group, AccessControl


class TimeStamp(object):
    """A simple timestamp mixin"""
    @declared_attr
    def created(cls):
        return db.Column(db.DateTime, default=func.now(), nullable=False)


_set_to_data = db.Table('set_to_data', db.Model.metadata,
    db.Column('set_id',  db.Integer, db.ForeignKey('set.id')),
    db.Column('data_id', db.Integer, db.ForeignKey('data.id')))


_set_to_set = db.Table('set_to_set', db.Model.metadata,
    db.Column('child_id' , db.Integer, db.ForeignKey('set.id'), primary_key=True),
    db.Column('parent_id', db.Integer, db.ForeignKey('set.id'), primary_key=True))


class Set(AccessControl, TimeStamp, db.Model):
    """The Set class is used to group Datas and other Sets"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(60), nullable=False)
    datas = db.relationship('Data', secondary=_set_to_data, backref='sets')
    children = db.relationship('Set', secondary=_set_to_set,
                               primaryjoin=id==_set_to_set.c.child_id,
                               secondaryjoin=id==_set_to_set.c.parent_id)

    def __repr__(self):
        return '<DataSet({0})>'.format(self.id)


class Data(db.Model, TimeStamp):
    """A Data is a collection of Entries"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(60), nullable=False)
    entries = db.relationship('Entry', backref='data')
    context_id = db.Column(db.Integer, db.ForeignKey('context.id'), nullable=False)
    context = db.relationship('Context')

    def __repr__(self):
        return '<Data({0})>'.format(self.id)


class Entry(db.Model, TimeStamp):
    """And Entry is a single bit of information (scalar or array) in a Data"""
    id = db.Column(db.Integer, primary_key=True)
    data_id = db.Column(db.Integer, db.ForeignKey('data.id'))
    parameter_id = db.Column(db.Integer, db.ForeignKey('parameter.id'), nullable=False)

    @hybrid_property
    def value(self):
        if self.value_float is None:
            return self.value_complex
        return self.value_float

    @value.setter
    def _(self, newvalue):
        if isinstance(newvalue, float):
            self.value_float = newvalue
        else:
            self.value_complex = newvalue

    value_float = db.Column(db.Float)
    value_complex = db.Column(db.PickleType)

    parameter = db.relationship('Parameter')

    def __repr__(self):
        if self.value is not None:
            return '<Entry({0},{1},{2})>'.format(self.id, self.parameter.name,
                                                 self.value)
        return '<Entry({0},{1},{2!r})>'.format(self.id, self.parameter.name,
                                               self.value_complex)


class DescriptionMixin(object):
    """Mixin class, which adds a brief and a long description column"""
    brief = db.Column(db.String(80))
    description = db.Column(db.Text)


# TODO: add hierarchical structure to Parameters (e.g. groups)
class Context(db.Model, DescriptionMixin):
    """The Context class is used to group several parameters"""
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(60))
    name = db.Column(db.String(60), unique=True)

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

    def __repr__(self):
        return '<Parameter({0})>'.format(self.name)
