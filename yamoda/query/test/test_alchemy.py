#  -*- coding: utf-8 -*-
#
# yamoda, (c) 2012, see AUTHORS.  Licensed under the GNU GPL.
'''
Created on 06.09.2012
@author: dpausp (Tobias Stenzel)
'''
from __future__ import division, absolute_import
import logging
from pprint import pformat
import yamoda.query.test.db_setup
from yamoda.query.parsing import parse_query_string
from yamoda.query.alchemy import convert_dict_query_to_sqla
from nose.tools import with_setup
from yamoda.query.test import db_setup

logg = logging.getLogger(__name__)


setup = db_setup.create_complete_env
teardown = db_setup.drop_schema


# def setup_module(module):
#     db_setup.create_complete_env()
#
#
# def teardown_module(module):
#     db_setup.drop_schema()


def assert_correct_query_result(query_string, expected):
        logg.info("testing query string %s", query_string)
        _, query = convert_dict_query_to_sqla(parse_query_string(query_string))
        result = query.all()
        logg.info("result %s", result)
        logg.info("expected %s", expected)
        assert set(result) == set(expected), ("result for '{}' is {}, expected {}".format(query_string, result, expected))


def test_datas_query_to_alchemy():
    logg.info("test_datas_query_to_alchemy")
    for query_string, expected in db_setup.data_testcases.iteritems():
        yield assert_correct_query_result, query_string, expected


def test_sets_query_to_alchemy():
    logg.info("test_sets_query_to_alchemy")
    for query_string, expected in db_setup.set_testcases.iteritems():
        yield assert_correct_query_result, query_string, expected
