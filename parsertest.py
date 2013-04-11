#  -*- coding: utf-8 -*-
#
# yamoda, (c) 2012, see AUTHORS.  Licensed under the GNU GPL.
'''
Created on 11.04.2013
@author: dpausp (Tobias Stenzel)
'''
from yamoda.query.pythonexpr import PythonExpr

parser = PythonExpr()
result = parser.parse_string("1+6;")
print(result)
