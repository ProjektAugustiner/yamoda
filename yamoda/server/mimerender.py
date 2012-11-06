#  -*- coding: utf-8 -*-
#
# yamoda, (c) 2012, see AUTHORS.  Licensed under the GNU GPL.
'''
Created on 23.10.2012
@author: dpausp (Tobias Stenzel)
'''
from __future__ import division, absolute_import
from functools import partial
import json
import logging
from flask import render_template, request, flash, redirect, url_for, jsonify, make_response, abort
from werkzeug.utils import escape
from mimerender import FlaskMimeRender
import mimerender as mr
from werkzeug.exceptions import NotFound, HTTPException, InternalServerError
from werkzeug.wrappers import BaseResponse
import functools


logg = logging.getLogger("yamoda.mimerender")


mr.register_mime("png", ("image/png",))
mr.register_mime("svg", ("image/svg+xml",))
mr.register_mime("pdf", ("application/pdf",))
mr.register_mime("eps", ("application/postscript",))


class FixedFlaskMimeRender(FlaskMimeRender):
    def _set_context_var(self, key, value):
        # logg.debug("set context var %s %s", key, value)
        request.environ[key] = value

    def _clear_context_var(self, key):
        # logg.debug("remove context var %s", key)
        del request.environ[key]

    def _make_response(self, content_or_response, headers, status):
        """Make a response object if neccessary.
        :param content_or_response: some content (str) or a Response object.
        Strings are wrapped with a Response objects.
        2-Tuples are splitted in content and status
        Response objects are returned unmodified
        """
        if isinstance(content_or_response, BaseResponse):
            logg.debug("is response object")
            response = content_or_response
            response.headers.extend(headers)
            logg.debug("response headers %s", response.headers)
            return response
        else:
            if isinstance(content_or_response, tuple) and len(content_or_response) == 2:
                content, status = content_or_response
                logg.debug("is tuple: content %s status %s", content, status)
            else:
                content = content_or_response
            return make_response(content, status, headers)


def callback406(accept_header, supported):
    return "text/plain", "supported Content Types: " + ", ".join(supported) + "\n"


mimerender = FixedFlaskMimeRender(global_not_acceptable_callback=callback406)


def render_json_exception(exception):
    data = {}
    if isinstance(exception, HTTPException):
        data["code"] = exception.code
        data["description"] = exception.description
    if hasattr(exception, "message"):
        data["message"] = exception.message
    return json.dumps(data)


def render_html_exception(exception):
    # HTTPExceptions are WSGI apps and can be called
    if isinstance(exception, HTTPException):
        return exception.get_response({})
    else:
        return InternalServerError().get_response({})


def render_txt_exception(exception):
    return exception.get_description({})


def render_png_exception(exception):
    return ""


def html_json_mimerender(html, json_func=jsonify):
    """
    Convenience wrapper for mimerender
    :param html: Callable or string. A string will be interpreted as a template name, a callable will be used for generating HTML.
    :param json_func: Callable which produces JSON output
    """
    if callable(html):
        html_func = html
    elif isinstance(html, str):
        html_func = partial(render_template, html)

    def wrap(target):
        functools.wraps(target)
        mapping = (
           (ValueError, '500 Internal Server Error'),
           (NotFound, '404 Not Found')
        )
        wrapped = mimerender(default="html", html=html_func, json=json_func)(target)
        wrapped2 = mimerender.map_exceptions(
                    mapping=mapping,
                    html=render_html_exception,
                    json=render_json_exception)(wrapped)
        return wrapped2

    return wrap


def mime_exceptions(fn):
    functools.wraps(fn)
    wrap = mimerender.map_exceptions(
        mapping=(
            (NotFound, 404),
        ),
        html=render_html_exception,
        json=render_json_exception,
        png=render_png_exception,
        txt=render_txt_exception,
    )
    return wrap(fn)
