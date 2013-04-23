#  -*- coding: utf-8 -*-
#
# yamoda, (c) 2012, see AUTHORS.  Licensed under the GNU GPL.
'''
Created on 06.09.2012
@author: dpausp (Tobias Stenzel)
'''
from __future__ import division, absolute_import
import logging
logging.basicConfig(level=logging.INFO)
from pprint import pformat
from parcon import ParseException
from nose.tools import raises
from yamoda.query.parsing import parse_query_string, replace_newline_with_comma
import yamoda.query.test.testqueries as tq
from yamoda.query.test.helpers import compare_dict_items

logg = logging.getLogger(__name__)


def assert_correct_parse_result(query_pair):
    parse_res = parse_query_string(replace_newline_with_comma(query_pair.string))
    expected = query_pair.dict
    assert parse_res == expected, ("parse result was\n{}, expected:\n\n{}. Diff is:\n{}".
                                                format(pformat(parse_res),
                                                       pformat(expected),
                                                       compare_dict_items(parse_res, expected)))


def test_replace_newline_with_comma():
    res = replace_newline_with_comma(tq.teststr_with_newlines)
    assert res == tq.teststr_comma_separated, "got {}, expected {}".format(res, tq.teststr_comma_separated)


testqueries_datas = [tq.testquery_datas, tq.testquery_datas2]
testqueries_sets = [tq.testquery_sets, tq.testquery_sets2]


def test_parse_query_datas():
    for query in testqueries_datas:
        yield assert_correct_parse_result, query


def test_parse_query_sets():
    for query in testqueries_sets:
        yield assert_correct_parse_result, query


@raises(ParseException)
def except_parse_exception(name, query_string):
    logg.info("testing incorrect query '%s'", name)
    try:
        parse_query_string(query_string)
    except ParseException as p:
        logg.error("ok, exception was %s", p)
        raise


def test_parse_failures():
    for name, query_string in tq.teststrings_parse_error.iteritems():
        yield except_parse_exception, name, query_string
