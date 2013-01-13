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
        super(UnitMismatchError, self).__init__(
            'In entry {0}: expected unit {1}, got {2}'.format(entry,
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

        :param ctx:  A Context object or the name of the Context in the db.
        :param target:  The target set, where the data should be imported.
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

    def import_items(self, names, orig_names, userinfo):
        """Import file(s).

        :param names:  A list of file or directory names.
        :param orig_names:  A list of corresponding original file names.
        :param userinfo:  A dictionary with user-supplied info.
        :returns:  A list of newly-created Data instances.
        """
        imported = []
        for name, orig in map(None, names, orig_names):
            # recursively import from subdirectories
            if path.isdir(name):
                items = [path.join(name, sub) for sub in os.listdir(name)]
                imported.extend(self.import_items(items, items, userinfo))
            elif path.isfile(name):
                # XXX support zipfiles?
                imported.extend(self.import_file(name, orig, userinfo))
            else:
                raise InvalidPathError(name)
        return imported

    def import_file(self, filename, original, userinfo):
        """Import a single file."""
        # default implementation: one file is one data
        entries = self.read_file(filename, original)
        data = self.process_entries(entries, userinfo)
        self.target.datas.append(data)
        return [data]

    def read_file(self, filename, original):
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
                except (ValueError, TypeError, SyntaxError, LookupError):
                    # XXX: some units just aren't convertible by the package,
                    # such as meV/THz
                    # raise UnitMismatchError(ent.name, param.unit, ent.unit)
                    pass
            data.entries.append(Entry(parameter=param, value=ent.value))
        if missing_params:
            raise MissingInfo([('par_' + param, 'new_param', unit)
                               for (param, unit) in missing_params])
        return data

    def _get_param(self, entry, userinfo):
        """Tries to get the param from the db or to create it otherwise.

        :param entry:  The import entry whose corresponding parameter
           should be returned.
        :param userinfo:  A dictionary containing all neccessary keywords
           for parameter creation.
        :returns:  The requested Parameter or None in case of failure.
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

    def _convert_unit(self, value, from_unit, to_unit):
        """Performs a unit conversion of value.

        :param value:  The value to convert.
        :param from_unit:  The unit string of the value.
        :param to_unit:  The string representation of the target unit.
        :returns:  The converted value.
        :raises ValueError: In case of a unit conversion failure.
        """
        x = pq.Quantity(value, from_unit)
        return x.rescale(to_unit).item()
