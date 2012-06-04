#  -*- coding: utf-8 -*-
#
# yamoda, (c) 2012, see AUTHORS.  Licensed under the GNU GPL.

from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import LoginManager

# configuration
SQLALCHEMY_DATABASE_URI = 'sqlite:////tmp/test.db'
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
login_manager.login_view = 'yamoda.server.views.login'


import yamoda.server.views
import yamoda.server.database
