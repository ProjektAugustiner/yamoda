#  -*- coding: utf-8 -*-
#
# yamoda, (c) 2012, see AUTHORS.  Licensed under the GNU GPL.

import logging
import json
import os
from pprint import pformat
from flask import Flask, request, flash, redirect, current_app, jsonify, make_response
from flask.ext.sqlalchemy import SQLAlchemy
from numpy import ndarray, std, average

from jinja2 import Markup
from werkzeug.exceptions import Unauthorized
from mimeparse import best_match
import markdown2

from yamoda.server.mimerender import mimerender
from . import jinja_filters
from . import default_settings
from .login import MimeLoginManager

try:
    import matplotlib
    matplotlib.use('agg')
except ImportError:
    pass


logg = logging.getLogger(__name__)


# globally used flask application objects, set via make_app
app = None
db = None
login_manager = None


def _add_jinja_filters_from_module(app, filter_module):
    '''Add all functions from a module as jinja2 template filters.
    Functions starting with a _ are ignored.
    :param app: Flask App to add filters to.
    :param filter_module: module which contains filter functions at module level.
    '''
    for key in dir(filter_module):
        if not key.startswith("_"):
            val = getattr(filter_module, key)
            if callable(val):
                app.jinja_env.filters[key] = val


def make_app(**app_options):
    '''Create YAMODA flask app.
    :param app_options: dict-like object which contains additonal settings, for example cmd line options.
    These settings override all other configuration settings.
    :returns: flask app object ready for use
    '''
    global app, db, login_manager
    # XXX: just for development, change to better logging configuration later!
    logging.basicConfig(level=logging.DEBUG)
    logg.info("creating flask app %s", __name__)
    app = Flask(__name__)
    # add our own extension to compile coffeescript code snippets in jinja2 templates
    app.jinja_env.add_extension("yamoda.server.coffeeforjinja.CoffeeExtension")

    app.config.from_object(default_settings)
    configfile_present = app.config.from_envvar('YAMODA_SETTINGS', silent=True)
    if configfile_present:
        logg.info("using config file ($YAMODA_SETTINGS) @ %s", os.environ["YAMODA_SETTINGS"])
    if app_options:
        app.config.update(app_options)
    logg.info("using database URI: '%s'", app.config["SQLALCHEMY_DATABASE_URI"])
    logg.debug("config is %s", pformat(dict(app.config)))
    # create generated content dir if not present
    generated_dir = app.config["GENERATED_DIR"]
    if not os.path.exists(generated_dir):
        os.mkdir(generated_dir)
    # login settings
    login_manager = MimeLoginManager()
    login_manager.init_app(app)
    login_manager.login_view = "login"
    # database
    db = SQLAlchemy(app)
    # jinja filters
    _add_jinja_filters_from_module(app, jinja_filters)
    # matplot setup
    matplotlib.rc('font', **app.config["MATPLOTLIB_FONT"])
    from . import views
    from . import database
    return app
