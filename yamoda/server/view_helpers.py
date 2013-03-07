#  -*- coding: utf-8 -*-
#
# yamoda, (c) 2012, see AUTHORS.  Licensed under the GNU GPL.
'''
Created on 08.09.2012
@author: dpausp (Tobias Stenzel)
'''
from __future__ import division, absolute_import
import logging
from yamoda.server.database.datamodel import Entry
from functools import wraps

logg = logging.getLogger("yamoda.view_helpers")


def get_entries(datas, params):
    """Get entries for params.
    Moved from views/set.py.
    FIXME: this is quick and dirty, and way too inefficient.  Must be
    rewritten using fewer queries.
    """
    entries = []
    for d in datas:
        entries.append([])
        for p in params:
            entry = Entry.query.filter_by(data=d, parameter=p).first()
            entries[-1].append(entry)

    return entries


def delete_cookies(*cookie_names, **cookie_names_with_path):
    """View decorator for deleting cookies after a request.
    :param cookie_names: Cookie names (keys) to delete. Default path / is used.
    :param cookie_names_with_path: Cookies with custom path, like: cookie="/path", ...
    """
    def _delete_cookies(func):

        @wraps(func)
        def decorated_func(*args, **kwargs):
            logg.info("args %s, kwargs %s", args, kwargs)
            response = func(*args, **kwargs)
#             assert isinstance(response, Response)
            for cookie_name in cookie_names:
                response.delete_cookie(cookie_name)
            for cookie_name, cookie_path in cookie_names_with_path.items():
                response.delete_cookie(cookie_name, cookie_path)
            logg.info("response is %s", response)
            return response
        return decorated_func
    logg.info("return %s", _delete_cookies)
    return _delete_cookies


