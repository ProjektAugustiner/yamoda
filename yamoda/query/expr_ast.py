#  -*- coding: utf-8 -*-
#
# yamoda, (c) 2012, see AUTHORS.  Licensed under the GNU GPL.
'''
Created on 23.04.2013
@author: dpausp (Tobias Stenzel)
Process Python expression ASTs.
'''
from __future__ import division, absolute_import
import ast
from _ast import BinOp, Add, Sub, Mult, Div, Pow, Expression, Str, Name, Num, Load, IfExp, BoolOp, Or, And, Not, Call,\
        Compare, Lt, Gt, GtE, LtE, Eq
import logging
import types
from meta.asttools import get_symbols


logg = logging.getLogger(__name__)


def add_allowed_calls_from_modules(cls):
    for module in cls.allowed_modules:
        for key in dir(module):
            if not key.startswith("_"):
                val = getattr(module, key)
                if callable(val):
                    cls.allowed_calls[key] = val
    return cls


class DisallowedException(Exception):
    pass


class WhiteListExprVisitor(ast.NodeVisitor):
    """Check given ast against whitelist
    """
    # always allowed
    node_whitelist = set()
    allowed_modules = set()
    allowed_calls = {}

    def visit_Call(self, node):
        # capture all "dot" calls
        if isinstance(node.func, ast.Attribute):
            raise DisallowedException("dot (.) not allowed at node {}".format(node))
        # capture other disallowed calls
        if not node.func.id in self.allowed_calls:
            raise DisallowedException("call to {} not allowed at node {}".format(node.func.id, node))
        # call is ok
        return super(WhiteListExprVisitor, self).generic_visit(node)

    def generic_visit(self, node):
        logg.debug("visiting %s", node)
        if node.__class__ not in self.node_whitelist:
            raise DisallowedException("disallowed node type found: node {} with type {}".format(node, node.__class__))
        return super(WhiteListExprVisitor, self).generic_visit(node)


@add_allowed_calls_from_modules
class ExprVisitorWithMath(WhiteListExprVisitor):
    import math
    """Extended visitor which allows math calls and records all calls in self.found_calls.
    """
    node_whitelist = {BinOp, Add, Sub, Mult, Div, Pow, Expression, Str, Name, Num, Load, IfExp, BoolOp, Or, And, Not, Call, Compare, Lt, Gt, GtE, LtE, Eq}
    allowed_modules = {math}

    def __init__(self):
        self.found_calls = {}

    def visit_Call(self, node):
        res = super(ExprVisitorWithMath, self).visit_Call(node)
        self.found_calls[node.func.id] = self.allowed_calls[node.func.id]
        return res


def make_function_from_ast(expr_ast):
    """Create callable from a python expression AST.
    Check given AST against whitelist and compile it if it's valid.
    Compiled Expression is returned wrapped in a lambda function with arguments for all free variables in expr_ast.
    :param expr_ast: python AST for an expression (instance of ast.Expression)
    :return: (function, argument names)
    """
    vis = ExprVisitorWithMath()
    vis.visit(expr_ast)
    symbols = {s for s in get_symbols(expr_ast) if s not in vis.found_calls}
    args = [Name(s, ast.Param()) for s in symbols]
    arguments = ast.arguments(args=args, defaults=[], kwarg="kwargs", vararg=None)
    lamb = ast.Lambda(args=arguments, body=expr_ast.body)
    expr = ast.Expression(lamb)
    ast.fix_missing_locations(expr)
    cc = compile(expr, "<expr_ast>", "eval")
    return eval(cc, vis.found_calls), symbols
