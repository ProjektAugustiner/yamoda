#  -*- coding: utf-8 -*-
#
# yamoda, (c) 2012, see AUTHORS.  Licensed under the GNU GPL.

'''
Created on 22.08.2012
@author: dpausp (Tobias Stenzel)

AugQL parsing, see parse_query_string.
'''
from __future__ import absolute_import, print_function
import ast
import logging as logg
from .language import query


def replace_newline_with_comma(query_str):
    """Replaces each newline (\n oder \r\n) with a comma
    and strips extraneous commas and blank lines."""
    splitted = query_str.replace("\r", "").split("\n")
    lines = [line.strip(",") for line in splitted if line]
    return ",".join(lines)


def parse_query_string(query_string):
    """ Parse AugQL query string to intermediate representation.
    :param query_string: AugQL string, clauses separated by comma or newline.
    :returns: intermediate representation (query dict)
    """
    query_dict = {}
    logg.debug("parsing: '%s'", query_string)
    parsed = query.parse_string(query_string)
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
            param_filters = query_dict.setdefault("param_filters", {})
            param_name = content.param_name
            if param_name in param_filters:
                raise Exception("duplicate param filter clause for '{}'!".format(param_name))
            param_filters[param_name] = content.param_exprs
        elif tag in ("visible_params"):
            view_options = query_dict.setdefault("view_options", {})
            visible_params = view_options.setdefault("visible_params", [])
            visible_params += content
        elif tag in ("calculated_params"):
            view_options = query_dict.setdefault("view_options", {})
            calculated_params = view_options.setdefault("calculated_params", [])
            calculated_params.append(content)
        else:
            raise Exception("internal parser error: something went wrong parsing the query!")

    return query_dict
