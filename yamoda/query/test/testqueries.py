# -*- coding: utf-8 -*-
'''
yamoda.query.test.querytest.py
Created on 21.08.2012
@author: tobixx0
'''
from __future__ import division, absolute_import, print_function
import daterangeparser 
parse_daterange = daterangeparser.parse
from yamoda.query.querylanguage import *

testquery_datas = {
             "context_name" : "TestContext",
             "find" : "datas",
             "param_filters" : {
                 "T" : Range(0, 400),
                 "omega": GreaterThan(1e6)
                 },
             "limit" : 10
             }

testquery_sets = {
             "find" : "sets",
             "creation_date": TimeInterval(*parse_daterange("13 August 2012 to 11 September 2012")) ,
             "user_name" : "user",
             "limit" : 10
             }
