#coding: utf8
from sqlalchemy.orm import aliased
from sqlalchemy.sql import exists
from yamoda.server import app, db
from yamoda.server.database import *

def usecase1(author, start_datetime, end_datetime):
    """suche alle sets von author:Tim_Adams, zeitraum:datum1-datum2"""
    return Set.query.filter(User.name == author).filter(Set.created > start_datetime).filter(Set.created < end_datetime).all()

def usecase2(author, probe):
    """suche alles author:Tim, probe:ofz66-3 (kann sowohl sets als auch datas listen, sets aber nur, wenn alle darin enthaltenen datas kriterien erfüllen)"""

def usecase3(param_name, start_value, end_value):
    """alle datas mit T<30K"""
    return Data.query.join(Entry).join(Parameter).filter(Parameter.name == param_name).filter(Entry.value_float > start_value).filter(Entry.value_float < end_value)

def usecase4(context_name=None, **params_start_end_values):
    """alle datas mit vsm.T2 im Interfall 20K-40K und B=3T"""
    query = Data.query
    if context_name is not None:
        context_sq = db.session.query(Context.id).filter_by(name = context_name).subquery()
        query = Data.query.filter_by(context_id = context_sq)

    for param_name, (start_value, end_value) in params_start_end_values.iteritems():
        param_sq = db.session.query(Parameter.id).filter_by(name = param_name).subquery()
        e_alias = aliased(Entry)
        query = query.join(e_alias, Data.entries).filter(e_alias.parameter_id == param_sq) 
        query = query.filter(e_alias.value_float > start_value).filter(e_alias.value_float < end_value)

    return query

def a_usecase4(context_name=None, **params_start_end_values):
    """alle datas mit vsm.T2 im Interfall 20K-40K und B=3T"""
    query = Data.query
    if context_name is not None:
        context_sq = db.session.query(Context.id).filter_by(name = context_name).subquery()
        query = Data.query.filter_by(context_id = context_sq)

    for param_name, (start_value, end_value) in params_start_end_values.iteritems():
        param_sq = db.session.query(Parameter.id).filter_by(name = param_name).subquery()
        # find out, if we have entries for a data which belong to the right parameter and have a value in the range start_value to end_value
        entry_for_data_and_param_stmt = and_(
            Entry.data_id == Data.id, 
            Entry.parameter_id == param_sq)

        entry_value_in_range_stmt = and_(
            Entry.value_float > start_value,
            Entry.value_float < end_value)

        entry_stmt = exists().where(and_(entry_for_data_and_param_stmt, entry_value_in_range_stmt))
        query = query.filter(entry_stmt)

    return query

