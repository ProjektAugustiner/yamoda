#  -*- coding: utf-8 -*-
#
# yamoda, (c) 2012, see AUTHORS.  Licensed under the GNU GPL.
from __future__ import absolute_import

import logging
import json
from flask import Flask, request, flash, redirect, current_app, jsonify, make_response
from flask.ext.login import LoginManager, user_unauthorized, login_url

from yamoda.server.mimerender import mimerender


logg = logging.getLogger(__name__)


class MimeLoginManager(LoginManager):
    @mimerender(
        html=lambda login_uri: redirect(login_uri),
        json=lambda login_uri: make_response(json.dumps(dict(login_uri=login_uri, msg="not logged in")), 401)
        )
    def unauthorized(self):
        """This is called when the user is required to log in.
        adapted from LoginManager.unauthorized
        """
        logg.debug("called unauthorized")
        user_unauthorized.send(current_app)
        if self.login_message:
            flash(self.login_message)
        return dict(login_uri=login_url(self.login_view, request.url))
