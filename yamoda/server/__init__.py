#  -*- coding: utf-8 -*-
#
# yamoda, (c) 2012, see AUTHORS.  Licensed under the GNU GPL.

from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import LoginManager

from jinja2 import Markup

import markdown2

try:
    import matplotlib
    matplotlib.use('agg')
except ImportError:
    pass

# configuration
#SQLALCHEMY_DATABASE_URI = 'sqlite:////tmp/test.db'
SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://yamoda:bla@/yamoda'
#SQLALCHEMY_DATABASE_URI = 'mysql://yamoda:bla@localhost/yamoda'
DEBUG = True
SECRET_KEY = 'development key'

# create application
app = Flask('yamoda.server')
app.config.from_object(__name__)
app.config.from_envvar('YAMODA_SETTINGS', silent=True)

# database
db = SQLAlchemy(app)

# login
login_manager = LoginManager()
login_manager.setup_app(app)
login_manager.login_view = 'login'


def datetimeformat(value, format='%Y-%m-%d %H:%M'):
    return value.strftime(format)


def dataformat(value):
    if value is None:
        return ''
    elif isinstance(value, float):
        fmt = '%.5g' % value
        if 'e' in fmt:
            fmt = Markup(fmt.replace('e', ' &times; 10<sup>') + '</sup>')
        return fmt
    return str(value)


def unitformat(value):
    if value is None:
        return ''
    return value
md = markdown2.Markdown(safe_mode='escape')


def markdown(value):
    return Markup(md.convert(value))
app.jinja_env.filters['dtformat'] = datetimeformat
app.jinja_env.filters['dataformat'] = dataformat
app.jinja_env.filters['unitformat'] = unitformat
app.jinja_env.filters['markdown'] = markdown

import yamoda.server.views
import yamoda.server.database
