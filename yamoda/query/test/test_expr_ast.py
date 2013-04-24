#  -*- coding: utf-8 -*-
#
# yamoda, (c) 2012, see AUTHORS.  Licensed under the GNU GPL.
'''
Created on 23.04.2013
@author: dpausp (Tobias Stenzel)
'''
from __future__ import division, absolute_import
import math
from nose.tools import raises
from yamoda.query.expr_ast import ExprVisitorWithMath, make_function_from_ast, DisallowedException
from yamoda.query.test.helpers import parse_expr
from collections import namedtuple


ValidExpression = namedtuple("Expression", "expr_str args expected called_funcs")
InvalidExpression = namedtuple("Expression", "expr_str")

es = set()

valid_expressions = [
     ValidExpression("a", dict(a=5), 5, es),
     ValidExpression("5", {}, 5, es),
     ValidExpression("2 + 4", {}, 6, es),
     ValidExpression("2**4", {}, 16, es),
     ValidExpression("a + b * (c * 6)", dict(a=1, b=2, c=3), 37, es),
     ValidExpression("a if a else b", dict(a=None, b=2), 2, es),
     ValidExpression("a or b", dict(a=None, b=2), 2, es),
     ValidExpression("exp(a)", dict(a=1), math.e, {math.exp}),
     ValidExpression("log(exp(a)*(b*c))", dict(a=1, b=math.e, c=math.e), 3, {math.exp, math.log}),
     ]

invalid_expressions_disallowed = [
    InvalidExpression("lambda b: 3 + b"),
    InvalidExpression("BLA.test()"),  # all "dot" calls not allowed
    InvalidExpression("os.system('echo')"),
    ]

invalid_expressions_syntax_error = [
    InvalidExpression("WTF?!?"),
    InvalidExpression("99***99"),
    InvalidExpression("exp("),
    InvalidExpression("import os; os.system('echo')"),  # only expressions
    InvalidExpression("."),
    ]


def visit_ast(expr):
    vis = ExprVisitorWithMath()
    expr_ast = parse_expr(expr.expr_str)
    vis.visit(expr_ast)
    assert set(vis.found_calls.values()) == set(expr.called_funcs), "called_funcs was {}, expected {}".format(vis.found_calls, expr.called_funcs)


def assert_created_function_is_valid(expr):
    expr_ast = parse_expr(expr.expr_str)
    lamb, args = make_function_from_ast(expr_ast)
    # function should also take excess arguments
    result = lamb(excess=5, **expr.args)
    assert set(args) == set(expr.args.keys()), "result args were {}, expected {}".format(args, expr.args.keys())
    assert result == expr.expected, "result was {}, expected {}".format(result, expr.expected)


visit_invalid_ast_disallowed = raises(DisallowedException)(visit_ast)
visit_invalid_ast_sytax_error = raises(SyntaxError)(visit_ast)


def test_whitelist_visitor_valid():
    for valid_expr in valid_expressions:
        yield visit_ast, valid_expr


def test_whitelist_visitor_invalid_disallowed():
    for invalid_expr in invalid_expressions_disallowed:
        yield visit_invalid_ast_disallowed, invalid_expr


def test_whitelist_visitor_invalid_syntax_error():
    for invalid_expr in invalid_expressions_syntax_error:
        yield visit_invalid_ast_sytax_error, invalid_expr


def test_make_function_from_ast():
    for valid_expr in valid_expressions:
        yield assert_created_function_is_valid, valid_expr
