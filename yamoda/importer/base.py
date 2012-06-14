#  -*- coding: utf-8 -*-
#
# yamoda, (c) 2012, see AUTHORS.  Licensed under the GNU GPL.

"""
Base class and utilities for importers.
"""

import os
from os import path
from datetime import datetime

from sqlalchemy.orm.exc import NoResultFound

from yamoda.server import db
from yamoda.server.database import Parameter, Data, Entry


class ReadFailed(Exception):
    """Raised when an importer cannot import one or more files."""


class MissingInfo(Exception):
    """Raised when an importer requires more information from the user
    in order to continue.
    """

    def __init__(self, parameters):
        self.parameters = parameters
        Exception.__init__(self, parameters)


class ImportEntry(object):
    """An entry as imported from a file, not yet with parameter
    instances assigned.
    """

    def __init__(self, name, value, unit=None):
        self.name = name
        self.value = value
        self.unit = unit

    def __repr__(self):
        return 'ImportEntry(%r, %r, %r)' % (self.name, self.value, self.unit)


class ImporterBase(object):
    """Base class for data importers.

    Subclasses need to implement the read_file() method.
    """

    def __init__(self, ctx, baseset):
        self.ctx = ctx
        self.baseset = baseset

    def import_items(self, *names):
        for name in names:
            # recursively import from subdirectories
            if path.isdir(name):
                self.import_items([path.join(name, sub)
                                   for sub in os.listdir(name)])
            elif path.isfile(name):
                # XXX support zipfiles?
                self.import_file(name)
            else:
                raise ReadFailed('could not handle path %r' % name)

    def import_file(self, filename):
        # default implementation: one file is one data
        entries = self.read_file(filename)
        data = self.process_entries(entries)
        self.baseset.datas.append(data)

    def read_file(self, filename):
        raise NotImplementedError('%s.read_file must be implemented' %
                                  self.__class__.__name__)

    def process_entries(self, entries):
        kwds = {'name': '(unnamed)'}
        if '__name__' in entries:
            kwds['name'] = entries.pop('__name__').value
        if '__created__' in entries:
            kwds['created'] = entries.pop('__created__').value
        data = Data(**kwds)
        for ent in entries.itervalues():
            try:
                param = Parameter.query.filter_by(name=ent.name,
                                                  context=self.ctx).one()
            except NoResultFound:
                # for testing:
                param = Parameter(name=ent.name, context=self.ctx, unit=ent.unit)
                db.session.add(param)
                db.session.commit()
                #raise MissingInfo('parameter %s' % ent.name)  # XXX format of errors
            else:
                assert param.unit == ent.unit  # XXX
            if isinstance(ent.value, float):
                data.entries.append(Entry(parameter=param, value=ent.value))
            else:
                data.entries.append(Entry(parameter=param, value_complex=ent.value))
        return data
