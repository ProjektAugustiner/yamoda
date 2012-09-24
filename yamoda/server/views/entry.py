#  -*- coding: utf-8 -*-
#
# yamoda, (c) 2012, see AUTHORS.  Licensed under the GNU GPL.

"""Entry view functions.
Return entries in various shapes and formats

Functions (all GET):
----------
entry_1D: get values of a 1D array entry in JSON format
entry_1D_1D: get values of two 1D array entries zipped together in JSON format (for x:y plotting)
entry_2D_png: get PNG image link (matplotlib imshow) of a 2D array entry (for x:y plotting)
testentry_1D_1D: used for datadisplaytest

Created on 19.09.2012
@author: dpausp (Tobias Stenzel)
"""
from __future__ import division, absolute_import
import itertools as it

import numpy as np
import logging as logg

from flask import render_template, make_response, request, abort, jsonify
from flask.ext.login import login_required

from yamoda.server import app, db
from yamoda.server.database import Data, Entry, Context


@app.route('/entries1D/<int:entry_id>')
@login_required
def entry_1D(entry_id):
    entry = Entry.query.get_or_404(entry_id)
    if not isinstance(entry.value, np.ndarray):
        abort(415)
    data = list(entry.value)
    return jsonify(data=data, parameter=entry.parameter.name)


@app.route('/entries1D/<int:xid>/<int:yid>')
@login_required
def entry_1D_1D(xid, yid):
    ex = Entry.query.get_or_404(xid)
    ey = Entry.query.get_or_404(yid)
    if not isinstance(ex.value, np.ndarray) or not isinstance(ey.value, np.ndarray) \
       or len(ex.value) != len(ey.value):
        abort(415)
    data = zip(ex.value, ey.value)
    return jsonify(data=data, parameter_x=ex.parameter.name, parameter_y=ey.parameter.name)


@app.route('/entries2D/png/<int:entry_id>')
@login_required
def entry2D_png(entry_id):
    # create image if it doesn't exit
    # return image href
    pass


@app.route('/testentry/<int:yid>')
@login_required
def testentry_1D_1D(yid):
    ctx_id = db.session.query(Context.id).filter_by(name="1DContext").subquery()
    data1D = Data.query.filter(Data.context_id == ctx_id).first()
    entries = dict((e.parameter.name, e) for e in data1D.entries)
    second_param = "T" if yid == 0 else "I"
    logg.info("returning %s", second_param)
    return entry_1D_1D(entries["t"].id, entries[second_param].id)
