#  -*- coding: utf-8 -*-
#
# yamoda, (c) 2012, see AUTHORS.  Licensed under the GNU GPL.
"""
Testing a comment section based on datatables
"""

import logging
from functools import wraps
from urllib import unquote
from urlparse import urlsplit
from numpy import ndarray
from werkzeug.exceptions import NotFound
from flask import url_for
from flask import render_template, make_response, request, abort, jsonify, Response, escape, Markup
from flask.ext.login import login_required, current_user
from yamoda.server.mimerender import html_json_mimerender
from yamoda.server import app, db
from yamoda.server.database import Data, Entry, Set, User, Comment
import datetime

logg = logging.getLogger(__name__)

#### data


@app.route('/commenttest', methods=["GET", "POST"])
@login_required
def commenttest():
    if request.method == "POST":
        raw_text = request.form.get("text")
        logg.info("raw %s", raw_text)
        text = unicode(escape(raw_text)).replace("\n", "<br>")
        comment = Comment(author=current_user, text=text)
        db.session.add(comment)
        logg.info("added new comment %s from user %s with text %s", comment, comment.author, comment.text)
        db.session.commit()
    # test comments
    user = User.query.all()[-1]
    comment0 = Comment(text="Ein Kommentar halt. Kein weiterer Text.", author=current_user, created=datetime.datetime.now())
    comment1 = Comment(text="Noch ein Kommentar, tro" + ("lo" * 40 + "\n") * 10, author=user, created=datetime.datetime.now())
    db_comments = Comment.query.all()
    return render_template("commenttest.html", comments=[comment0, comment1] + db_comments)

