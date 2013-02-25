#  -*- coding: utf-8 -*-
#
# yamoda, (c) 2012, see AUTHORS.  Licensed under the GNU GPL.
'''
Created on 05.11.2012
@author: dpausp (Tobias Stenzel)

adapted from tgext.coffeescript for flask
https://bitbucket.org/clsdaniel/tgext.coffeescript/
'''
import logging
import subprocess
import os
from jinja2 import nodes
from jinja2.ext import Extension

logg = logging.getLogger("yamoda.coffeeforjinja")


class CoffeeExtension(Extension):
    tags = set(['coffee'])

    def __init__(self, environment):
        logg.debug("Coffee4Jinja extension loaded")
        super(CoffeeExtension, self).__init__(environment)

    def compile_coffee(self, name, caller):
        body = caller()
        # We are assuming Jinja only calls this function when the template
        # is loaded or reloaded (cached), thus no caching on our part.
        coffee = subprocess.Popen(['coffee', "-c", "-b", "-s"], stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = coffee.communicate(input=body + "\n")
        # TODO: Handle returned error code from compiler properly...
        if err:
            body_with_numbers = "\n".join("{}: {}".format(number, line) for number, line in enumerate(body.split("\n")))
            raise Exception("compilation of coffee code failed in block name '{}', error was:\n {}\n code {}".format(name, err, body_with_numbers))
        logg.debug("coffee compile succeeded for %s", name)
        return out

    def parse(self, parser):
        lineno = parser.stream.next().lineno
        args = [parser.parse_expression()]
        body = parser.parse_statements(['name:endcoffee'], drop_needle=True)
        return nodes.CallBlock(self.call_method('compile_coffee', args), [], [], body).set_lineno(lineno)
