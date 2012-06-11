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
from yamoda.server import db
from yamoda.server.database.accesscontrol import User, Group, AccessControl


_set_to_data = db.Table('set_to_data', db.Model.metadata,
    db.Column('set_id',  db.Integer, db.ForeignKey('set.id')),
    db.Column('data_id', db.Integer, db.ForeignKey('data.id')))


_set_to_set = db.Table('set_to_set', db.Model.metadata,
    db.Column('child_id' , db.Integer, db.ForeignKey('set.id'), primary_key=True),
    db.Column('parent_id', db.Integer, db.ForeignKey('set.id'), primary_key=True))


class Set(db.Model, AccessControl):
    """The Set class is used to group Datas and other Sets"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(60))
    created = db.Column(db.DateTime, nullable=False)
    datas = db.relationship('Data', secondary=_set_to_data, backref='sets')
    children = db.relationship('Set', secondary=_set_to_set,
                               primaryjoin=id==_set_to_set.c.child_id,
                               secondaryjoin=id==_set_to_set.c.parent_id)

    def __repr__(self):
        return '<DataSet({0})>'.format(self.id)


class Data(db.Model):
    """A Data is a collection of Entries"""
    id = db.Column(db.Integer, primary_key=True)
    created = db.Column(db.DateTime, nullable=False)
    entries = db.relationship('Entry', backref='data')

    def __repr__(self):
        return '<Data({0})>'.format(self.id)


class Entry(db.Model):
    """And Entry is a single bit of information (scalar or array) in a Data"""
    id = db.Column(db.Integer, primary_key=True)
    data_id = db.Column(db.Integer, db.ForeignKey('data.id'))
    parameter_id = db.Column(db.Integer, db.ForeignKey('parameter.id'), nullable=False)
    value = db.Column(db.Float)
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
