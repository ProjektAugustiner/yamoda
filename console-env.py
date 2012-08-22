# use with ipython: ipython -i yamodaconsole.py

import logging
logging.basicConfig(level=logging.INFO)
logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)

from yamoda.server import app, db
from yamoda.server.database import *

import yamoda.query.alchemy as alchemy
import yamoda.query.test.testqueries as tq

q = db.session.query
rollback = db.session.rollback

