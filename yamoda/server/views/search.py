#  -*- coding: utf-8 -*-
#
# yamoda, (c) 2012, see AUTHORS.  Licensed under the GNU GPL.
'''
Created on 23.08.2012
@author: dpausp (Tobias Stenzel)
'''

import logging as logg
import pprint

from flask import render_template, request
from flask.ext.login import login_required

from yamoda.server import app, db
from yamoda.query import convert_dict_query_to_sqla, parse_query_string, replace_newline_with_comma
from yamoda.server.database import HistoricQuery


@app.route('/search', methods=["POST"])
@login_required
def do_search():
    """Parse and execute query from client.
    Queries are saved if the user requests that.
    If successful, this view renders a data or set list with the results.
    Parse errors are sent to client in a special error template.
    """
    logg.debug("request was %s, form %s", request, request.form)
    # query strings from the client can use newline as separator
    query_string = replace_newline_with_comma(request.form["query"])
    logg.debug("got query string %s", query_string)
    try:
        query_dict = parse_query_string(query_string)
    except Exception as e:
        msg = e.message
        logg.error("error parsing query: %s", e)
        letters = " ".join("{}:{}".format(number, letter)
                           for number, letter in enumerate(query_string)
                           if not letter.isspace())
        return render_template("querylangerror.html", query=query_string.replace(",", ", "),
                                letters=letters, error_msg=msg)
    logg.debug("query dict %s", query_dict)
    result_type, query = convert_dict_query_to_sqla(query_dict)
    logg.debug("result type %s, query %s", result_type, query)
    if "save_query" in request.form:
        # save query for later use (search history)
        logg.info("saving query to DB")
        hist_query = HistoricQuery(query_string=query_string)
        db.session.add(hist_query)
        db.session.commit()

    if result_type == "sets":
        sets = query.all_readable()
        logg.info("query returned %s sets", len(sets))
        logg.debug("result sets %s", sets)
        return render_template('setresult.html', sets=sets,
                               query=query_string.replace(",", ", "))
    elif result_type == "datas":
        # XXX: no accesscontrol for datas
        datas = query.all()
        logg.info("query returned %s datas", len(datas))
        formatted_data = pprint.pformat([(d, d.entries) for d in datas])
        logg.info("result datas and entries \n%s", formatted_data)
        return render_template("dataresult.html", datas=datas, params=[],
                               query=query_string.replace(",", ", "))


@app.route('/search/deletequeries', methods=["POST"])
@login_required
def delete_queries():
    """Delete queries by id list (AJAX)
    """
    logg.info("delete queries")
    ids = request.form.getlist("ids[]")
    logg.info("ids to delete: %s", ids)
    for query_id in ids:
        hist_query = HistoricQuery.query.get(query_id)
        logg.debug("deleting history query %s", hist_query)
        db.session.delete(hist_query)
    db.session.commit()
    return ""


@app.route('/search', methods=["GET"])
@login_required
def search():
    """Display search page with AugQL help and search history
    """
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
        return render_template('setresult.html', sets=result)
    else:
        return render_template('dataresult.html', datas=result, params=[], query=tq.testquery_sets)
