#  -*- coding: utf-8 -*-
#
# yamoda, (c) 2012, see AUTHORS.  Licensed under the GNU GPL.
from werkzeug.exceptions import NotFound
from flask.helpers import url_for
from yamoda.server.mimerender import html_json_mimerender

"""
Data related views.

data: render a data instance (HTML or JSON)
datadelete: delete some data instances (POST)
"""

import cStringIO

from numpy import ndarray

from flask import render_template, make_response, request, abort, jsonify
from flask.ext.login import login_required

from yamoda.server import app, db
from yamoda.server.database import Data, Entry


#### data

def _render_data_json(data):
    entry_uris = [url_for("entry", entry_id=e.id) for e in data.entries]
    return jsonify(id=data.id,
                   name=data.name,
                   context_uri=url_for("context", context_id=data.context.id),
                   entry_uris=entry_uris)


@app.route('/datas/<int:data_id>')
@login_required
@html_json_mimerender("data.html", _render_data_json)
def data(data_id):
    d = Data.query.get(data_id)
    if not d:
        raise NotFound()
    return dict(data=d)


@app.route('/datas/delete', methods=['POST'])
@login_required
def datadelete():
    try:
        ids = map(int, request.form.getlist('ids[]'))
        for data_id in ids:
            d = Data.query.get(data_id)
            # if d.writeable():  # XXX Data is not AccessControl'd
            db.session.delete(d)
        db.session.commit()
    except Exception, err:
        return jsonify(result='error', data=str(err))
    return jsonify(result='success', data=None)

