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
from _ast import BinOp, Add, Sub, Mult, Div, Expression, Name, Num, Load
import logging
import types
from meta.asttools import get_symbols


logg = logging.getLogger(__name__)


class WhiteListVisitor(ast.NodeVisitor):
    """Check given ast against whitelist
    """
    node_whitelist = {BinOp, Add, Sub, Mult, Div, Expression, Name, Num, Load}

    def visit(self, node):
        logg.debug("visiting %s", node)
        if node.__class__ not in self.node_whitelist:
            raise Exception("disallowed node type found: node {} with type {}".format(node, node.__class__))
        return self.generic_visit(node)


VIS = WhiteListVisitor()


def make_function_from_ast(expr_ast):
    """Create callable from a python expression AST.
    Check given AST against whitelist and compile it if it's valid.
    Compiled Expression is returned wrapped in a lambda function with arguments for all free variables in expr_ast.
    :param expr_ast: python AST for an expression (instance of ast.Expression)
    :return: (function, argument names)
    """
    VIS.visit(expr_ast)
    symbols = get_symbols(expr_ast)
    args = [Name(s, ast.Param()) for s in symbols]
    arguments = ast.arguments(args=args, defaults=[], kwarg=None, vararg=None)
    lamb = ast.Lambda(args=arguments, body=expr_ast.body)
    expr = ast.Expression(lamb)
    ast.fix_missing_locations(expr)
    cc = compile(expr, "<expr_ast>", "eval")
    return eval(cc), symbols
