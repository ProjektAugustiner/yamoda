# -*- coding: utf-8 -*-
'''
yamoda.query.test.querytest.py
Created on 21.08.2012
@author: tobixx0
'''
from __future__ import division, absolute_import, print_function
import daterangeparser
parse_daterange = daterangeparser.parse
from yamoda.query.representation import *

testquery_datas = {
             "context_name": "TestContext",
             "find": "datas",
             "param_filters": {
                 "T": Interval(200, 400),
                 "omega": GreaterThan(1e6)
                 },
             "sort": [SortParameter("T", "asc")],
             "limit": 50
             }

testquery_sets = {
             "find": "sets",
             "creation_date": TimeInterval(*parse_daterange("11 August 2012 to 11 September 2012")),
             "user_name": "user",
             "limit": 10
             }

teststr_sets = """
find: sets
user: tstenzel
created: 11 August 2012 to 15 August 2012
"""

teststr_datas = """
find: datas
context: TestContext
T: 0 to 400 or 500 to 600
omega: > 1e6
sort: T omega.desc
limit: 10
"""

teststr_comma_separated = """
context.name: TestContext, T: 0 to 400, omega: > 100
"""
