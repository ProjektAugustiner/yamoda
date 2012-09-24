#!/usr/bin/env python
"""Script to create the database schema and populate with test data."""

import random
import logging as logg
logg.basicConfig(level=logg.INFO)
#logg.getLogger("sqlalchemy.engine").setLevel(logging.INFO)
from optparse import OptionParser

import numpy as np

from yamoda.server import db, app
from yamoda.server.database import User, Group, Context, Parameter, \
     Set, Data, Entry
from dbsettings import DATABASE_URIS


parser = OptionParser()
parser.add_option('--testdata', dest='testdata', default=True,
                  help='create some test data')
parser.add_option('--database', dest='database', default="sqlite",
                  help='Select Database backend (sqlite | mysql | postgres)')
(options, args) = parser.parse_args()

app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URIS[options.database]

logg.info("using database URI: '%s'", app.config["SQLALCHEMY_DATABASE_URI"])

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

    def create_testdata_scalar():
        print 'adding "TestContext" context'
        brief = 'This is the short description of the test context.'
        desc = """\
    Lorem *ipsum* dolor sit amet, consectetur adipisici elit, sed eiusmod tempor
    incidunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis
    nostrud exercitation ullamco laboris nisi ut aliquid ex ea commodi
    consequat.
    * Quis aute iure reprehenderit in voluptate velit esse cillum
    * dolore eu fugiat nulla pariatur. Excepteur sint obcaecat cupiditat non
    * proident, sunt in culpa qui officia deserunt mollit anim id est laborum.
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
                e1 = Entry(value=random.random() * 270, parameter=par_T)
                e2 = Entry(value=random.random() * 5000000, parameter=par_om)
                datas.append(Data(name='random data', entries=[e1, e2],
                                  context=ctx))
            children.append(Set(name='set %d' % i, datas=datas,
                                user=user, group=user_group))
        # create admin only visible set
        admin_set = Set(name="admin-only", user=admin, group=admin_group,
                        group_readable=False, all_readable=False)
        children.append(admin_set)
        superset = Set(name='superset', children=children,
                       user=admin, group=admin_group)
        db.session.add(superset)
        db.session.commit()

    def create_testdata_1D():
        ### 1D test data context
        print "adding 1DContext"
        brief = 'just a time series'
        desc = "spam"
        ctx = Context(name='1DContext', brief=brief, description=desc)
        db.session.add(ctx)

        par_t = Parameter(
            name='t', brief='time',
            description='time of measurement, starting with 0',
            unit='ms', context=ctx, visible=True)

        par_T = Parameter(
            name='T', brief='Temperature',
            description="1D Array of temperature values",
            unit='K', context=ctx, visible=True)

        par_I = Parameter(
            name='I', brief='Current',
            description="1D Array of electric current values",
            unit='mA', context=ctx, visible=True)

        db.session.add(par_t)
        db.session.add(par_T)
        db.session.add(par_I)

        val_t = np.linspace(0, 10, 100)
        val_T = np.random.random(100)
        val_I = np.random.random(100) * 10
        e_t = Entry(value=val_t, parameter=par_t)
        e_T = Entry(value=val_T, parameter=par_T)
        e_I = Entry(value=val_I, parameter=par_I)
        db.session.add(e_t)
        db.session.add(e_T)
        data = Data(name="random time series", entries=[e_t, e_T, e_I], context=ctx)
        db.session.add(data)
        a_set = Set(name="set 1D", datas=[data], user=admin, group=admin_group)
        db.session.add(a_set)
        db.session.commit()

    create_testdata_scalar()
    create_testdata_1D()

