#  -*- coding: utf-8 -*-
#
# yamoda, (c) 2012, see AUTHORS.  Licensed under the GNU GPL.
'''
Created on 08.09.2012
@author: dpausp (Tobias Stenzel)
'''
from __future__ import division, absolute_import
import logging
from yamoda.server.database.datamodel import Entry, Parameter
from yamoda.server import db
from functools import wraps

logg = logging.getLogger("yamoda.view_helpers")


def get_entries_slow(datas, params):
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


def get_all_entries(datas, params):
    """Get entries for given params.
    :param datas: Datas to get entries for.
    :param params: Params to get entries for.
    :return: a list of entries, sorted first by Data.id, then Parameter.id 
    """
    if not (datas and params):
        return []
    data_ids = [d.id for d in datas]
    param_ids = [p.id for p in params]
    query = Entry.query.filter(Entry.data_id.in_(data_ids)).filter(Entry.parameter_id.in_(param_ids))\
        .order_by("data_id").order_by("parameter_id")
    return query.all()


def get_all_entry_values(datas, params):
    """Get entry values for given params.
    :param datas: Datas to get entries for.
    :param params: Params to get entries for.
    :return: a list of entry values, sorted first by Data.id, then Parameter.id
    """
    data_ids = [d.id for d in datas]
    param_ids = [p.id for p in params]
    query = db.session.query(Entry.value).filter(Entry.data_id.in_(data_ids)).filter(Entry.parameter_id.in_(param_ids))\
        .order_by("data_id").order_by("parameter_id")
    return [v[0] for v in query.all()]


def get_entries(datas, params):
    """Get entries for given params.
    :param datas: Datas to get entries for.
    :param params: Params to get entries for.
    :return: a list for each data with entries for the given params.
    """
    num_params = len(params)
    num_all_entries = len(datas) * num_params
    all_entries = get_all_entries(datas, params)
    entries = []
    pos = num_params
    while pos <= num_all_entries:
        entries.append(all_entries[pos - num_params:pos])
        pos += num_params
    return entries


def get_entry_values_dict(datas, params):
    """Like get_entries, but return dicts instead with the param name as the key and the entry value as value
    """
    num_params = len(params)
    param_names = [p.name for p in params]
    num_all_entries = len(datas) * num_params
    all_entry_values = get_all_entry_values(datas, params)
    entry_values = []
    pos = num_params
    while pos <= num_all_entries:
        entry_values_for_data = all_entry_values[pos - num_params:pos]
        entry_values.append({n: e for n, e in zip(param_names, entry_values_for_data)})
        pos += num_params
    return entry_values


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


