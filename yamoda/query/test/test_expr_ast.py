#  -*- coding: utf-8 -*-
#
# yamoda, (c) 2012, see AUTHORS.  Licensed under the GNU GPL.
'''
Created on 23.04.2013
@author: dpausp (Tobias Stenzel)
'''
from __future__ import division, absolute_import
from nose.tools import raises
from yamoda.query.expr_ast import WhiteListVisitor, make_function_from_ast
from yamoda.query.test.helpers import parse_expr
from collections import namedtuple


TestExpression = namedtuple("Expression", "expr_str args expected")

valid_expressions = [
     TestExpression("a", dict(a=5), 5),
     TestExpression("5", {}, 5),
     TestExpression("2 + 4", {}, 6),
     TestExpression("a + b * (c * 6)", dict(a=1, b=2, c=3), 37)
     ]
# invalid_expressions = ["lambda b: 3 + b", "import os; os.system('echo')", "99**99"]

VIS = WhiteListVisitor()


def visit_ast(expr):
    expr_ast = parse_expr(expr.expr_str)
    VIS.visit(expr_ast)


def assert_created_function_is_valid(expr):
    expr_ast = parse_expr(expr.expr_str)
    lamb = make_function_from_ast(expr_ast)
    result = lamb(**expr.args)
    assert result == expr.expected, "result was {}, expected {}".format(result, expr.expected)


@raises(Exception)
def visit_invalid_ast(expr_str):
    """Same as visit_ast, but for failing generator functions"""
    visit_ast(expr_str)


def test_whitelist_visitor_valid():
    for valid_expr in valid_expressions:
        yield visit_ast, valid_expr

#
# def test_whitelist_visitor_invalid():
#     for invalid_expr in invalid_expressions:
#         yield visit_invalid_ast, invalid_expr


def test_make_function_from_ast():
    for valid_expr in valid_expressions:
        yield assert_created_function_is_valid, valid_expr
