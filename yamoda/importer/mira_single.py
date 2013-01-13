#  -*- coding: utf-8 -*-
#
# yamoda, (c) 2012, see AUTHORS.  Licensed under the GNU GPL.

"""
Importer for MIRA single counter data.
"""

import time
import textwrap
from os import path
from datetime import datetime

import numpy

from yamoda.importer.base import ImporterBase, ParsingError, ImportEntry
from yamoda.server.database import Context, Parameter


def try_float(s):
    try:
        return float(s)
    except ValueError:
        return s


class Importer(ImporterBase):
    def __init__(self, target):
        super(Importer, self).__init__('Mira singlecounter', target)

    def read_file(self, filename, original):
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
                key = items[1]
                if line.endswith(' ') or key.endswith('_status'):
                    val = try_float(items[3])
                    unit = None
                else:
                    try:
                        val, unit = items[3].rsplit(None, 1)
                    except ValueError:
                        val = try_float(items[3])
                        unit = None
                    else:
                        val = try_float(val)
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
        mira_brief = 'Data from MIRA single-counter data files.'
        mira_desc = textwrap.dedent('''\
        The MIRA all-purpose instrument at the FRM II.

        This context is for data measured using a single counter, as opposed to
        a PSD detector.
        ''')
        mira_single = Context(name='Mira singlecounter', brief=mira_brief,
                              description=mira_desc)
        for parname, (parbrief, parunit) in MIRA_PARAMS.iteritems():
            par_value = Parameter(name=parname, brief=parbrief, unit=parunit)
            par_status = Parameter(name=parname + '_status',
                                   brief='Status of %s' % parname)
            par_offset = Parameter(name=parname + '_offset',
                                   brief='Offset of %s' % parname, unit=parunit)
            par_precision = Parameter(name=parname + '_precision',
                                      brief='Precision of %s' % parname,
                                      unit=parunit)
            mira_single.parameters.extend([par_value, par_status,
                                           par_offset, par_precision])
        return mira_single


MIRA_PARAMS = {
    'mth':  ('MIRA1 Monochromator theta angle'       , 'deg'),
    'mtt':  ('MIRA1 Monochromator two-theta angle'   , 'deg'),
    'mgx':  ('MIRA1 Monochromator tilt'              , 'deg'),
    'mtx':  ('MIRA1 Monochromator translation X'     , 'mm'),
    'mty':  ('MIRA1 Monochromator translation Y'     , 'mm'),
    'm2th': ('MIRA2 Monochromator theta angle'       , 'deg'),
    'm2tt': ('MIRA2 Monochromator two-theta angle'   , 'deg'),
    'm2gx': ('MIRA2 Monochromator tilt'              , 'deg'),
    'm2tx': ('MIRA2 Monochromator translation X'     , 'mm'),
    'm2ty': ('MIRA2 Monochromator translation Y'     , 'mm'),
    'mono': ('Monochromator (ki)'                    , 'A-1'),
    'om':   ('Sample theta angle'                    , 'deg'),
    'phi':  ('Sample two-theta angle'                , 'deg'),
    'sgx':  ('Sample goniometer around X axis'       , 'deg'),
    'sgy':  ('Sample goniometer around Y axis'       , 'deg'),
    'stx':  ('Sample translation X (along the beam)' , 'mm'),
    'sty':  ('Sample translation Y (horizontal)'     , 'mm'),
    'stz':  ('Sample translation Z (vertical)'       , 'mm'),
    'srot': ('Sample rotation inside cryostat'       , 'deg'),
    'ath':  ('Analyser theta angle'                  , 'deg'),
    'att':  ('Analyser two-theta angle'              , 'deg'),
    'ana':  ('Analyser (kf)'                         , 'A-1'),
    'mira': ('MIRA triple-axis device'               , 'rlu/meV'),
    'ms2':  ('Slit after the monochromator'          , 'mm'),
    'ss1':  ('Sample slit 1'                         , 'mm'),
    'ss2':  ('Sample slit 2'                         , 'mm'),
    'T':    ('Sample temperature'                    , 'K'),
    'I':    ('Current in electromagnet'              , 'A'),
    'B':    ('Magnetic field'                        , 'T'),
}
