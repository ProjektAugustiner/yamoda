#  -*- coding: utf-8 -*-
#
# yamoda, (c) 2012, see AUTHORS.  Licensed under the GNU GPL.

"""
Importer for MIRA single counter data.
"""

import time

import numpy

from yamoda.importer.base import ImporterBase, ReadFailed, \
     ImportEntry


class Importer(ImporterBase):

    def read_file(self, filename):
        entries = []
        fp = open(filename, 'rb')
        dtline = fp.readline()
        if not dtline.startswith('### NICOS data file'):
            raise ReadFailed('%r does not appear to be a NICOS data file' %
                               filename)
        entries.append(ImportEntry(name='created', value=time.mktime(time.strptime(
            dtline[len('### NICOS data file, created at '):].strip(),
            '%Y-%m-%d %H:%M:%S'))))
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
                entries.append(ImportEntry(name=key, value=val, unit=unit))
        colnames = fp.readline()[1:].split()
        colunits = fp.readline()[1:].split()
        def convert_value(s):
            try:
                return float(s)
            except ValueError:
                return 0.0  # XXX care for string columns?!
        cvdict = dict((i, convert_value) for i in range(len(colnames))
                      if colnames[i] != ';')
        usecols = cvdict.keys()
        coldata = numpy.loadtxt(fp, converters=cvdict, usecols=usecols, unpack=True)
        for (name, unit, data) in zip(colnames, colunits, coldata):
            entries.append(ImportEntry(name=name, value=data, unit=unit))
        return entries
