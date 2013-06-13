#  -*- coding: utf-8 -*-
#
# yamoda, (c) 2012, see AUTHORS.  Licensed under the GNU GPL.
from flask import send_from_directory
from flask_login import login_required

"""
Flask views for yamoda.
"""

from flask import render_template, redirect, url_for

from yamoda.server import app

# import other modules with views
from yamoda.server.views import user, context, set, data, entry, search, querylanghelp, \
    datadisplaytest, parameter, commenttest, comment


@app.route('/')
def index():
    """displays the main index page"""
    return redirect(url_for('search'))


@app.route("/generated/<filename>", methods=["GET"])
@login_required
def generated(filename):
    """Serve generated files from a directory
    """
    directory = app.config["GENERATED_DIR"]
    return send_from_directory(directory=directory, filename=filename, as_attachment=True)
