#  -*- coding: utf-8 -*-
#
# yamoda, (c) 2012, see AUTHORS.  Licensed under the GNU GPL.
from yamoda.server.mimerender import html_json_mimerender
import json
from werkzeug.exceptions import NotFound
from flask.helpers import jsonify

"""
Functions:
----------
contexts: get context list as HTML or JSON
context: get context as HTML or JSON
create_context: new context (POST)
"""
import logging
from flask import render_template, request, flash, redirect, url_for
from flask.ext.login import login_user, login_required, logout_user
from sqlalchemy.exc import IntegrityError

from yamoda.server import app, db
from yamoda.server.database import Context, User, Group, Set


logg = logging.getLogger("yamoda.views.context")


#### contexts

def _render_contextlist_json(contextlist):
    context_uris = [url_for("context", context_id=c.id) for c in contextlist]
    return jsonify(context_uris=context_uris)


@app.route('/contexts', methods=['GET'])
@login_required
@html_json_mimerender("contextlist.html", _render_contextlist_json)
def contexts():
    """Retrieve a listing of all contexts"""
    contextlist = Context.query.all()
    return dict(contextlist=contextlist)


#### context

def _render_context_json(context):
    parameter_uris = [url_for("parameter", parameter_id=p.id) for p in context.parameters]
    return json.dumps(dict(
                id=context.id,
                type=context.type,
                name=context.name,
                description=context.description,
                parameter_uris=parameter_uris,
                brief=context.brief))


@app.route('/contexts/<context_name>')
@app.route('/contexts/<int:context_id>')
@login_required
@html_json_mimerender("context.html", _render_context_json)
def context(context_name=None, context_id=None):
    logg.debug("getting context: context_name %s context_id %s", context_name, context_id)
    """displays the requested context"""
    if context_name:
        context = Context.query.filter_by(name=context_name).first()
    elif context_id:
        context = Context.query.get(context_id)
    if context is None:
        raise NotFound()
    return dict(context=context)


#### contextcreate

@app.route('/contexts/create', methods=['POST'])
@login_required
def create_context():
    """Creates a new context from a POST request"""
    name = request.form['context_name']
    brief = request.form['context_brief']
    description = request.form['context_description']
    try:
        if not name or not brief:
            raise ValueError
        new_context = Context(name=name, brief=brief, description=description)
        db.session.add(new_context)
        db.session.commit()
    except (ValueError, IntegrityError):
        db.session.rollback()
        flash('Invalid Input', 'error')
    else:
        flash('Created new context: {0}'.format(name), 'info')
