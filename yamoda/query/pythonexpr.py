#  -*- coding: utf-8 -*-
#
# yamoda, (c) 2012, see AUTHORS.  Licensed under the GNU GPL.

'''
Created on 22.08.2012
@author: dpausp (Tobias Stenzel)

AugQL parsing, see parse_query_string.
'''
from __future__ import absolute_import
import logging
import ast
from parcon import Parser, match, failure, Expectation, EUnsatisfiable


logg = logging.getLogger(__name__)


class PythonExprExpectation(Expectation):
    def __init__(self, got):
        self.got = got

    def format(self):
        return "valid python expression, got '{}'".format(self.got)


class PythonExpr(Parser):
    def __init__(self):
        pass

    def parse(self, text, position, end, space):
        position = space.consume(text, position, end)
        try:
            expr_str = text[position:end]
            result = ast.parse(expr_str)
            expr_ast = result.body[0]
            if not isinstance(expr_ast, ast.Expr):
                raise Exception()
        except Exception:
            return failure([(position, PythonExprExpectation(expr_str))])

        return match(end, (expr_str, expr_ast), [(end, EUnsatisfiable())])

