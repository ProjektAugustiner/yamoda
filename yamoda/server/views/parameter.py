#  -*- coding: utf-8 -*-
#
# yamoda, (c) 2012, see AUTHORS.  Licensed under the GNU GPL.
"""Parameter view functions.

Functions (all GET):
----------
parameter: return infos for a given parameter (id)

Created on 23.10.2012
@author: dpausp (Tobias Stenzel)
"""
from __future__ import division, absolute_import

import logging as logg
from functools import partial
import json

from flask import render_template, make_response, request, abort, jsonify, url_for
from flask.ext.login import login_required

from yamoda.server import app
from yamoda.server.database import Parameter
from yamoda.server.mimerender import html_json_mimerender
from werkzeug.exceptions import NotFound


def _render_parameter_json(parameter):
    return json.dumps(dict(
                context_uri=url_for("context", context_id=parameter.context.id),
                unit=parameter.unit,
                name=parameter.name,
                description=parameter.description,
                id=parameter.id))


@app.route('/parameters/<int:parameter_id>')
@html_json_mimerender(html="parameter.html", json_func=_render_parameter_json)
@login_required
def parameter(parameter_id):
    parameter = Parameter.query.get(parameter_id)
    if parameter is None:
        raise NotFound()
    return dict(parameter=parameter)
