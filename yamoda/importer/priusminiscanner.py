#  -*- coding: utf-8 -*-
#
# yamoda, (c) 2012, see AUTHORS.  Licensed under the GNU GPL.

'''
Created on 3.11.2012
@author: dpausp (Tobias Stenzel)

Import Prius miniscanner data (an importer just for me ;))
'''

import time
import textwrap
from os import path
import re
from datetime import datetime

import numpy as np

from yamoda.importer.base import ImporterBase, ParsingError, ImportEntry
from yamoda.server.database import Context, Parameter


PARAMETER_LINE_RE = re.compile("# Parameter (\d): (.+) \((.+)\)")
DATA_LINE_RE = re.compile(" (\d+\.\d\d\d)(\t+)(.+)")


class Importer(ImporterBase):
    def __init__(self, target):
        super(Importer, self).__init__('Prius Miniscanner', target)

    def read_file(self, filename, original):
        parameter_values = {}
        parameter_timestamps = {}
        parameter_units = {}
        current_parameters = {}
        fp = open(filename)
        dtline = fp.readline()
        # check marker comment which has to be the first line in the file
        if not dtline.startswith('### Miniscanner data file'):
            raise ParsingError(
                '{0!r} does not appear to be a Miniscanner data file'.format(filename))

        for linenum, line in enumerate(fp):
            if line.startswith('# Parameter'):
                # read parameter line and add new parameter
                match = PARAMETER_LINE_RE.match(line)
                parameter_pos, parameter_name, parameter_unit = match.groups()
                current_parameters[int(parameter_pos)] = parameter_name
                parameter_values.setdefault(parameter_name, [])
                parameter_timestamps.setdefault(parameter_name, [])
                parameter_units[parameter_name] = parameter_unit

            elif not line.strip() or line.startswith('# '):
                continue

            else:
                match = DATA_LINE_RE.match(line)
                if match is None:
                    raise ParsingError("invalid line {}: {}".format(linenum, line))
                timestamp, tabs, value = match.groups()
                parameter_pos = len(tabs)
                if value.startswith(":"):
                    # is a temperature value starting with :
                    value = value[1:]
                try:
                    conv_value = float(value)
                except:
                    raise ParsingError("invalid value in line {}: {} at time %s".format(linenum, value, timestamp))

                parameter_name = current_parameters[parameter_pos]
                parameter_timestamps[parameter_name].append(float(timestamp))
                parameter_values[parameter_name].append(conv_value)

        # build entries
        entries = {}
        for name, values in parameter_values.iteritems():
            unit = parameter_units[name]
            timestamps = parameter_timestamps[name]
            entries[name + "_time"] = ImportEntry(name=name + "_time", value=np.array(timestamps), unit="s")
            entries[name] = ImportEntry(name=name, value=np.array(values), unit=unit)
        return entries

    @classmethod
    def default_context(cls):
        """Creates a `Miniscanner` context object."""
        brief = 'Data from annotated Prius miniscanner data files.'
        desc = textwrap.dedent('''\
        Data from the Prius Miniscanner by Graham Davies
        ''')
        context = Context(name='Prius Miniscanner', brief=brief,
                              description=desc)
        for parname, (parbrief, parunit) in MINISCANNER_PARAMS.iteritems():
            par_timestamp = Parameter(name=parname + '_time', unit="s")
            par_value = Parameter(name=parname, brief=parbrief, unit=parunit)
            context.parameters.append(par_timestamp)
            context.parameters.append(par_value)
        return context


MINISCANNER_PARAMS = {
    'MG2 Spin': ('MG2 Spin', '1/min'),
    'Requested Power': ('Requested Power', 'kW'),
    'Battery Current': ('Battery Current', 'A'),
    'Battery SOC': ('Battery SOC', '%')
}
