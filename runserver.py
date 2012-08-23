#!/usr/bin/env python
"""Script to start the yamoda development server.

The runserver.py script starts the yamoda server. It accepts several command
line arguments. For a complete list pass the "--help" option. Ctrl-C stops the
server.

"""

import logging as logg
logg.basicConfig(level=logg.INFO)
# INFO shows SQL statements, DEBUG even shows raw result sets
#logg.getLogger("sqlalchemy.engine").setLevel(logging.INFO)

from optparse import OptionParser
from yamoda.server import app
from dbsettings import DATABASE_URIS

parser = OptionParser()
parser.add_option('--debug', dest='debug', default=True,
                  help='enable Flask debug mode')
parser.add_option('--database', dest='database', default="sqlite",
                  help='Select Database backend (sqlite | mysql | postgres)')
(options, args) = parser.parse_args()

app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URIS[options.database]

# start server
logg.info("yamoda server init")
logg.info("using database URI: '%s'", app.config["SQLALCHEMY_DATABASE_URI"])
logg.info("running server...")
app.run(debug=options.debug)
