#  -*- coding: utf-8 -*-
#
# yamoda, (c) 2012, see AUTHORS.  Licensed under the GNU GPL.

'''
Created on 22.08.2012
@author: dpausp (Tobias Stenzel)

AugQL parsing, see parse_query_string.
'''
from __future__ import absolute_import, print_function
import logging as logg
from .language import query


def _replace_newline_with_comma(query_str):
    """Replaces each newline with a comma and strips extraneous commas and blank lines"""
    lines = [line.strip(",") for line in query_str.split("\n") if line]
    return ",".join(lines)


def parse_query_string(query_string):
    """ Parse AugQL query string to intermediate representation.
    :param query_string: AugQL string, clauses separated by comma or newline.
    """
    query_dict = dict(param_filters={})
    query_str = _replace_newline_with_comma(query_string)
    logg.debug("parsing: '%s'", query_str)
    parsed = query.parse_string(query_str)
    logg.debug("parsing result: %s", parsed)

    def check_duplicate(tag):
        """duplicate clauses not allowed"""
        if tag in query_dict:
            raise Exception("duplicate clause for '{}'!".format(tag))

    # walk result and populate query_dict
    for tag, content in parsed:
        logg.debug("adding tag %s, content %s", tag, content)
        # XXX: this is a bit stupid, change that...
        if tag in ("context_name", "find", "limit", "user_name"):
            check_duplicate(tag)
            query_dict[tag] = content.value
        elif tag in ("created", "sort"):
            check_duplicate(tag)
            query_dict[tag] = content
        elif tag == "param_filter":
            param_name = content.param_name
            if param_name in query_dict["param_filters"]:
                raise Exception("duplicate param filter clause for '{}'!".format(param_name))
            query_dict["param_filters"][param_name] = content.param_exprs

    return query_dict
