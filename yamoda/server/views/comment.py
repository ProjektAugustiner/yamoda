#  -*- coding: utf-8 -*-
#
# yamoda, (c) 2012, see AUTHORS.  Licensed under the GNU GPL.
"""
Comment section for different entities like set or data.
"""

import logging
from functools import wraps
from urllib import unquote
from urlparse import urlsplit
from numpy import ndarray
from werkzeug.exceptions import NotFound
from flask.helpers import url_for
from flask import render_template, make_response, request, abort, jsonify, Response, escape, Markup
from flask.ext.login import login_required, current_user
from yamoda.server.mimerender import html_json_mimerender
from yamoda.server import app, db
from yamoda.server.database import Data, Entry, Set, User, Comment
import datetime

logg = logging.getLogger(__name__)


def _render_comments_json(comments, commented_entity):
    return jsonify(commented_entity=commented_entity.id,
                   name=data.name,
                   context_uri=url_for("context", context_id=data.context.id),
                   entry_uris=entry_uris)


@app.route('/<commented_type>/comments/<int:commented_id>', methods=["GET"])
@html_json_mimerender("comments.html", _render_comments_json)
@login_required
def comments():
    db_comments = Comment.query.
    return render_template("commenttest.html", comments=[comment0, comment1] + db_comments)

