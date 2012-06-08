#!/usr/bin/env python
"""Script to test the importer.
"""

import sys

from yamoda.server import app, db
from yamoda.server.database import User, Context, Parameter, Set, Data, Entry

from yamoda.importer import load_importer

impname = sys.argv[1]
filenames = sys.argv[2:]

ctx = Context.query.get(1)
baseset = Set(name='imported')

importer = load_importer(impname)(ctx, baseset)
try:
    importer.import_items(*filenames)
    db.session.add(baseset)
    db.session.commit()
except:
    db.session.rollback()
    raise
