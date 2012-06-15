#  -*- coding: utf-8 -*-
#
# yamoda, (c) 2012, see AUTHORS.  Licensed under the GNU GPL.

"""
Data related views.
"""

import cStringIO

from numpy import ndarray

from flask import render_template, make_response, abort
from flask.ext.login import login_required

from yamoda.server import app
from yamoda.server.database import Data, Entry


@app.route('/data/<id>')
@login_required
def data(id):
    d = Data.query.get_or_404(id)
    return render_template('data.html', data=d)


@app.route('/entry/plot/<xid>/<yid>')
@login_required
def plot(yid, xid):
    import matplotlib.pyplot as plt

    ex = Entry.query.get_or_404(xid)
    ey = Entry.query.get_or_404(yid)
    if not isinstance(ex.value, ndarray) or not isinstance(ey.value, ndarray) \
       or len(ex.value) != len(ey.value):
        abort(415)
    fig = plt.figure()
    ax = fig.gca()
    ax.plot(ex.value, ey.value)
    ax.set_xlabel('%s (%s)' % (ex.parameter.name, ex.parameter.unit))
    ax.set_ylabel('%s (%s)' % (ey.parameter.name, ey.parameter.unit))
    fp = cStringIO.StringIO()
    fig.savefig(fp)
    resp = make_response(fp.getvalue())
    resp.headers['Content-Type'] = 'image/png'
    return resp
