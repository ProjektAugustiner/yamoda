#  -*- coding: utf-8 -*-
#
# yamoda, (c) 2012, see AUTHORS.  Licensed under the GNU GPL.

'''
Created on 19.08.2012
@author: dpausp (Tobias Stenzel)

Intermediate representation of AugQL queries.
'''

from __future__ import division, absolute_import
import types


def add_tup_method(cls):
    def tup(args):
        return cls(*args)
    cls.tup = staticmethod(tup)
    return cls


@add_tup_method
class SortParameter(object):
    def __init__(self, param_name, sort_direction):
        self.param_name = param_name
        self.sort_direction = sort_direction if sort_direction else "asc"

    def __repr__(self):
        return "SortParameter({}, {})".format(self.param_name, self.sort_direction)


@add_tup_method
class Interval(object):
    def __init__(self, start, end):
        self.start = start
        self.end = end

    def __repr__(self):
        return "Interval({}, {})".format(self.start, self.end)


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


class Context(object):
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return "Context({})".format(self.value)


class Limit(object):
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return "Limit({})".format(self.value)


class Find(object):
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return "Find({})".format(self.value)


class User(object):
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return "User({})".format(self.value)


@add_tup_method
class ParamFilter(object):
    def __init__(self, param_name, param_exprs):
        self.param_name = param_name
        self.param_exprs = param_exprs

    def __repr__(self):
        return "ParamFilter({}, {})".format(self.param_name, self.param_exprs)


@add_tup_method
class TimeInterval(object):
    def __init__(self, start_datetime, end_datetime):
        self.start = start_datetime
        self.end = end_datetime

    def __repr__(self):
        return "TimeInterval({}, {})".format(self.start, self.end)
