#  -*- coding: utf-8 -*-
#
# yamoda, (c) 2012, see AUTHORS.  Licensed under the GNU GPL.

'''
Created on 19.08.2012
@author: dpausp (Tobias Stenzel)

Intermediate representation of AugQL queries.
'''

from __future__ import division, absolute_import


class SortParameter(object):
    def __init__(self, param_name, sort_direction):
        self.param_name = param_name
        self.sort_direction = sort_direction


class Interval(object):
    def __init__(self, start, end):
        self.start = start
        self.end = end

    def __repr__(self):
        return "Range({}, {})".format(self.start, self.end)


class LessThan(object):
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return "LessThan({})".format(self.value)


class GreaterThan(object):
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return "GreaterThan({})".format(self.value)


class ParamFilter(object):
    def __init__(self, param_name, param_values):
        self.param_name = param_name
        self.param_values = param_values


class TimeInterval(object):
    def __init__(self, start_datetime, end_datetime):
        self.start = start_datetime
        self.end = end_datetime

    def __repr__(self):
        return "TimeInterval({}, {})".format(self.start, self.end)
