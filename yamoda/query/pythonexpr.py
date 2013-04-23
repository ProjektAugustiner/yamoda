#  -*- coding: utf-8 -*-
#
# yamoda, (c) 2012, see AUTHORS.  Licensed under the GNU GPL.

'''
Created on 18.04.2013
@author: dpausp (Tobias Stenzel)
Parse a python expression string.
Implemented as a Parcon Parser.
'''
from __future__ import absolute_import
import logging
import ast
from parcon import Parser, match, failure, Expectation, EUnsatisfiable


logg = logging.getLogger(__name__)


def scan_for_delimiter(text, delimiter=";", position=0, end=None):
    """Scan for given delimiter outside of comments
    `text` is valid when comments are closed and a delimiter outside of comments is found.
    :param text: string to scan
    :param delimiter: character to scan for
    :param position: start position in `text`
    :param end: end position in `text`, exclusive
    :returns: delimiter position in string if valid, otherwise None
    """
    endpos = end if end is not None else len(text)
    comment_sym = None
    for c in text[position:endpos]:
        if c == "'":
            if comment_sym is None:
                comment_sym = "'"
            elif comment_sym == "'":
                comment_sym = None

        elif c == '"':
            if comment_sym is None:
                comment_sym = '"'
            elif comment_sym == '"':
                comment_sym = None

        elif c == delimiter:
            if not comment_sym:
                return position
        position += 1


class PythonExprExpectation(Expectation):
    """A PythonExprExpectation is returned by a PythonExpr-Parser when no match was found.
    """
    def __init__(self, got):
        self.got = got

    def format(self):
        return "valid python expression, got '{}'".format(self.got)


class PythonExpr(Parser):
    """Parse a python expression.
    The expression must be delimited by a ";" at the end
    """
    def __init__(self):
        pass

    def parse(self, text, position, end, space):
        """Parse given expression
        :param text: string containing an expression
        see base class Parser
        """
        position = space.consume(text, position, end)

        try:
            expected_end = scan_for_delimiter(text, ";", position, end)
            expr_str = text[position:expected_end]
            result = ast.parse(expr_str)
            expr_ast = result.body[0]
            if not isinstance(expr_ast, ast.Expr):
                raise Exception()
        except Exception:
            return failure([(position, PythonExprExpectation(text[position:end]))])

        return match(expected_end + 1, (expr_str, expr_ast), [(expected_end + 1, EUnsatisfiable())])

