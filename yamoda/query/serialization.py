#  -*- coding: utf-8 -*-
#
# yamoda, (c) 2012, see AUTHORS.  Licensed under the GNU GPL.
"""(De)Serialize query dicts to and from JSON

Created on 21.09.2012
@author: dpausp (Tobias Stenzel)
"""
from __future__ import division, absolute_import
import cStringIO
import logging as logg
import json
import meta.asttools
from yamoda.query import jsondecode
from yamoda.query.representation import Interval, GreaterThan, SortParameter, TimeInterval, \
    LessThan, CalculatedParam


class _JSONAugQLEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Interval):
            return [obj.start, obj.end]
        elif isinstance(obj, GreaterThan):
            return [">", obj.value]
        elif isinstance(obj, LessThan):
            return ["<", obj.value]
        elif isinstance(obj, SortParameter):
            return [obj.param_name, obj.sort_direction]
        elif isinstance(obj, TimeInterval):
            return [obj.start.isoformat(), obj.end.isoformat()]
        elif isinstance(obj, CalculatedParam):
            return [obj.name, obj.expr_str]
        else:
            logg.info("other: %s type %s", object, type(object))
            return json.JSONEncoder.default(self, object)


def to_json(query_dict):
    return json.dumps(query_dict, cls=_JSONAugQLEncoder)


def from_json(json_string):
    return json.loads(json_string, object_pairs_hook=jsondecode.obj_pairs_hook)

