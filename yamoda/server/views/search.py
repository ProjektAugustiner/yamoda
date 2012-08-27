#  -*- coding: utf-8 -*-
#
# yamoda, (c) 2012, see AUTHORS.  Licensed under the GNU GPL.
'''
Created on 23.08.2012
@author: dpausp (Tobias Stenzel)
'''

import logging as logg
import pprint

from flask import render_template, request, abort
from flask.ext.login import login_required

from yamoda.server import app, db
from yamoda.query import convert_dict_query_to_sqla, parse_query_string, replace_newline_with_comma
from yamoda.server.database import HistoricQuery


@app.route('/search', methods=["POST"])
@login_required
def do_search():
    logg.debug(request)
    # query strings from the client can use newline as separator
    query_string = replace_newline_with_comma(request.form["query"])
    logg.debug("got query string %s", query_string)
    try:
        query_dict = parse_query_string(query_string)
    except:
        abort(400)
    logg.debug("query dict %s", query_dict)
    result_type, query = convert_dict_query_to_sqla(query_dict)
    logg.debug("result type %s, query %s", result_type, query)
    # save query for later use (search history)
    hist_query = HistoricQuery(query_string=query_string)
    db.session.add(hist_query)
    db.session.commit()

    if result_type == "sets":
        sets = query.all_readable()
        logg.info("query returned %s sets", len(sets))
        logg.debug("result sets %s", sets)
        return render_template('setresult.html', sets=sets, query=query_string)
    elif result_type == "datas":
        # XXX: no accesscontrol for datas
        datas = query.all()
        logg.info("query returned %s datas", len(datas))
        formatted_data = pprint.pformat([(d, d.entries) for d in datas])
        logg.info("result datas and entries \n%s", formatted_data)
        return render_template("dataresult.html", datas=datas, params=[], query=query_string)


@app.route('/deletequery/<id>', methods=["GET"])
@login_required
def delete_query(id):
    query = HistoricQuery.get(id)
    db.session.delete(query)
    return ""

@app.route('/search', methods=["GET"])
@login_required
def search():
    query_history = HistoricQuery.query.order_by(HistoricQuery.created).limit(50).all()
    return render_template('search.html', query_history=query_history)


@app.route('/searchtest')
@login_required
def searchtest():
    """ just run some test query"""
    import yamoda.query.test.testqueries as tq

    query_dict = parse_query_string(tq.teststr_sets)
    result_type, query = convert_dict_query_to_sqla(query_dict)
    result = query.all_readable()

    if result_type == "sets":
        return render_template('setlist.html', sets=result)
    else:
        abort(400)
