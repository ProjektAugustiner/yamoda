#  -*- coding: utf-8 -*-
#
# yamoda, (c) 2012, see AUTHORS.  Licensed under the GNU GPL.

import logging
import json
from flask import Flask, request, flash, redirect, current_app, jsonify, make_response
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import LoginManager, user_unauthorized, login_url
from numpy import ndarray, std, average

from jinja2 import Markup
from werkzeug.exceptions import Unauthorized
from mimeparse import best_match
import markdown2
from yamoda.server.mimerender import mimerender
import os

try:
    import matplotlib
    matplotlib.use('agg')

    font = {
        'family': 'normal',
        'weight': 'bold',
        'size': 14
    }
    matplotlib.rc('font', **font)
except ImportError:
    pass


logg = logging.getLogger("yamoda.server")

# configuration
DEBUG = True
SECRET_KEY = 'development key'

# create application
app = Flask('yamoda.server')
app.jinja_env.add_extension("yamoda.server.coffeeforjinja.CoffeeExtension")

app.config.from_object(__name__)
app.config["GENERATED_DIR"] = os.path.join(os.getcwd(), "yamoda", "server", "generated")

# Flask-Sqlalchemy object.
# This is not yet bound to the flask application, must be done in the
# application factory function.
db = SQLAlchemy()


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


def dataformat(value, maxlen=None):
    """Format data for HTML display
    The returned value is compatible with JQuery.sparkline
    """
    if value is None:
        return ''
    elif isinstance(value, float):
        fmt = '%.5g' % value
        if 'e' in fmt:
            fmt = Markup(fmt.replace('e', ' &times; 10<sup>') + '</sup>')
        return fmt
    elif isinstance(value, ndarray):
        # return arrays as 1, 2, 3, 4 ... for use with jquery.sparkline
        if maxlen is not None:
            # if array is too long: shorten array by sampling it
            step = max(len(value) // maxlen, 1)
            value = value[::step]
            if step > 1:
                # if we omit values we must send matching xvalues so that sparkline knows what to do
                return ", ".join(["{}:{:.8f}".format(i * step, v) for i, v in enumerate(value)])
        # just send yvalues
        logg.debug("type %s, values: %s", type(value), value)
        return ", ".join("{:.8f}".format(v) for v in value.ravel())
    return str(value)


def count_formatted(value, maxlen=None):
    """Return count of values as returned by dataformat with same maxlen argument"""
    if maxlen is None:
        return valuecount(value)
    else:
        # if array is too long: shorten array by sampling it
        step = max(len(value) // maxlen, 1)
        return valuecount(value[::step])


def normal_min(value):
    return average(value) - std(value)


def normal_max(value):
    return average(value) + std(value)


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


def valuecount(value):
    if isinstance(value, ndarray):
        return len(value.ravel())
    else:
        return len(value)


def markdown(value):
    return Markup(md.convert(value))


def shape(value):
    """Shape.
    :param value: float, int or ndarray are recognized
    :returns: string "scalar" or numpy shape, like "100, 100"
    """
    if isinstance(value, float) or isinstance(value, int):
        return "scalar"
    if isinstance(value, ndarray):
        shapestr = str(value.shape).strip("(),")
        return shapestr
    else:
        return "unknown"


def dimension(value):
    if isinstance(value, float) or isinstance(value, int):
        return 0
    if isinstance(value, ndarray):
        return len(value.shape)
    else:
        return "unknown"

# matplot setup

font = {'family': 'normal',
        'weight': 'bold',
        'size': 14}

matplotlib.rc('font', **font)


# add all jinja filters used in the project below

app.jinja_env.filters['dtformat'] = datetimeformat
app.jinja_env.filters['dataformat'] = dataformat
app.jinja_env.filters['unitformat'] = unitformat
app.jinja_env.filters['markdown'] = markdown
app.jinja_env.filters['yesnoformat'] = yesnoformat
app.jinja_env.filters['average'] = average
app.jinja_env.filters['normal_min'] = normal_min
app.jinja_env.filters['normal_max'] = normal_max
app.jinja_env.filters['min'] = min
app.jinja_env.filters['max'] = max
app.jinja_env.filters['valuecount'] = valuecount
app.jinja_env.filters['count_formatted'] = count_formatted
app.jinja_env.filters['shape'] = shape
app.jinja_env.filters['dimension'] = dimension

import yamoda.server.views
import yamoda.server.database
