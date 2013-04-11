#  -*- coding: utf-8 -*-
#
# yamoda, (c) 2012, see AUTHORS.  Licensed under the GNU GPL.

'''
yamoda.server.jinja_filters.py
Custom filters for jinja2 templates used for yamoda.
'''
from __future__ import division, absolute_import

import logging
import json
import os
import numpy as np
from jinja2 import Markup
import markdown2


logg = logging.getLogger(__name__)

# imported functions

from __builtin__ import min, max
std = np.std
average = np.average


def dtformat(value, formatstr='%Y-%m-%d %H:%M'):
    return value.strftime(formatstr)


def dataformat(value, maxlen=None):
    """Format data for HTML display
    The returned value is compatible with JQuery.sparkline
    """
    if value is None:
        return ''
    elif isinstance(value, float):
        fmt = '%.5g' % value
        if 'e' in fmt:
            fmt = Markup(fmt.replace('e', ' &times; 10<sup>') + '</sup>')
        return fmt
    elif isinstance(value, np.ndarray):
        # return arrays as 1, 2, 3, 4 ... for use with jquery.sparkline
        if maxlen is not None:
            # if array is too long: shorten array by sampling it
            step = max(len(value) // maxlen, 1)
            value = value[::step]
            if step > 1:
                # if we omit values we must send matching xvalues so that sparkline knows what to do
                return ", ".join(["{}:{:.8f}".format(i * step, v) for i, v in enumerate(value)])
        # just send yvalues
        logg.debug("type %s, values: %s", type(value), value)
        return ", ".join("{:.8f}".format(v) for v in value.ravel())
    return str(value)


def count_formatted(value, maxlen=None):
    """Return count of values as returned by dataformat with same maxlen argument"""
    if maxlen is None:
        return valuecount(value)
    else:
        # if array is too long: shorten array by sampling it
        step = max(len(value) // maxlen, 1)
        return valuecount(value[::step])


def normal_min(value):
    return average(value) - std(value)


def normal_max(value):
    return average(value) + std(value)


def jsonformat(value):
    return json.dumps(value)


def unitformat(value):
    if value is None:
        return ''
    return value


def yesnoformat(truth_value):
    if truth_value:
        return "yes"
    else:
        return "no"


def valuecount(value):
    if isinstance(value, np.ndarray):
        return len(value.ravel())
    else:
        return len(value)


md = markdown2.Markdown(safe_mode='escape')


def markdown(value):
    return Markup(md.convert(value))


def shape(value):
    """Shape.
    :param value: float, int or ndarray are recognized
    :returns: string "scalar" or numpy shape, like '100, 100'
    """
    if isinstance(value, float) or isinstance(value, int):
        return "scalar"
    if isinstance(value, np.ndarray):
        shapestr = str(value.shape).strip("(),")
        return shapestr
    else:
        return "unknown"


def dimension(value):
    if isinstance(value, float) or isinstance(value, int):
        return 0
    if isinstance(value, np.ndarray):
        return len(value.shape)
    else:
        return "unknown"
