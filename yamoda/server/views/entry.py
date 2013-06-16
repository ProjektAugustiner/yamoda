#  -*- coding: utf-8 -*-
#
# yamoda, (c) 2012, see AUTHORS.  Licensed under the GNU GPL.
"""Entry view functions.
Return entries in various shapes and formats

Functions (all GET):
----------
entry: get an entry in various formats (see function decorator)
entry_1D_1D: convenience view for two 1D entries, for example for x-y plotting

Created on 19.09.2012
@author: dpausp (Tobias Stenzel)
"""
from __future__ import division, absolute_import
import itertools as it
from functools import partial
import logging as logg
import os

import numpy as np
import matplotlib.pyplot as plt

from flask import render_template, make_response, request, abort, jsonify, url_for
from flask.ext.login import login_required

from yamoda.server import app, db
from yamoda.server.database import Data, Entry, Context, Parameter
from yamoda.server.mimerender import html_json_mimerender, mimerender, mime_exceptions
from werkzeug.exceptions import NotFound, UnsupportedMediaType, BadRequest
from flask import send_from_directory
import cStringIO

GEN_IMAGE_DIR = app.config["GENERATED_DIR"]


# ## entry view helpers

def _save_entry_image_if_needed(img_type, entry):
    value = entry.value
    if isinstance(value, np.ndarray):
        filename = "entry_{}.{}".format(entry.id, img_type)
        filepath = os.path.join(GEN_IMAGE_DIR, filename)
        if not os.path.isfile(filepath):
            label = "{} ({})".format(entry.parameter.name, entry.parameter.unit)
            if len(value.shape) == 1:
                save_func = _save_image_1D
            elif len(value.shape) == 2:
                save_func = _save_image_2D
            else:
                return
            save_func(img_type, value, label, filepath)
    return filename


def _render_entry_json(entry):
    logg.debug("_render_entry_json")
    value = entry.value
    # special handling if client wants a image uri
    img_type = request.args.get("img_url_for_type")
    if img_type is not None:
        if isinstance(value, np.ndarray) and len(value.shape) <= 2:
            filename = _save_entry_image_if_needed(img_type.lower(), entry)
            return jsonify(img_url=url_for("generated", filename=filename), image_type=img_type)
        else:
            return "", 406
    else:
        if isinstance(value, np.ndarray):
            # convert ndarrays to a (nested) list for JSON serializer
            value = value.tolist()

        # make json content
        parameter_uri = url_for("parameter", parameter_id=entry.parameter.id)
        parameter_name = entry.parameter.name
        return jsonify(id=entry.id,
                       value=value,
                       parameter_uri=parameter_uri,
                       parameter_name=parameter_name)


def _render_entry_html(entry):
    value = entry.value
    if isinstance(value, np.ndarray):
        if len(value.shape) < 3:
            return render_template("entrydisplay.html", entry=entry)
    return "", 406


def _render_entry_plain(entry):
    return str(entry.value)


def _save_image_1D(img_type, value, label, filepath):
    logg.debug("saving 1D image of type %s to file %s", img_type, filepath)
    fig = plt.figure()
    ax = fig.gca()
    ax.plot(value)
    ax.set_title(label)
    ax.grid(1)
    fig.savefig(filepath, format=img_type, bbox_inches='tight', transparent=True)


def _save_image_2D(img_type, value, label, filepath):
    logg.debug("saving 2D image of type %s to file %s", img_type, filepath)
    fig = plt.figure()
    ax = fig.gca()
    ax_image = ax.imshow(value)
    ax.set_title(label)
    fig.colorbar(ax_image)
    ax.grid(1)
    fig.savefig(filepath, format=img_type, bbox_inches='tight', transparent=True)


def _render_entry_image(img_type, entry):
    logg.debug("_render_entry_image")
    filename = _save_entry_image_if_needed(img_type, entry)
    if not filename:
        return "", 406
    return send_from_directory(GEN_IMAGE_DIR, filename, as_attachment=True)


@app.route('/entries/<int:entry_id>')
@app.route('/entries')
@login_required
@mime_exceptions
@mimerender(
    html=_render_entry_html,
    json=_render_entry_json,
    png=partial(_render_entry_image, "png"),
    svg=partial(_render_entry_image, "svg"),
    eps=partial(_render_entry_image, "eps"),
    pdf=partial(_render_entry_image, "pdf"),
    txt=_render_entry_plain
)
def entry(entry_id=None):
    if entry_id:
        entry = Entry.query.get(entry_id)
    else:
        parameter_id = request.args.get("parameter_id")
        data_id = request.args.get("data_id")
        parameter_name = request.args.get("parameter_name")

        if parameter_id and data_id:
            logg.debug("looking for an entry with parameter id %s for data id %s", parameter_id, data_id)
            entry = Entry.query.filter_by(parameter_id=parameter_id, data_id=data_id).first()
        elif parameter_name and data_id:
            logg.debug("looking for an entry with parameter name %s for data id %s", parameter_name, data_id)
            # TODO: optimize
            data = Data.query.get(data_id)
            if not data:
                raise NotFound()
            parameter_sq = Parameter.query.filter_by(context=data.context, name=parameter_name).subquery()
            entry = Entry.query.filter_by(data_id=data_id).filter_by(parameter_id=parameter_sq.c.id).first()
        else:
            raise BadRequest()

    if entry is None:
        raise NotFound()
    return dict(entry=entry)


# ## entry_1D_1D view helpers

def _save_image_1D_1D(filepath, img_type, values_x, values_y, label_x, label_y):
    fig = plt.figure()
    ax = fig.gca()
    ax.plot(values_x, values_y)
    ax.grid(1)
    ax.set_xlabel(label_x)
    ax.set_ylabel(label_y)
    fig.savefig(filepath, format=img_type, bbox_inches='tight', transparent=True)


def _render_entry1D_1D_image(img_type, id_x, id_y, **kw):
    filename = "entry_{}x{}.{}".format(id_x, id_y, img_type)
    filepath = os.path.join(GEN_IMAGE_DIR, filename)
    if not os.path.isfile(filepath):
        logg.debug("saving plot for entry %s against %s to file %s as %s", id_x, id_y, filepath, img_type.upper())
        _save_image_1D_1D(filepath, img_type, **kw)
    return send_from_directory(GEN_IMAGE_DIR, filename, as_attachment=True)


def _render_entry1D_1D_json(values_x, values_y, **kw):
    return jsonify(values_x=list(values_x), values_y=list(values_y), **kw)


@app.route('/entries/<int:xid>/<int:yid>')
@login_required
@mime_exceptions
@mimerender(
    json=_render_entry1D_1D_json,
    png=partial(_render_entry1D_1D_image, "png"),
    svg=partial(_render_entry1D_1D_image, "svg"),
    eps=partial(_render_entry1D_1D_image, "eps"),
    pdf=partial(_render_entry1D_1D_image, "pdf")
)
def entry_1D_1D(xid, yid):
    ex = Entry.query.get(xid)
    ey = Entry.query.get(yid)
    if not (ex and ey):
        raise NotFound()
    elif not isinstance(ex.value, np.ndarray) or not isinstance(ey.value, np.ndarray) \
       or len(ex.value) != len(ey.value) or len(ex.value.shape) > 1 or len(ey.value.shape) > 1:
        abort(406)
    label_x = "{} ({})".format(ex.parameter.name, ex.parameter.unit)
    label_y = "{} ({})".format(ey.parameter.name, ey.parameter.unit)
    return dict(values_x=ex.value, values_y=ey.value, label_x=label_x, label_y=label_y, id_x=ex.id, id_y=ey.id)
