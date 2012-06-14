#!/usr/bin/env python
"""Script to create the database schema and populate with test data."""

import random
from datetime import datetime
from optparse import OptionParser

from yamoda.server import db
from yamoda.server.database import User, Group, Context, Parameter, Set, Data, Entry


parser = OptionParser()
parser.add_option('--testdata', dest='testdata', default=True,
                  help='create some test data')
(options, args) = parser.parse_args()

print 'creating schema...'
db.drop_all()
db.create_all()

if options.testdata:
    print 'adding users: admin:admin and user:user'
    admin_group = Group(name='admin')
    user_group = Group(name='users')
    admin = User(name='admin', password='admin', primary_group=admin_group)
    user = User(name='user', password='user', primary_group=user_group)
    db.session.add(admin)
    db.session.add(user)

    print 'adding "TestContext" context'
    brief = 'This is the short description of the test context.'
    desc = """
    Lorem ipsum dolor sit amet, consectetur adipisici elit, sed eiusmod tempor
    incidunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis
    nostrud exercitation ullamco laboris nisi ut aliquid ex ea commodi
    consequat. Quis aute iure reprehenderit in voluptate velit esse cillum
    dolore eu fugiat nulla pariatur. Excepteur sint obcaecat cupiditat non
    proident, sunt in culpa qui officia deserunt mollit anim id est laborum.
    """
    ctx = Context(name='TestContext', brief=brief, description=desc)
    db.session.add(ctx)

    print 'adding some test parameters'
    par_T = Parameter(
        name='T', brief='Temperature',
        description='This is the description of the temperature',
        unit='K', context=ctx, visible=True)
    par_om = Parameter(
        name='omega', brief='Rocking angle',
        description='The omega parameter represents the rocking angle.',
        unit='deg', context=ctx, visible=True)

    db.session.add(par_T)
    db.session.add(par_om)

    print 'constructing some test data'
    children = []
    for i in range(5):
        datas = []
        for j in range(10):
            e1 = Entry(value=random.random()*270, parameter=par_T)
            e2 = Entry(value=random.random()*50, parameter=par_om)
            datas.append(Data(name='random data', entries=[e1, e2]))
        children.append(Set(name='set %d' % i, datas=datas,
                            user=user, group=user_group))
    #create admin only visible set
    admin_set = Set(name="admin-only", user=admin, group=admin_group,
                    group_readable=False, all_readable=False)
    children.append(admin_set)
    superset = Set(name='superset', children=children,
                   user=admin, group=admin_group)
    db.session.add(superset)

    db.session.commit()
