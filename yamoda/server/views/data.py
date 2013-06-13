#  -*- coding: utf-8 -*-
#
# yamoda, (c) 2012, see AUTHORS.  Licensed under the GNU GPL.
"""
Data related views.

data: render a data instance (HTML or JSON)
datadelete: delete some data instances (POST)
"""

import logging
from functools import wraps
from urllib import unquote
from urlparse import urlsplit
from numpy import ndarray
from werkzeug.exceptions import NotFound
from flask import url_for
from flask import render_template, make_response, request, abort, jsonify, Response
from flask.ext.login import login_required
from yamoda.server.mimerender import html_json_mimerender
from yamoda.server import app, db
from yamoda.server.database import Data, Entry, Set

logg = logging.getLogger(__name__)

#### data


def _render_data_json(data):
    entry_uris = [url_for("entry", entry_id=e.id) for e in data.entries]
    return jsonify(id=data.id,
                   name=data.name,
                   context_uri=url_for("context", context_id=data.context.id),
                   entry_uris=entry_uris)


@app.route('/datas/<int:data_id>')
# @delete_cookies("data_order")
@login_required
@html_json_mimerender("data.html", _render_data_json)
def data(data_id):
    d = Data.query.get(data_id)
    if not d:
        raise NotFound()
    previous_data = None
    next_data = None
    from_set = None
    # determine where we are coming from
    logg.info("data, referrer is %s", request.referrer)
    path_parts = urlsplit(request.referrer).path.split("/") if request.referrer else None
    # TODO better way to determine if we are coming from the set view?!
    set_path_part = url_for("set", set_id="1").split("/")[1]
    date_path_part = url_for("data", data_id="1").split("/")[1]
    if path_parts and path_parts[1] in (set_path_part, date_path_part):
        # we came from a set
        from_set_id = request.cookies.get("from_set", None, int)
        from_set = Set.query.get(from_set_id) if from_set_id else None
        # get data order given by client side
        data_ids = [int(id_str) for id_str in unquote(request.cookies.get("data_order", "")).split(",")]
        # current position of shown data in data order
        logg.debug("data order %s", data_ids)
        cur_pos = data_ids.index(data_id)
        if cur_pos > 0:
            previous_data = Data.query.get(data_ids[cur_pos - 1])
        else:
            previous_data = None
        if cur_pos < len(data_ids) - 1:
            next_data = Data.query.get(data_ids[cur_pos + 1])
        else:
            next_data = None
    return dict(data=d, previous_data=previous_data, next_data=next_data, from_set=from_set)


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

