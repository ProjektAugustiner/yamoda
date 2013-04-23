#  -*- coding: utf-8 -*-
#
# yamoda, (c) 2012, see AUTHORS.  Licensed under the GNU GPL.

'''
Created on 22.08.2012
@author: dpausp (Tobias Stenzel)

The AugQL query language written as parcon parsers.
'''
from __future__ import absolute_import
import string
from parcon import *
from .representation import GreaterThan, LessThan, SortParameter, Interval, \
    ContextRepr, Find, ParamFilter, UserRepr, TimeInterval, Limit, CalculatedParam
import daterangeparser
from .pythonexpr import PythonExpr

# just to save some keystrokes ;-)
L = Literal
SL = SignificantLiteral

##### actions


def _make_comparison(args):
    op, number = args
    if op == "<":
        return LessThan(number)
    else:
        return GreaterThan(number)


def _join(seq):
    return " ".join(seq)


def _concat_list(args):
    return list([args[0]] + args[1])


def _make_calculated_param(args):
    param_name = args[0]
    _, expr_ast = args[1:]
    return CalculatedParam(param_name, expr_ast)

##### parsers (rules)

# ## names
identifier = Word(string.letters + string.digits + "_")
context_name = OneOrMore(identifier)[_join]
data_name = identifier(description="data_name")
param_name = identifier(description="param_name")
user_name = identifier(description="user name")

# ## number literals

#  a floating point number like in Python
float_lit = Expected(Regex(r"[-+]?(\d+(\.\d*)?|\.\d+)([eE][-+]?\d+)?")[float](name="float lit regex"), "'floating point number'")

# ## misc

int_lit = Word(string.digits)[int]

interval = (float_lit + "to" + float_lit)[Interval.tup]

dot = L(".")(name="dot")

sort_dir = ((dot + SL("asc")(name="asc")) | (dot + SL("desc")(name="desc")) | SL("")(name="empty"))(name="sort_dir")

sort_param = (param_name + sort_dir)[SortParameter.tup](name="sort_param")

comparison = ((SL("<")(name="<") | SL(">")(name=">")) + float_lit)[_make_comparison](name="comparison")

param_cond = interval | comparison

filter_expr = (param_cond + ZeroOrMore(L("or") + param_cond))[_concat_list]

# ## clauses

sort_spec = L("sort") + ":" + OneOrMore(sort_param)

limit_spec = (L("limit") + ":" + int_lit)[Limit]

context_spec = ((L("context.name") | "context") + ":" + context_name)[ContextRepr]

find_spec = (L("find") + ":" + (SL("sets") | SL("datas")))[Find]

# tag filter spec with parameter name so we can insert it correctly in the query dict later
filter_spec = (param_name + ":" + filter_expr)[ParamFilter.tup]

user_spec = (L("user") + ":" + user_name)[UserRepr]

# Date range like: '12 August 2012 to 12 December 2012'
# XXX: we could allow more date range formats because daterangeparser understands many other formats
date_interval = Expected(Regex(r"\d{1,2} \w+ \d{2,4} to \d\d \w+ \d{2,4}"), "'date string (like 11 August 2011 to 12 September 2012)'")

creation_time_spec = (L("created") + ":" + date_interval)[lambda t: TimeInterval(*daterangeparser.parse(t))]

visible_params_spec = (L("visible")) + ":" + OneOrMore(param_name)

# python expression
calculated_param_spec = L("calculate") + ":" + (param_name + "=" + PythonExpr())[_make_calculated_param]

query_clause = (context_spec["context_name"]
                | user_spec["user_name"]
                | find_spec["find"]
                | limit_spec["limit"]
                | filter_spec["param_filter"]
                | sort_spec["sort"]
                | creation_time_spec["created"]
                | visible_params_spec["visible_params"]
                | calculated_param_spec["calculated_param"])

# complete AugQL query string
query = (query_clause + ZeroOrMore(L(",") + query_clause))[_concat_list]
