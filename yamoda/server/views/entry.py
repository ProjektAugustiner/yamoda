#  -*- coding: utf-8 -*-
#
# yamoda, (c) 2012, see AUTHORS.  Licensed under the GNU GPL.
"""Entry view functions.
Return entries in various shapes and formats

Functions (all GET):
----------
entry: get an entry in various formats (specified by Accept header)
testentry_1D_1D: used for datadisplaytest

Created on 19.09.2012
@author: dpausp (Tobias Stenzel)
"""
from __future__ import division, absolute_import
import itertools as it

import numpy as np
import pylab
import logging as logg
import os
from functools import partial

from flask import render_template, make_response, request, abort, jsonify, url_for
from flask.ext.login import login_required

from yamoda.server import app, db
from yamoda.server.database import Data, Entry, Context
from yamoda.server.mimerender import html_json_mimerender, mimerender, render_html_exception, render_json_exception, \
    render_txt_exception, render_png_exception
from werkzeug.exceptions import NotFound, UnsupportedMediaType
from flask.helpers import send_from_directory


def _render_entry_json(entry):
    value = entry.value
    if isinstance(value, np.ndarray):
        if len(value.shape) == 1:
            parameter_uri = url_for("parameter", parameter_id=entry.parameter.id)
            parameter_name = entry.parameter.name
            return jsonify(id=entry.id,
                           values=list(entry.value),
                           parameter_uri=parameter_uri,
                           parameter_name=parameter_name)
    return "", 406


def _render_entry_html(entry):
    value = entry.value
    if isinstance(value, np.ndarray):
        if len(value.shape) == 1:
            return render_template("entry1D.html", entry=entry)
    return "", 406


def _render_entry_plain(entry):
    return str(entry.value)


def _save_png_1D(value, filepath):
    logg.debug("saving 1D image to file %s", filepath)
    fig = pylab.figure()
    ax = fig.gca()
    ax.plot(value)
    ax.grid(1)
    fig.savefig(filepath, format="png", bbox_inches='tight', transparent=True)


def _save_png_2D(value, filepath):
    logg.debug("saving 2D image to file %s", filepath)
    fig = pylab.figure()
    ax = fig.gca()
    ax_image = ax.imshow(value)
    fig.colorbar(ax_image)
    ax.grid(1)
    fig.savefig(filepath, format="png", bbox_inches='tight', transparent=True)


def _render_entry_png(entry):
    value = entry.value
    if isinstance(value, np.ndarray):
        directory = os.path.join(os.getcwd(), "yamoda", "server", "static")
        filename = "entry_{}.png".format(entry.id)
        filepath = os.path.join(directory, filename)
        if len(value.shape) == 1:
            save_func = _save_png_1D
        elif len(value.shape) == 2:
            save_func = _save_png_2D
        else:
            return "", 406
        if not os.path.isfile(filepath):
            save_func(value, filepath)
        return send_from_directory(directory, filename, as_attachment=True)
    return "", 406


@app.route('/entries/<int:entry_id>')
@login_required
@mimerender.map_exceptions(
    mapping=(
        (NotFound, 404),
    ),
    html=render_html_exception,
    json=render_json_exception,
    png=render_png_exception,
    txt=render_txt_exception,
)
@mimerender(
    html=_render_entry_html,
    json=_render_entry_json,
    png=_render_entry_png,
    txt=_render_entry_plain
)
def entry(entry_id):
    entry = Entry.query.get(entry_id)
    if entry is None:
        raise NotFound()
    return dict(entry=entry)


@app.route('/entries/<int:xid>/<int:yid>')
@login_required
def entry_1D_1D(xid, yid):
    ex = Entry.query.get_or_404(xid)
    ey = Entry.query.get_or_404(yid)
    if not isinstance(ex.value, np.ndarray) or not isinstance(ey.value, np.ndarray) \
       or len(ex.value) != len(ey.value):
        abort(415)
    data = zip(ex.value, ey.value)
    return jsonify(data=data, parameter_x=ex.parameter.name, parameter_y=ey.parameter.name)


@app.route('/testentry/<int:yid>')
@login_required
def testentry_1D_1D(yid):
    ctx_id = db.session.query(Context.id).filter_by(name="1DContext").subquery()
    data1D = Data.query.filter(Data.context_id == ctx_id).first()
    entries = dict((e.parameter.name, e) for e in data1D.entries)
    second_param = "T" if yid == 0 else "I"
    logg.info("returning %s", second_param)
    return entry_1D_1D(entries["t"].id, entries[second_param].id)
