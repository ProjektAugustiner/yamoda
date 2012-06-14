#!/usr/bin/env python
"""Script to test the importer.
"""

import sys

from yamoda.server import app, db
from yamoda.server.database import User, Group, Context, Parameter, Set, Data, Entry

from yamoda.importer import load_importer

impname = sys.argv[1]
filenames = sys.argv[2:]

ctx = Context.query.get(1)
usr = User.query.filter_by(name='admin').first()
grp = Group.query.filter_by(name='admin').first()
baseset = Set(name='imported', user=usr, group=grp)

importer = load_importer(impname)(ctx, baseset)
try:
    importer.import_items(*filenames)
    db.session.add(baseset)
    db.session.commit()
except:
    db.session.rollback()
    raise
