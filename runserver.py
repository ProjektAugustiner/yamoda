#!/usr/bin/env python
"""Script to start the yamoda development server.

The runserver.py script starts the yamoda server. It accepts several command
line arguments. For a complete list pass the "--help" option. Ctrl-C stops the
server.

"""

from optparse import OptionParser

from yamoda.server import app


parser = OptionParser()
parser.add_option('--debug', dest='debug', default=True,
                  help='enable Flask debug mode')
(options, args) = parser.parse_args()

#start server
app.run(debug=options.debug)
