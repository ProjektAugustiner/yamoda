import logging as logg
import sys
logg.basicConfig(level=logg.DEBUG, stream=sys.stdout)
# INFO shows SQL statements, DEBUG even shows raw result sets
# logg.getLogger("sqlalchemy.engine").setLevel(logging.INFO)

from optparse import OptionParser
from yamoda.server import app
from yamoda.server.database.dbsettings import DATABASE_URIS


def run_server(argv=sys.argv):
    parser = OptionParser()
    parser.add_option('--debug', dest='debug', default=False,
                      help='enable Flask debug mode')
    parser.add_option('--database', dest='database', default="sqlite",
                      help='Select Database backend (sqlite | mysql | postgres)')
    (options, args) = parser.parse_args()

    app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URIS[options.database]

    # start server
    logg.info("yamoda server init")
    logg.info("using database URI: '%s'", app.config["SQLALCHEMY_DATABASE_URI"])
    logg.info("running server...")
    app.run(debug=options.debug, port=5000, host="0.0.0.0")
