#  -*- coding: utf-8 -*-
#
# yamoda, (c) 2012, see AUTHORS.  Licensed under the GNU GPL.

'''
Created on 19.08.2012
@author: dpausp (Tobias Stenzel)

Intermediate representation of AugQL queries.
'''
from __future__ import division, absolute_import
from meta.asttools import cmp_ast, dump_python_source


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

    def __eq__(self, other):
        return self.param_name == other.param_name and self.sort_direction == other.sort_direction


@add_tup_method
class Interval(object):
    def __init__(self, start, end):
        self.start = start
        self.end = end

    def __repr__(self):
        return "Interval({}, {})".format(self.start, self.end)

    def __eq__(self, other):
        return self.start == other.start and self.end == other.end


@add_tup_method
class ParamFilter(object):
    def __init__(self, param_name, param_exprs):
        self.param_name = param_name
        self.param_exprs = param_exprs

    def __repr__(self):
        return "ParamFilter({}, {})".format(self.param_name, self.param_exprs)

    def __eq__(self, other):
        return self.param_name == other.param_name and self.param_exprs == other.param_exprs


@add_tup_method
class TimeInterval(object):
    def __init__(self, start_datetime, end_datetime):
        self.start = start_datetime
        self.end = end_datetime

    def __repr__(self):
        return "TimeInterval({}, {})".format(self.start, self.end)

    def __eq__(self, other):
        return self.start == other.start and self.end == other.end


@add_tup_method
class CalculatedParam(object):
    def __init__(self, name, expr_str, expr_ast):
        self.name = name
        self.expr_str = expr_str
        self.expr_ast = expr_ast

    def __eq__(self, other):
        """Equal when name and expr_ast the same.
        """
        return (self.name == other.name
                and cmp_ast(self.expr_ast, other.expr_ast))

    def __repr__(self):
        return "CalculatedParam: {} = {}".format(self.name, self.expr_str)


class SimpleValue(object):
    def __init__(self, value):
        self.value = value

    def __eq__(self, other):
        return self.value == other.value

    def __repr__(self):
        return "{}({})".format(self.__class__.__name__, self.value)


class LessThan(SimpleValue):
    pass


class GreaterThan(SimpleValue):
    pass


class ContextRepr(SimpleValue):
    pass


class Limit(SimpleValue):
    pass


class Find(SimpleValue):
    pass


class UserRepr(SimpleValue):
    pass
