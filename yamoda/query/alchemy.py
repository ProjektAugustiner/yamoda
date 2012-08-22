# -*- coding: utf-8 -*-
'''
yamoda.query.sqlalchemy.py
Created on 21.08.2012
@author: tobixx0
'''
from __future__ import division, absolute_import, print_function
import logging as logg
from sqlalchemy.sql import exists, and_, between
from .querylanguage import *
from yamoda.server.database import *


def convert_dict_query(query_dict):
    what_to_find = query_dict.get("find", "datas")
    
    if what_to_find == "datas":
        return _convert_dict_query_datas(query_dict)
    elif what_to_find == "sets":
        return _convert_dict_query_sets(query_dict)
    else:
        raise NotImplementedError()

def _make_entry_stmt(param_name, param_value):
    
    param_sq = db.session.query(Parameter.id).filter_by(name = param_name).subquery()
    entry_stmt = exists()
    # find out, if we have entries for a data which belong to the right parameter        
    entry_stmt = entry_stmt.where(and_(
                                       Entry.data_id == Data.id, 
                                       Entry.parameter_id == param_sq))
        
    if isinstance(param_value, Range):
        r = param_value
        # do values in the range `start` to `end` exist?
        entry_stmt = entry_stmt.where(Entry.value.between(r.start, r.end))
            
    elif isinstance(param_value, GreaterThan):
        gt = param_value
        entry_stmt = entry_stmt.where(Entry.value > gt.value)
            
    elif isinstance(param_value, LessThan):
        lt = param_value
        entry_stmt = entry_stmt.where(Entry.value < lt.value)
        
    else:
        raise Exception("invalid param_value for param {}: param_value {}".format(param_name, param_value))
        
    logg.debug("entry_stmt is %s", entry_stmt)
        
    return entry_stmt
        
def _convert_dict_query_datas(query_dict):
    query = Data.query
    
    # filter datas by context name
    context_name = query_dict.get("context_name")
    if context_name is not None:
        context_sq = db.session.query(Context.id).filter_by(name = context_name).subquery()
        query = query.filter_by(context_id = context_sq)
        
    # apply entry filters
    param_filters = query_dict.get("param_filters", {})
    for param_name, param_value in param_filters.iteritems():
        query = query.filter(_make_entry_stmt(param_name, param_value))
        
    limit = query_dict.get("limit")
    
    if limit is not None:
        query = query.limit(limit)
    
    return query
            
def _convert_dict_query_sets(query_dict):
    """ returns an sqlalchemy query 
        the query finds all sets which datas conform to the characterists given in query_dicts
    """
    query = Set.query
    
    # filter sets by users's name
    user_name = query_dict.get("user_name")
    if user_name is not None:
        user_sq = db.session.query(User.id).filter_by(name = user_name).subquery()
        query = query.filter_by(user_id = user_sq)
        
    # filter sets by creation date
    time_interval = query_dict.get("creation_date")
    if time_interval is not None:
        query = query.filter(Set.created.between(time_interval.start, time_interval.end))
        
    
    return query
    
        