#  -*- coding: utf-8 -*-
#
# yamoda, (c) 2012, see AUTHORS.  Licensed under the GNU GPL.
'''
Run YAMODA with a standalone test server. Not intended for production use!
'''

import logging
import sys
logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)
# INFO shows SQL statements, DEBUG even shows raw result sets
# logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)

from optparse import OptionParser
from .server import make_app
from .server.example_dbsettings import DATABASE_URIS

logg = logging.getLogger()


def run_server(argv=sys.argv):
    parser = OptionParser()
    parser.add_option('--debug', dest='debug', default=False,
                      help='enable Flask debug mode')
    parser.add_option('--database', dest='database',
                      help='Select Database backend (sqlite | mysql | postgres)')
    parser.add_option('--host', dest='host', default="127.0.0.1",
                      help='Server host to use')
    parser.add_option('--port', dest='port', default=5000, type="int",
                      help='Server port to use')
    options, _ = parser.parse_args()

    app_options = dict(DEBUG=options.debug)
    if options.database:
        app_options["SQLALCHEMY_DATABASE_URI"] = DATABASE_URIS[options.database]

    app = make_app(**app_options)
    # start server
    logg.info("yamoda server init")
    logg.info("running server...")
    app.run(debug=options.debug, host=options.host, port=options.port)
