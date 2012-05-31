#!/usr/bin/env python
"""Script to start the yamoda development server.

The runserver.py script starts the yamoda server. It accepts several command
line arguments. For a complete list pass the "--help" option. Ctrl-C stops the
server.

"""

import os
import random
from optparse import OptionParser

from yamoda.server import app, db
from yamoda.server.database import User, Context, Parameter, Set, Data, Entry


parser = OptionParser()
parser.add_option('--debug', dest='debug', default=True,
                  help='enable Flask debug mode')
parser.add_option('--init-db', dest='init_db', default=True,
                  help='initializes the database with test data')
(options, args) = parser.parse_args()

# do not run the init_db step twice if running under the Werkzeug reloader
if options.init_db and os.environ.get('WERKZEUG_RUN_MAIN') != 'true':
    db.drop_all()
    db.create_all()

    print 'adding user:admin pw:password'
    admin = User(name='admin', password='password')
    db.session.add(admin)

    print 'adding "test" context'
    ctx = Context(name='test')
    db.session.add(ctx)

    print 'adding some test parameters'
    par_T = Parameter(name='T', brief='Temperature', context=ctx, visible=True)
    par_om = Parameter(name='om', brief='Rocking angle', context=ctx, visible=True)
    db.session.add(par_T)
    db.session.add(par_om)

    print 'constructing some test data'
    children = []
    for i in range(5):
        datas = []
        for j in range(10):
            e1 = Entry(value=random.random()*270, parameter=par_T)
            e2 = Entry(value=random.random()*50, parameter=par_om)
            datas.append(Data(entries=[e1, e2]))
        children.append(Set(datas=datas))
    superset = Set(children=children)
    db.session.add(superset)

    db.session.commit()

#start server
app.run(debug=options.debug)
