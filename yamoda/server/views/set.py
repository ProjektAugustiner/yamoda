#  -*- coding: utf-8 -*-
#
# yamoda, (c) 2012, see AUTHORS.  Licensed under the GNU GPL.

"""
Data set related views.
"""

from flask import render_template
from flask.ext.login import login_required

from yamoda.server import app
from yamoda.server.database import Set


@app.route('/data')
@login_required
def data_view(all=False):
    setlist = Set.query.all()
    for s in setlist:
        print s.readable()
    return render_template('setlist.html', sets=setlist)
