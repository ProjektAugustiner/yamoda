#  -*- coding: utf-8 -*-
#
# yamoda, (c) 2012, see AUTHORS.  Licensed under the GNU GPL.

"""
Base class and utilities for importers.
"""

import os
from os import path

from sqlalchemy.orm.exc import NoResultFound
import quantities as pq

from yamoda.server import db
from yamoda.server.database import Context, Parameter, Data, Entry


class ImporterError(Exception):
    """Base Exception of the Importer module."""


class ParsingError(ImporterError):
    """Raised when the parsing of a file fails."""


class InvalidPathError(ImporterError):
    def __init__(self, path):
        super(InvalidPathError, self).__init__(
            'Could not handle path {0}'.format(path))


class UnitMismatchError(ImporterError):
    """Raised in case of a unit mismatch."""
    def __init__(self, entry, expected_unit, received_unit):
        super(UnitMismatch, self).__init__(
            'In entry {0}: expected unit {1} got {2}'.format(entry, 
            expected_unit, received_unit))


class MissingInfo(ImporterError):
    """Raised when an importer requires more information from the user
    in order to continue.

    *info* is a list of tuples ``(key, type, ...)``, where the rest of the
    entries depends on the type.

    """
    def __init__(self, info):
        self.info = info
        super(MissingInfo, self).__init__(info)


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

    .. note::
       
       Subclasses need to implement the following methods:

        * read_file()
        * default_context()

    """

    def __init__(self, ctx, target):
        """Constructor.

        Args:
            ctx (str, Context):  A Context object or the name of the Context in
                                 the db.
            target (Set):  The target set, where the data should be imported.

        """
        if isinstance(ctx, basestring):
            ctx = Context.query.filter_by(name=ctx).first()
            if ctx is None:
                # XXX possible race condition?
                ctx = self.default_context()
                db.session.add(ctx)
                db.session.commit()
        
        self.ctx = ctx
        self.target = target

    @classmethod
    def default_context(cls):
        raise NotImplementedError('{0}.default_context must be implemented'.format(
                                  cls.__name__))
        
    def import_items(self, names, userinfo):
        imported = []
        for name in names:
            # recursively import from subdirectories
            if path.isdir(name):
                items = [path.join(name, sub) for sub in os.listdir(name)]
                imported.extend(self.import_items(items, userinfo))
            elif path.isfile(name):
                # XXX support zipfiles?
                imported.extend(self.import_file(name, userinfo))
            else:
                raise InvalidPathError(name)
        return imported

    def import_file(self, filename, userinfo):
        # default implementation: one file is one data
        entries = self.read_file(filename)
        data = self.process_entries(entries, userinfo)
        self.target.datas.append(data)
        return [data]

    def read_file(self, filename):
        raise NotImplementedError('{0}.read_file must be implemented'.format(
                                  self.__class__.__name__))

    def process_entries(self, entries, userinfo):
        kwds = {'name': '(unnamed)', 'context': self.ctx}
        if '__name__' in entries:
            kwds['name'] = entries.pop('__name__').value
        if '__created__' in entries:
            kwds['created'] = entries.pop('__created__').value
        data = Data(**kwds)
        missing_params = []
        for ent in entries.itervalues():
            param = self._get_param(entry=ent, userinfo=userinfo)
            if param is None:
                missing_params.append((ent.name, ent.unit))
                continue
            if param.unit != ent.unit:
                try:
                    ent.value = self._convert_unit(ent.value, ent.unit,
                                                   param.unit)
                except ValueError:
                    raise UnitMismatchError(ent.name, param.unit, ent.unit)
            data.entries.append(Entry(parameter=param, value=ent.value))
        if missing_params:
            raise MissingInfo([('par_' + param, 'new_param', unit)
                               for (param, unit) in missing_params])
        return data
           
    def _get_param(self, entry, userinfo):
        """Tries to get the param from the db or to create it otherwise.

        Args:
          entry (ImportEntry):  The import entry, whose corresponding parameter
                                should be returned.
          userinfo (dict):  A dictionairy containing all neccessary keywords
                            for parameter creation

        Returns:
          Parameter, None.  The requested parameter or None in case of failure.
        
        """
        name = entry.name
        try:
            param = Parameter.query.filter_by(name=name,
                                              context=self.ctx).one()
        except NoResultFound:
            if not ('par_' + name) in userinfo:
                return None
            kw = userinfo['par_' + name]
            unit = kw.pop('unit', entry.unit)
            # XXX possible race condition?
            param = Parameter(name=name, context=self.ctx, unit=unit, **kw)
            db.session.add(param)
            db.session.flush()
        return param
            
    def _convert_unit(value, from_unit, to_unit):
        """Performs a unit conversion of value.

        Args:
          value:  The value to convert.
          from_unit (str):  The unit string of the value.
          to_unit (str):  The string representation of the target unit.

        Returns:
          type(value).  The converted value.

        Raises:
          ValueError

        """
        pq.Quantity(value, from_unit)
        return x.rescale(to_unit).item()
