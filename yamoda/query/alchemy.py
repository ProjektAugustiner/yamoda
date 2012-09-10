#  -*- coding: utf-8 -*-
#
# yamoda, (c) 2012, see AUTHORS.  Licensed under the GNU GPL.

'''
Created on 19.08.2012
@author: dpausp (Tobias Stenzel)

Conversion of queries (in intermediate representation) to SQLAlchemy.
'''
from __future__ import division, absolute_import
import logging as logg
from sqlalchemy.sql import and_, or_
from sqlalchemy.orm import aliased
from .representation import Interval, LessThan, GreaterThan
from yamoda.server.database import Set, Entry, Parameter, Data, Context, User, db


def convert_dict_query_to_sqla(query_dict):
    """Convert AugQL query representation to an SQLAlchemy query.
    This method selects the right conversion method according to the find attribute.
    Supports querying for `datas` (default) and `sets` at the moment.
    Returns what is queried for as first value
    :param query_dict: dict representation of an AugQL query
    :returns (what_to_find, query)

    """
    what_to_find = query_dict.get("find", "sets")

    if what_to_find == "datas":
        return ("datas", _convert_dict_query_datas(query_dict))
    elif what_to_find == "sets":
        return ("sets", _convert_dict_query_sets(query_dict))
    else:
        raise NotImplementedError(str(what_to_find) + " queries are not supported!")


def _make_entry_query(context_sq, param_name, param_exprs):
    """unused atm"""

    entry_query = db.session.query(Parameter.name, Entry.value)
    # find out, if we have entries for a data which belong to the right parameter
    entry_query = entry_query.filter(and_(Entry.data_id == Data.id,
                                          Entry.parameter_id == Parameter.id))
    if context_sq is not None:
        entry_query = entry_query.filter(Parameter.context_id == context_sq)

    if isinstance(param_exprs, Interval):
        r = param_exprs
        # do values in the range `start` to `end` exist?
        entry_query = entry_query.filter(Entry.value.between(r.start, r.end))

    elif isinstance(param_exprs, GreaterThan):
        gt = param_exprs
        entry_query = entry_query.filter(Entry.value > gt.value)

    elif isinstance(param_exprs, LessThan):
        lt = param_exprs
        entry_query = entry_query.filter(Entry.value < lt.value)

    else:
        raise Exception("invalid param_exprs for param {}: param_exprs {}".format(param_name, param_exprs))

    logg.debug("entry_query is %s", entry_query)

    return entry_query


def _make_entry_cond(param_name, param_exprs):
    """Create condition for entries for the _convert_dict_query_datas method.
    Only entries which belong to a certain Data and Parameter will be selected.
    Supports restricting selected entries by value (>, < or interval)
    """

    # find out, if we have entries for a data which belong to the right parameter
    cond = and_(Parameter.context_id == Data.context_id,
                Parameter.name == param_name,
                Entry.data_id == Data.id,
                Entry.parameter_id == Parameter.id)

    # multiple exprs are joined by OR
    or_cond = or_()

    for expr in param_exprs:
        if isinstance(expr, Interval):
            # do values in the range `start` to `end` exist?
            or_cond = or_(or_cond, Entry.value.between(expr.start, expr.end))

        elif isinstance(expr, GreaterThan):
            or_cond = or_(or_cond, Entry.value > expr.value)

        elif isinstance(expr, LessThan):
            or_cond = or_(or_cond, Entry.value < expr.value)

        else:
            raise Exception("invalid param_exprs for param {}: param_exprs {}".format(param_name, param_exprs))

    cond = and_(cond, or_cond)

    logg.debug("entry_cond is %s", cond)

    return cond


def _convert_dict_query_datas(query_dict):
    """ Convert a data query to SQLAlchemy.
    Supports:
    * selecting datas for a given context name
    * selecting Datas for which every entity satisfies some condition
    * sorting by values of parameters
    * applying a result limit
    """
    query = Data.query

    # filter datas by context name
    context_name = query_dict.get("context_name")
    if context_name is not None:
        context_sq = db.session.query(Context.id).filter_by(name=context_name).subquery()
        query = query.filter_by(context_id=context_sq)
    else:
        context_sq = None

    # apply entry filters
    # TODO: test performance of any() and remove it if neccessary
    param_filters = query_dict.get("param_filters", {})
    for param_name, param_exprs in param_filters.iteritems():
        entry_cond = _make_entry_cond(param_name, param_exprs)
        query = query.filter(Data.entries.any(entry_cond))

    # apply sorting
    sort = query_dict.get("sort", [])
    for sort_param in sort:
        e_alias = aliased(Entry)
        p_alias = aliased(Parameter)
        query = query.join(e_alias, Data.entries).join(p_alias).filter(and_(p_alias.name == sort_param.param_name,
                                                                            p_alias.context_id == Data.context_id))
        sort_col = e_alias.value_float if sort_param.sort_direction == "asc" else e_alias.value_float.desc()
        query = query.order_by(sort_col)

    # limit number of results
    limit = query_dict.get("limit")
    if limit is not None:
        query = query.limit(limit)

    return query


def _convert_dict_query_sets(query_dict):
    """Returns an sqlalchemy query.
       the query finds all sets which datas conform to the characterists given in query_dicts
    """
    query = Set.query

    # filter sets by username
    user_name = query_dict.get("user_name")
    if user_name is not None:
        user_sq = db.session.query(User.id).filter_by(name=user_name).subquery()
        query = query.filter_by(user_id=user_sq)

    # filter sets by creation date
    time_interval = query_dict.get("created")
    if time_interval is not None:
        query = query.filter(Set.created.between(time_interval.start, time_interval.end))

    # limit number of results
    limit = query_dict.get("limit")
    if limit is not None:
        query = query.limit(limit)

    return query
