#  -*- coding: utf-8 -*-
#
# yamoda, (c) 2012, see AUTHORS.  Licensed under the GNU GPL.
'''
Created on 06.09.2012
@author: dpausp (Tobias Stenzel)
'''
from __future__ import division, absolute_import
import ast
# import logging
from yamoda.query.parsing import parse_query_string, replace_newline_with_comma
from pprint import pformat

# logg = logging.getLogger(__name__)


def compare_dict_items(left, right):
    if sorted(left.keys()) != sorted(right.keys()):
        return "keys are not the same!"

    failures = []
    for key, value in left.iteritems():
        if value != right[key]:
            failures.append("difference for key {}:\nleft {}(: {}),\n\nright {}(: {})".format(key, value, type(value),
                                                                                          right[key], type(right[key])))
    return "\n".join(failures)


def parse_expr(expr_str):
    return ast.parse(expr_str, "<expr>", "eval")

