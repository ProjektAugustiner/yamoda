# -*- coding: utf-8 -*-
'''
yamoda.query.test.querytest.py
Created on 21.08.2012
@author: tobixx0
'''
from __future__ import division, absolute_import, print_function
from collections import namedtuple
import daterangeparser
parse_daterange = daterangeparser.parse
from yamoda.query.representation import Interval, GreaterThan, SortParameter, TimeInterval, \
    LessThan

QueryPair = namedtuple("QueryPair", ["dict", "string"])

testquery_datas = QueryPair({
             "find": "datas",
             "param_filters": {
                 "omega": [LessThan(0.0), GreaterThan(1e6)]
                 },
             "sort": [SortParameter("omega", "asc"), SortParameter("P", "desc")]
             },
"""
find: datas
omega: < 0 or > 1e6
sort: omega P.desc
"""
)

testquery_datas2 = QueryPair({
             "context_name": "TestContext",
             "find": "datas",
             "param_filters": {
                 "T": [Interval(0.0, 400.0), Interval(500.0, 600.0)],
                 "omega": [GreaterThan(1e6)]
                 },
             "sort": [SortParameter("T", "asc"), SortParameter("omega", "desc")],
             "limit": 10
             },
"""
find: datas
context: TestContext
T: 0 to 400 or 500 to 600
omega: > 1e6
sort: T omega.desc
limit: 10
"""
)

testquery_sets = QueryPair({
             "find": "sets",
             "user_name": "some_one",
             },

"""
find: sets
user: some_one
"""
)

testquery_sets2 = QueryPair({
             "find": "sets",
             "created": TimeInterval(*parse_daterange("11 August 2011 to 12 September 2012")),
             "user_name": "admin",
             "limit": 10
             },

"""
find: sets
user: admin
created: 11 August 2011 to 12 September 2012
limit: 10
"""
)

teststr_comma_separated = "context: TestContext,T: 0 to 400,omega: > 100"

teststr_with_newlines = """
context: TestContext
T: 0 to 400
omega: > 100
"""

teststrings_parse_error = {
            "nonsense": "rfrfkjr!!!einself",
            "wrong_param_filter_operator": "context: TestContext, omega: == 100",
            "wrong_param_filter_nonumber": "context: TestContext, omega: > Haus",
            "missing_colon": "context TestContext, omega: > 10",
            }
