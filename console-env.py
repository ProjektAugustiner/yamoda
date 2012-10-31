# use with ipython: ipython -i console-env.py

import logging as logg
logg.basicConfig(level=logg.INFO)
logg.getLogger("sqlalchemy.engine").setLevel(logg.INFO)

from yamoda.server import app, db
from yamoda.server.database import *

import yamoda.query.alchemy as alchemy
import yamoda.query.test.testqueries as tq

from dbsettings import DATABASE_URIS

q = db.session.query
rollback = db.session.rollback

DATABASE = "sqlite"
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URIS[DATABASE]

logg.info("using database URI: '%s'", app.config["SQLALCHEMY_DATABASE_URI"])

