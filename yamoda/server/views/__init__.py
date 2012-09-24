#  -*- coding: utf-8 -*-
#
# yamoda, (c) 2012, see AUTHORS.  Licensed under the GNU GPL.

"""
Flask views for yamoda.
"""

from flask import render_template

from yamoda.server import app

# import other modules with views
from yamoda.server.views import user, context, set, data, entry, search, querylanghelp, datadisplaytest


@app.route('/')
def index():
    """displays the main index page"""
    return render_template('index.html')
