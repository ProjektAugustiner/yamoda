# use with ipython: ipython -i yamodaconsole.py

from yamoda.server import app, db
from yamoda.server.database import *
import logging
logging.basicConfig(level=logging.INFO)
logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)

q = db.session.query
rollback = db.session.rollback

