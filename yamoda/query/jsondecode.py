#  -*- coding: utf-8 -*-
#
# yamoda, (c) 2012, see AUTHORS.  Licensed under the GNU GPL.
"""
Deserialize query dicts from JSON

Created on 21.09.2012
@author: dpausp (Tobias Stenzel)
"""
from __future__ import division, absolute_import
import logging as logg
import json
import datetime

from yamoda.query.representation import Interval, GreaterThan, SortParameter, TimeInterval, \
    LessThan


def decode_sort(sort_list):
#        logg.info("decode sort %s", sort_list)
    sort_params = [SortParameter(s[0], s[1]) for s in sort_list]
    logg.info("decoded: %s", sort_params)
    return sort_params


def decode_param_cond(f):
    first = f[0]
    value = f[1]
    if first == ">":
        return GreaterThan(int(value))
    elif first == "<":
        return LessThan(int(value))
    else:
        return Interval(first, value)


def decode_param_filters(filters_in):
#        logg.info("decode param filters %s", filters_in)
    filters_out = {}
    for param_name, param_conds in filters_in.iteritems():
        conds = [decode_param_cond(p) for p in param_conds]
        filters_out[param_name] = conds

    logg.info("decoded: %s", filters_out)
    return filters_out


def decode_time(isoformat_time):
    return datetime.datetime.strptime(isoformat_time, '%Y-%m-%dT%H:%M:%S')


def obj_pairs_hook(pairs):
    result = {}
    for key, value in pairs:
#            logg.info("key %s value %s", key, value)
        if key == "param_filters":
            result["param_filters"] = decode_param_filters(value)
        elif key == "sort":
            result["sort"] = decode_sort(value)
        elif key == "created":
            result["created"] = TimeInterval(*[decode_time(v) for v in value])
        else:
            result[key] = value
    return result
