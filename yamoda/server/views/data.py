#  -*- coding: utf-8 -*-
#
# yamoda, (c) 2012, see AUTHORS.  Licensed under the GNU GPL.

"""
Data related views.
"""

from flask import render_template, request
from flask.ext.login import login_required, current_user

from yamoda.server import app
from yamoda.server.database import Data


@app.route('/data/<id>')
@login_required
def data(id):
    d = Data.query.get_or_404(id)
    return render_template('data.html', data=d)
