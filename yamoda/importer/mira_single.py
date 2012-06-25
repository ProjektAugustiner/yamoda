#  -*- coding: utf-8 -*-
#
# yamoda, (c) 2012, see AUTHORS.  Licensed under the GNU GPL.

"""
Importer for MIRA single counter data.
"""

import time
from os import path
from datetime import datetime

import numpy

from yamoda.importer.base import ImporterBase, ParsingError, ImportEntry
from yamoda.server.database import Context, Parameter
    

class Importer(ImporterBase):
    def __init__(self, target):
        super(Importer, self).__init__('Mira singlecounter', target)

    def read_file(self, filename):
        entries = {}
        fp = open(filename, 'rb')
        dtline = fp.readline()
        if not dtline.startswith('### NICOS data file'):
            raise ParsingError(
                '{0!r} does not appear to be a NICOS data file'.format(filename))
        ctime = time.mktime(time.strptime(
            dtline[len('### NICOS data file, created at '):].strip(),
            '%Y-%m-%d %H:%M:%S'))
        entries['created'] = ImportEntry(name='created', value=ctime)
        entries['__created__'] = ImportEntry(name='created',
                                             value=datetime.fromtimestamp(ctime))
        for line in iter(fp.readline, ''):
            if line.startswith('### Scan data'):
                break
            if line.startswith('# '):
                items = line.strip().split(None, 3)
                try:
                    val, unit = items[3].split(None, 1)
                    val = float(val)
                except ValueError:
                    try:
                        val = float(items[3])
                    except ValueError:
                        val = items[3]
                    unit = None
                key = items[1]
                if key.endswith('_value'):
                    key = key[:-6]
                entries[key] = ImportEntry(name=key, value=val, unit=unit)
        if 'filename' in entries:
            basename = path.splitext(entries['filename'].value)[0]
            entries['__name__'] = ImportEntry(name='name', value=basename)
        colnames = fp.readline()[1:].split()
        colunits = fp.readline()[1:].split()
        def convert_value(s):
            try:
                return float(s)
            except ValueError:
                return 0.0  # XXX care for string columns?!
        cvdict = dict((i, convert_value) for i in range(len(colnames))
                      if colnames[i] != ';')
        colnames = [name for name in colnames if name != ';']
        colunits = [unit for unit in colunits if unit != ';']
        usecols = cvdict.keys()
        coldata = numpy.loadtxt(fp, converters=cvdict,
                                usecols=usecols, unpack=True)
        for (name, unit, data) in zip(colnames, colunits, coldata):
            entries[name] = ImportEntry(name=name, value=data, unit=unit)
        return entries

    @classmethod
    def default_context(cls):
        """Creates a `Mira singlecounter` context object."""
        # TODO Implement complete context initialisation.
        mira_brief = 'Mira singlecounter.'
        mira_single = Context(name='Mira singlecounter', brief=mira_brief)
        return mira_single
