#  -*- coding: utf-8 -*-
#
# yamoda, (c) 2012, see AUTHORS.  Licensed under the GNU GPL.

'''
Created on 06.09.2012
@author: dpausp (Tobias Stenzel)
'''
from __future__ import division, absolute_import
from random import random
import logging
from collections import OrderedDict
import datetime


from yamoda.server import make_app
app = make_app(DEBUG=True)
from yamoda.server import db
from yamoda.server.database import User, Group, Context, Parameter, \
     Set, Data, Entry
from yamoda.server.example_dbsettings import DATABASE_URIS

logg = logging.getLogger(__name__)
# logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)

app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URIS["sqlite"]
logg.info("using database URI: '%s'", app.config["SQLALCHEMY_DATABASE_URI"])

sets = []
data_testcases = {}
set_testcases = {}


def drop_schema():
    logg.info("cleaning up db...")
    db.drop_all()
    db.session.commit()


def create_schema():
    logg.info("create schema...")
    db.create_all()
    db.session.commit()


def add_users():
    logg.info("creating groups admins and users")
    admin_group = Group(name='admins')
    user_group = Group(name='users')
    db.session.add(admin_group)
    db.session.add(user_group)
    logg.info("creating users admin and user")
    admin = User(name='admin', password='admin', primary_group=admin_group)
    user = User(name='user', password='user', primary_group=user_group)
    db.session.add(admin)
    db.session.add(user)
    db.session.commit()


def add_context0():
    brief = "This is the short description of the test context."
    desc = """\
Lorem *ipsum* dolor sit amet, consectetur adipisici elit, sed eiusmod tempor
incidunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis
nostrud exercitation ullamco laboris nisi ut aliquid ex ea commodi
consequat.

* Quis aute iure reprehenderit in voluptate velit esse cillum
* dolore eu fugiat nulla pariatur. Excepteur sint obcaecat cupiditat non
* proident, sunt in culpa qui officia deserunt mollit anim id est laborum.
"""
    logg.info("creating context TestContext")
    ctx = Context(name='TestContext', brief=brief, description=desc)
    db.session.add(ctx)

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
    db.session.commit()
    logg.info("created params %s and %s", id(par_T), id(par_om))
    logg.info("names %s and %s", par_T.name, par_om.name)


def add_context1():
    brief = "This is some context."
    desc = "This is a loooooong description of the context."
    logg.info("creating context SomeContext")
    ctx = Context(name='SomeContext', brief=brief, description=desc)
    db.session.add(ctx)

    par_T = Parameter(
        name='T', brief='temp',
        description='describe the temperature',
        unit='K', context=ctx, visible=True)
    par_p = Parameter(
        name='p', brief='pressure',
        description="some pressure value",
        unit='MPa', context=ctx, visible=True)

    db.session.add(par_T)
    db.session.add(par_p)
    db.session.commit()
    logg.info("created params %s and %s", id(par_T), id(par_p))
    logg.info("names %s and %s", par_T.name, par_p.name)


def add_contexts():
    add_context0()
    add_context1()


def add_set0():
    logg.info("creating set0")
    creation_dt = datetime.datetime(year=2011, month=6, day=10, hour=13, minute=37)
    st = Set(created=creation_dt, name="set0",
             user=User.query.filter_by(name="admin").one(), group=Group.query.filter_by(name="admins").one())
    ctx = Context.query.filter_by(name="TestContext").one()
    params = dict((p.name, p) for p in ctx.parameters)
    logg.info("params from db %s", params)
    datas = []
    for j in xrange(5):
        entry_om = Entry(value=(5 - j) * 1000.0, parameter=params["omega"])
        entry_T = Entry(value=j * 100.0, parameter=params["T"])
        data = Data(name="data{}/{}".format("set0", j), entries=[entry_T, entry_om], context=ctx)
        db.session.add(data)
        db.session.commit()
        datas.append(data)

    st.datas = datas
    db.session.add(st)
    db.session.commit()
    return st


def add_set1():
    logg.info("creating set1")
    creation_dt = datetime.datetime(year=2012, month=4, day=12, hour=13, minute=37)
    st = Set(created=creation_dt, name="set1",
             user=User.query.filter_by(name="user").one(), group=Group.query.filter_by(name="users").one())
    ctx = Context.query.filter_by(name="SomeContext").one()
    params = dict((p.name, p) for p in ctx.parameters)
    datas = []
    for j in xrange(5):
        entry_p = Entry(value=10.0 * j, parameter=params["p"])
        entry_T = Entry(value=100 + j * 50.0, parameter=params["T"])
        data = Data(name="data{}/{}".format("set1", j), entries=[entry_T, entry_p], context=ctx)
        db.session.add(data)
        db.session.commit()
        datas.append(data)

    st.datas = datas
    db.session.add(st)
    db.session.commit()
    return st


def add_sets():
    return add_set0(), add_set1()


def create_data_cases(set0, set1):
    def cmp_data(d0, d1):
        return cmp(d0.id, d1.id)

    d0 = sorted(set0.datas, cmp_data)
    logg.info("datas %s", d0)
    d1 = sorted(set1.datas, cmp_data)
    data_testcases["find:datas, T: > 210"] = d0[3:] + d1[3:]
    data_testcases["find:datas, T: < 210"] = d0[:3] + d1[:3]
    data_testcases["find:datas, T: < 0"] = []
    data_testcases["find:datas, context: NotExisting"] = []
    data_testcases["find:datas, context: TestContext, T: < 210"] = d0[:3]
    data_testcases["find:datas, context: TestContext, T: 60 to 210"] = d0[1:3]
    data_testcases["find:datas, context: TestContext, T: 60 to 210 or > 380"] = d0[1:3] + [d0[4]]
    data_testcases["find:datas, context: TestContext, sort: omega.desc"] = d0
    data_testcases["find:datas, context: TestContext, sort: T.asc"] = d0
    data_testcases["find:datas, context: TestContext, sort: T.desc"] = d0[::-1]
    data_testcases["find:datas, context: TestContext, sort: omega"] = d0[::-1]
    data_testcases["find:datas, context: TestContext, sort: omega.desc, limit: 2"] = d0[:2]


def create_set_cases(s0, s1):
    set_testcases["find: sets, user: admin"] = [s0]
    set_testcases["find: sets, user: user"] = [s1]
    set_testcases["find: sets, created: 9 June 2011 to 11 August 2011 "] = [s0]
    set_testcases["find: sets, user: dummy"] = []
    set_testcases["find: sets, created: 9 March 2012 to 11 December 2012"] = [s1]
    set_testcases["find: sets, user: user, created: 9 March 2012 to 11 December 2012"] = [s1]
    set_testcases["find: sets, created: 9 March 2015 to 11 December 2019"] = []


def create_complete_env():
    try:
        drop_schema()
        create_schema()
        add_users()
        add_contexts()
        set0, set1 = add_sets()
        create_data_cases(set0, set1)
        create_set_cases(set0, set1)
        db.session.commit()
    finally:
        db.session.rollback()
