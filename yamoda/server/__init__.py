#  -*- coding: utf-8 -*-
#
# yamoda, (c) 2012, see AUTHORS.  Licensed under the GNU GPL.

import logging
import json
from flask import Flask, request, flash, redirect, current_app, jsonify, make_response
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import LoginManager, user_unauthorized, login_url
from numpy import ndarray

from jinja2 import Markup
from werkzeug.exceptions import Unauthorized
from mimeparse import best_match
import markdown2
from yamoda.server.mimerender import mimerender

try:
    import matplotlib
    matplotlib.use('agg')
except ImportError:
    pass


logg = logging.getLogger("yamoda.server")

# configuration
DEBUG = True
SECRET_KEY = 'development key'

# create application
app = Flask('yamoda.server')

app.config.from_object(__name__)
app.config.from_envvar('YAMODA_SETTINGS', silent=True)

# database
db = SQLAlchemy(app)


class MimeLoginManager(LoginManager):
    @mimerender(
        html=lambda login_uri: redirect(login_uri),
        json=lambda login_uri: make_response(json.dumps(dict(login_uri=login_uri, msg="not logged in")), 401)
        )
    def unauthorized(self):
        """This is called when the user is required to log in.
        adapted from LoginManager.unauthorized
        """
        logg.debug("called unauthorized")
        user_unauthorized.send(current_app)
        if self.login_message:
            flash(self.login_message)
        return dict(login_uri=login_url(self.login_view, request.url))

# login
login_manager = MimeLoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


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
    elif isinstance(value, ndarray):
        # return arrays as 1, 2, 3, 4 ... for use with jquery.sparkline
        return ", ".join(["{:.16f}".format(v) for v in value])
    return str(value)


def jsonformat(value):
    return json.dumps(value)


def unitformat(value):
    if value is None:
        return ''
    return value


def yesnoformat(truth_value):
    if truth_value:
        return "yes"
    else:
        return "no"


md = markdown2.Markdown(safe_mode='escape')


def markdown(value):
    return Markup(md.convert(value))


app.jinja_env.filters['dtformat'] = datetimeformat
app.jinja_env.filters['dataformat'] = dataformat
app.jinja_env.filters['unitformat'] = unitformat
app.jinja_env.filters['markdown'] = markdown
app.jinja_env.filters['yesnoformat'] = yesnoformat

import yamoda.server.views
import yamoda.server.database
