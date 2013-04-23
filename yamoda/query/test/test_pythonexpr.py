#  -*- coding: utf-8 -*-
#
# yamoda, (c) 2012, see AUTHORS.  Licensed under the GNU GPL.
'''
Created on 21.04.2013
@author: dpausp (Tobias Stenzel)
'''
from __future__ import division, absolute_import
import ast

from yamoda.query.pythonexpr import scan_for_delimiter, PythonExpr


def test_scan_for_delimiter_without_comment():
    assert scan_for_delimiter("") == None
    assert scan_for_delimiter(";") == 0
    assert scan_for_delimiter("abcde;") == 5
    assert scan_for_delimiter("abcde;fgh") == 5
    assert scan_for_delimiter("abcde;;") == 5


def test_scan_for_delimiter_with_comment():
    assert scan_for_delimiter("''") == None
    assert scan_for_delimiter("';'") == None
    assert scan_for_delimiter('abc"de;') == None
    assert scan_for_delimiter('"abc"de;') == 7
    assert scan_for_delimiter("'abc'de;") == 7
    assert scan_for_delimiter("'abc'\"de\";") == 9


def test_scan_for_delimiter_other():
    assert scan_for_delimiter("abcde.", delimiter=".") == 5


def test_scan_for_delimiter_position():
    assert scan_for_delimiter("abcde;", position=1, end=3) == None
    assert scan_for_delimiter("abcde;", position=1, end=6) == 5


def test_parse_pythonexpr():
    parser = PythonExpr()
    # TODO maybe test ast correctness in some way...
    # or should we trust the python parser (implementation detail ;)?
    res = parser.parse_string("1+5;")
    assert res[0] == "1+5"
    assert isinstance(res[1], ast.Expr)
    res = parser.parse_string("exp(1+5*a);")
    assert res[0] == "exp(1+5*a)"
    assert isinstance(res[1], ast.Expr)
    res = parser.parse_string("len('aa;');")
    assert res[0] == "len('aa;')"
    assert isinstance(res[1], ast.Expr)

