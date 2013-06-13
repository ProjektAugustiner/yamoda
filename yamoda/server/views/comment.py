#  -*- coding: utf-8 -*-
#
# yamoda, (c) 2012, see AUTHORS.  Licensed under the GNU GPL.
"""
Comment section for different entities like set or data.
"""

import logging
import datetime
import json
from flask import url_for
from flask import render_template, make_response, request, abort, jsonify, Response, escape, Markup, redirect
from flask.ext.login import login_required, current_user
from yamoda.server.mimerender import html_json_mimerender, mimerender
from yamoda.server import app, db
from yamoda.server.database import Data, Entry, Set, User, SetComment
from yamoda.server.database.datamodel import DataComment

logg = logging.getLogger(__name__)


# ## set comments

def _post_set_comment_html(set_id):
    return redirect(url_for("set", set_id=set_id), 302)


def _post_set_comment_json(set_id):
    return make_response(json.dumps(dict(msg="comment created", set_id=set_id)), 200)


@app.route('/sets/<int:set_id>/new', methods=["POST"])
@html_json_mimerender(_post_set_comment_html, _post_set_comment_json)
@login_required
def post_set_comment(set_id):
    logg.info("post_set_comment %s", request.form)
    sett = Set.query.get_or_404(set_id)
    text = request.form.get("text", None)
    if text:
        comment = SetComment(author=current_user, text=text)
        sett.comments.append(comment)
        db.session.add(comment)
        db.session.commit()
    return dict(set_id=set_id)


# ## data comments

def _post_data_comment_html(data_id):
    return redirect(url_for("data", data_id=data_id), 302)


def _post_data_comment_json(data_id):
    return make_response(json.dumps(dict(msg="comment created", data_id=data_id)), 200)


@app.route('/datas/<int:data_id>/new', methods=["POST"])
@html_json_mimerender(_post_data_comment_html, _post_data_comment_json)
@login_required
def post_data_comment(data_id):
    logg.info("post_data_comment %s", request.form)
    data = Data.query.get_or_404(data_id)
    text = request.form.get("text", None)
    if text:
        comment = DataComment(author=current_user, text=text)
        data.comments.append(comment)
        db.session.add(comment)
        db.session.commit()
    return dict(data_id=data_id)
