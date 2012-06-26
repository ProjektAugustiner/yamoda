#  -*- coding: utf-8 -*-
#
# yamoda, (c) 2012, see AUTHORS.  Licensed under the GNU GPL.
"""Importer for VSM datafiles.

Classes:
----------
  Importer:  Importer for VSM datafiles.
"""
from datetime import datetime
from itertools import izip
from os import path

import numpy as np

from yamoda.importer.base import ImporterBase, ImportEntry, ParsingError
from yamoda.server.database import Context, Parameter


class Importer(ImporterBase):
    """Importer for VSM datafiles.

    VSM files follow the following syntax:

        COMMENTS
        DATETIME

        COLNAMES
        COLUNITS

        PRECISSION
        DATA

    `COMMENTS` start with a `;`, multiple `COMMENTS` per line are possible.
    The `DATETIME` follows the Syntax `day month date hh:mm:ss yyyy` e.g.
    `Wed May 23 16:11:30 2012`.

    """
    def __init__(self, target):
        super(Importer, self).__init__('VSM', target)

    def read_file(self, filename, original):
        """Parses a VSM file.

        Args:
          filename (str):  Path to the file, which should get parsed.

        Returns:
          dict.  A dictionairy holding the parsed ImportEntries.

        Raises:
          ParsingError

        """
        def assert_blank(line):
            """Tiny helper funtion checking if the line is blank."""
            if line.strip():
                raise ParsingError('Line is not blank.')
        name = path.splitext(original)[0]
        entries = {'__name__': ImportEntry(name='name', value=name),}

        with open(filename, 'rb') as f:
            for line in iter(f.readline, ''):
                if line.startswith(';'):
                    # TODO parse comments
                    continue
                else:
                    try:
                        t = datetime.strptime(line.strip(),
                                              "%a %b %d %H:%M:%S %Y")
                    except ValueError:
                        raise ParsingError('Invalid Date.')
                    entries['Date'] = ImportEntry(name='Date', value=t)
                    break

            assert_blank(f.readline())
            cols = [x.strip() for x in f.readline().split(',')]
            units = [x.strip() for x in f.readline().split(',')]
            assert_blank(f.readline())

            precission = f.readline()
            M = np.loadtxt(f)
            if not(len(cols) == len(units) == M.shape[1]):
                raise ParsingError('Column mismatch.')

            for (row, col, unit) in izip(M.T, cols, units):
                entries[col] = ImportEntry(name=col, unit=unit, value=row)
        return entries

    @classmethod
    def default_context(cls):
        """Creates and returns a default VSM context.

        Returns:
          Context.  The default context for the VSM Importer.

        """
        T1_brief = 'Temperature of the capacitance thermometer.'
        T1_desc = """\
The *T1* variable represents the temperature of the capacitance thermometer.
It's advantage is the low magnetic field dependance. It is perfectly suited for
magnetic field sweeps. It reacts slowly to large temperature changes, the
resistive thermometer *T1* and *T2* are the better alternative for temperature
sweeps.
"""
        T1 = Parameter(name='T1', brief=T1_brief, description=T1_desc,
                       unit='K')
        T2_brief = 'Temperature of the resistive thermometer.'
        T2_desc = """\
The *T2* variable represents the temperature of the resistive thermometer. It
is mounted adjacent to the *T1* thermometer. It's strength is the short
reaction time to temperature changes. It is the first choice for Temperature
Sweeps.
"""
        T2 = Parameter(name='T2', brief=T2_brief, description=T2_desc,
                       unit='K')
        T3_brief = 'Temperature of the resistive sample thermometer'
        T3_desc = """\
The *T3* variable represents the temperature of the resistive sample
thermometer. It is mounted close to the sample holder, between the inner pickup
coils, to achieve a more acurate sample Temperature.
"""
        T3 = Parameter(name='T3', brief=T3_brief, description=T3_desc,
                       unit='K')
        Tsample_brief = 'Tsample is the sample temperature (default: *T3*)'
        Tsample = Parameter(name='Tsample', brief=Tsample_brief, unit='K')
        inv_Tsample = Parameter(name='1/Tsample', unit='1/K',
                                brief='Inverse sample temperature.')
        Tset_desc = """\
*Tset* is the current target temperature used by the temperature controler.
"""
        Tset = Parameter(name='Tset', description=Tset_desc, unit='K',
                         brief='The target temperature (Default:T2).')
        Tcontrol_brief = 'The temperature used by the temperature controller.'
        Tcontrol_desc = """\
*Tcontrol* is the temperature used by the temperature controller. It tries to
minimize the difference between *Tset* and *Tcontrol* (**Default**:*T2*).
"""
        Tcontrol = Parameter(name='Tcontrol', brief=Tcontrol_brief,
                             description=Tcontrol_desc, unit='K')
        X_desc = """\
*X* is the in phase magnetic induction signal. A SR830 Lock-In amplifier is
used to measure the magnetic induction signal. The in-phase component
represents the sample signal. With a reference measurement, typically a high
purity Ni sample of known magnetic moment, the magnetic moment of the sample
can be calculated.
"""
        X = Parameter(name='X', brief='In-phase magnetic induction signal.',
                       description=X_desc, unit='V')
        Y_brief = 'Quadrature component of magnetic induction signal.'
        Y = Parameter(name='Y', brief=Y_brief, unit='V')

        H_desc = """\
The VSM is equipped with a bipolar superconducting solenoid magnet. It is
capable of delivering a magnetic field up to 9T.
"""
        H = Parameter(name='H', brief='Applied magnetic field.',
                      description=H_desc, unit='T')
        Time_brief = 'Counts the expired time in seconds.'
        Time_desc = """\
The *Time* variable counts the expired time of the measurement.

### Note
It does not neccessary start at zero.
"""
        Time = Parameter(name='Time', brief=Time_brief, description=Time_desc,
                         unit='s')
        m_ref_brief = "Magnetic moment of the reference sample."
        m_ref_desc = """\
Magnetic moment of the reference sample (**Default**: 0.519emu @ 0.6T).
"""
        m_ref = Parameter(name='m_ref', brief=m_ref_brief,
                          description=m_ref_desc, unit='emu')
        U_ref_desc = """\
*U_ref* is the voltage of the reference sample measured at the correct
z-position.
        """
        U_ref = Parameter(name='U_ref', brief='Reference Voltage.',
                          description=U_ref_desc, unit='V')
        Date = Parameter(name='Date', brief='Date of the measurement')
        vsm_brief = "The VSM is the Oxford Vibrating Sample Magnetometer"
        vsm_desc = """\
The VSM is the Oxford Vibrating Sample Magnetometer. It is capable of
delivering magnetic fields up to 9T in a temperature range of 1.7K-300K.

### Components:

 * VCU
 * ITC503
 * SR830
"""
        vsm = Context(name='VSM', brief=vsm_brief, description=vsm_desc )
        vsm.parameters.extend([X, Y, T1, T2, T3, Tsample, Tset, Tcontrol,
                               inv_Tsample, Time, H, m_ref, U_ref, Date])
        return vsm
