import logging as logg
import sys
logg.basicConfig(level=logg.DEBUG, stream=sys.stdout)
# INFO shows SQL statements, DEBUG even shows raw result sets
# logg.getLogger("sqlalchemy.engine").setLevel(logging.INFO)

from optparse import OptionParser
from yamoda.server import app
from yamoda.server.database.dbsettings import DATABASE_URIS


DATABASE_URIS = {
    "sqlite": "sqlite:////tmp/test.db",
    "mysql": "mysql://yamoda:yamoda@localhost/yamoda",
    "postgres": "postgresql+psycopg2://yamoda:yamoda@/yamoda",
    "postgres-test": "postgresql+psycopg2://yamoda:yamoda@/yamoda-test"
}


def application(database='sqlite'):
    """Application factory function.

    :param database: A string selecting the database backend or the database
	uri. Available backends are 'sqlite', 'mysql' and 'postgres'.

    :returns: A configured flask application object.

    Additional keyword arguments can be passed as keyword arguments. They will
    be used to configure the application.

    """
    logg.info('Yamoda Server init.')

    # configure application
    app.config.from_object('yamoda.server.default_settings')
    app.config.from_envvar('YAMODA_SETTINGS')

    uri = DATABASE_URIS.get(database, database)
    logg.info("using database URI: {0}".format(uri)
    app.config["SQLALCHEMY_DATABASE_URI"] = uri
    return app


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
