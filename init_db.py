#!/usr/bin/env python
"""Script to create the database schema and populate with test data."""

import random
from optparse import OptionParser

from yamoda.server import db
from yamoda.server.database import User, Context, Parameter, Set, Data, Entry


parser = OptionParser()
parser.add_option('--testdata', dest='testdata', default=True,
                  help='create some test data')
(options, args) = parser.parse_args()

print 'creating schema...'
db.drop_all()
db.create_all()

if options.testdata:
    print 'adding user:admin pw:password'
    admin = User(name='admin', password='password')
    db.session.add(admin)

    print 'adding "test" context'
    ctx = Context(name='test')
    db.session.add(ctx)

    print 'adding some test parameters'
    par_T = Parameter(name='T', brief='Temperature', unit='K', context=ctx, visible=True)
    par_om = Parameter(name='om', brief='Rocking angle', unit='deg', context=ctx, visible=True)
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
