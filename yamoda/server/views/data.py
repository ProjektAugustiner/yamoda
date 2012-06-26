#  -*- coding: utf-8 -*-
#
# yamoda, (c) 2012, see AUTHORS.  Licensed under the GNU GPL.

"""
Data related views.
"""

import cStringIO

from numpy import ndarray

from flask import render_template, make_response, request, abort, jsonify
from flask.ext.login import login_required

from yamoda.server import app, db
from yamoda.server.database import Data, Entry


@app.route('/data/<int:id>')
@login_required
def data(id):
    d = Data.query.get_or_404(id)
    return render_template('data.html', data=d)


@app.route('/data/delete', methods=['POST'])
@login_required
def datadelete():
    try:
        ids = map(int, request.form.getlist('ids[]'))
        for id in ids:
            d = Data.query.get(id)
            #if d.writeable():  # XXX Data is not AccessControl'd
            db.session.delete(d)
        db.session.commit()
    except Exception, err:
        return jsonify(result='error', data=str(err))
    return jsonify(result='success', data=None)


@app.route('/entry/plot/<int:xid>/<int:yid>')
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
