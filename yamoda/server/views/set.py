#  -*- coding: utf-8 -*-
#
# yamoda, (c) 2012, see AUTHORS.  Licensed under the GNU GPL.

"""
Data set related views.
"""

from flask import render_template, request
from flask.ext.login import login_required, current_user

from yamoda.server import app
from yamoda.server.database import Set


@app.route('/set/<id>')
@login_required
def set(id):
    s = Set.query.get_or_404(id)
    return render_template('set.html', set=s)


@app.route('/sets')
@app.route('/sets/<which>')
@login_required
def setlist(which='mine'):
    if which == 'all':
        setlist = Set.query.all()
    else:
        setlist = Set.query.filter_by(user=current_user)
    for s in setlist:
        print s.readable()
    return render_template('setlist.html', sets=setlist)
