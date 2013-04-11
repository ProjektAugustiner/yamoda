# use with ipython: ipython -i console-env.py

import logging as logg
logg.basicConfig(level=logg.INFO)
logg.getLogger("sqlalchemy.engine").setLevel(logg.INFO)

from yamoda.server import make_app

app = make_app()

from yamoda.server import db
from yamoda.server.database import *

import yamoda.query.alchemy as alchemy
import yamoda.query.test.testqueries as tq

from yamoda.server.example_dbsettings import DATABASE_URIS

q = db.session.query
rollback = db.session.rollback

available_dbs = DATABASE_URIS.iterkeys()
default_db = next(DATABASE_URIS.iterkeys())
database = raw_input("database connector ({}, default {}): ".format("|".join(available_dbs), default_db))
if not database.strip():
    database = default_db

app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URIS[database]

logg.info("using database URI: '%s'", app.config["SQLALCHEMY_DATABASE_URI"])

