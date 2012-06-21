#  -*- coding: utf-8 -*-
#
# yamoda, (c) 2012, see AUTHORS.  Licensed under the GNU GPL.
"""Importer for VSM datafiles.

Functions:
----------
 vsm_context -- Creates a default VSM context.
"""
from yamoda.server.database import Context
from yamoda.importer.base import ImporterBase, ReadFailed, ImportEntry

import numpy as np
from datetime import datetime
from itertools import izip
from os import path


def vsm_context():
    """Creates a default VSM context."""
    T1_brief = 'Temperature of the capacitance thermometer.'
    T1_desc = """
    The T1 variable represents the temperature of the capacitance thermometer.
    It's advantage is the low magnetic field dependance. It is perfectly 
    suited for magnetic field sweeps. It reacts slowly to large temperature 
    changes, the resistive thermometer T1 and T2 are the better alternative
    for temperature sweeps.
    """
    T1 = Parameter(name='T1', brief=T1_brief,description=T1_desc)
    T2_brief = 'Temperature of the resistive thermometer.'
    T2_desc = """
    The T1 variable represents the temperature of the resistive thermometer.
    It is mounted adjacent to the T1 thermometer. It's strength is the short
    reaction time to temperature changes. It is the first choice for 
    Temperature Sweeps.
    """
    T2 = Parameter(name='T2', brief=T2_brief, description=T2_desc)
    T3_brief = 'Temperature of the resistive sample thermometer'
    T3_desc = """
    The T1 variable represents the temperature of the resistive sample
    thermometer. It is mounted close to the sample holder, between the inner
    pickup coils, to achieve a more acurate sample Temperature.
    """
    T3 = Parameter(name='T3', brief=T3_brief, description=T3_desc)
    X1_desc = """
    X1 is the in phase magnetic induction signal. A SR830 Lock-In amplifier is
    used to measure the magnetic induction signal. The in-phase component
    represents the sample signal. With a reference measurement, typically a
    high purity Ni sample of known magnetic moment, the magnetic moment of the
    sample can be calculated.
    """
    X1 = Parameter(name='X1', brief='In-phase magnetic induction signal.',
                   description=X1_desc)
    Y1_brief = 'Quadrature component of magnetic induction signal'
    Y1 = Parameter(name='Y1', brief=Y1_brief)

    H_desc = """
    The VSM is equipped with a bipolar superconducting solenoid magnet. It is
    capable of delivering a magnetic field up to 9T.
    """
    H = Parameter(name='H', brief='Applied magnetic field.',
                  description=H_desc)
    m_rev_brief = "Magnetic moment of the reference sample."
    m_rev_desc = """
    Magnetic moment of the reference sample (Default: 0.519emu @ 0.6T).
    """
    m_rev = Parameter(name='m_rev', brief=m_ref_brief,
                      description=m_ref_description)
    U_ref_desc = """
    U_ref is the voltage of the reference sample measured at the correct
    z-position.
    """
    U_ref = Parameter(name='U_ref', brief='Reference Voltage.',
                      description=U_ref_desc)
    vsm_brief = "The VSM is the Oxford Vibrating Sample Magnetometer"
    vsm_desc = """
    The VSM is the Oxford Vibrating Sample Magnetometer. It is capable of 
    delivering magnetic fields up to 9T in a temperature range of 1.7K-300K.
    """
    vsm = Context(name='VSM', brief=vsm_brief, description=vsm_desc )
    vsm.parameters.extend([X1, Y1, T1, T2, T3, H, m_rev, U_rev])
    return vsm


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
    def read_file(self, filename):
        """Parses a VSM file."""
        def assert_blank(line):
            """Tiny helper funtion checking if the line is blanck."""
            if line.strip():
                raise ReadFailed('invalid VSM file:{0}, line:{1}:'.format(filename, len(line)))
        name = path.splitext(path.basename(filename))[0]
        entries = {'__name__':ImportEntry(name=filename, value=name),}

        with open(filename, 'rb') as f:
            for line in iter(f.readline, ''):
                if line.startswith(';'):
                    # TODO parse comments
                    continue
                else:
                    t = datetime.strptime(line.strip(), "%a %b %d %H:%M:%S %Y")
                    entries['time'] = ImportEntry(name='time', value=t)
                    break

            assert_blank(f.readline())
            cols = [x.strip() for x in f.readline().split(',')]
            units = [x.strip() for x in f.readline().split(',')]
            assert_blank(f.readline())

            precission = f.readline()
            M = np.loadtxt(f)
            assert(len(cols) == len(units) == M.shape[1])

            for (row, col, unit) in izip(M.T, cols, units):
                entries[col] = ImportEntry(name=col, unit=unit, value=row)

        return entries
    



