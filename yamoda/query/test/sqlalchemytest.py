# -*- coding: utf-8 -*-
'''
yamoda.query.test.sqlalchemytest.py
Created on 21.08.2012
@author: tobixx0
'''
from __future__ import division, absolute_import, print_function
from yamoda.query.alchemy import convert_dict_query
from testqueries import testquery_datas, testquery_sets
import logging as logg
logg.basicConfig(level=logg.DEBUG)

print("testquery for datas")
print("-" * 100)
res_datas = convert_dict_query(testquery_datas)
print(res_datas)
print("\n")

print("testquery for sets")
print("-" * 100)
res_sets = convert_dict_query(testquery_sets)
print(res_sets)