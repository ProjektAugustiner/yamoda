#  -*- coding: utf-8 -*-
#
# yamoda, (c) 2012, see AUTHORS.  Licensed under the GNU GPL.
'''
Created on 23.08.2012
@author: dpausp (Tobias Stenzel)

Functions:
----------
do_search    -- POST queries and display results
delete_queries    -- POST delete queries from history
save_query    -- POST query for saving
get_query_history -- history update via AJAX
search   -- display search page
searchtest   -- test searching
'''

import logging as logg
import pprint
import time

from flask import render_template, request
from flask.helpers import flash
from flask.ext.login import login_required
from parcon import ParseException

from yamoda.server import app, db, view_helpers
from yamoda.query.alchemy import convert_dict_query_to_sqla
from yamoda.query.parsing import parse_query_string, replace_newline_with_comma
from yamoda.server.database import HistoricQuery

### helpers ###


def _save_query(query_string, query_name):
    """Save query to DB for later use (search history)
    :return: Flash message and category for user response
    """
    logg.info("saving query '%s' to DB, name is %s", query_string, query_name)
    # don't save query if we have an identical query in the DB
    duplicate = HistoricQuery.query.filter_by(name=query_name).filter_by(query_string=query_string).all()
    logg.info("found duplicate in DB: %s", duplicate)
    if not duplicate:
        hist_query = HistoricQuery(query_string=query_string, name=query_name)
        db.session.add(hist_query)
        db.session.commit()
        return ("Query saved.", "info")
    else:
        return ("Query was not saved (duplicate).", "warn")

### view functions ###


@app.route('/search', methods=["POST"])
@login_required
def do_search():
#    time.sleep(0.8)
    """Parse and execute query from client.
    Queries are saved if the user requests that.
    If successful, this view renders a data or set list with the results.
    Parse errors are sent to client in a special error template.
    """
    logg.debug("request was %s, form %s, form keys %s", request, request.form, request.form.keys())
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
        query_name = request.form["name"]
        flash_msg, flash_cat = _save_query(query_string, query_name)
        flash(flash_msg, flash_cat)

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
        # determine common visible parameters for all rows which will be displayed on the result page
        all_param_sets = [{p for p in d.context.parameters if p.visible} for d in datas]
        if datas:
            common_param_set = set.intersection(*all_param_sets)
            pvalues = view_helpers.get_pvalues(datas, common_param_set)
            logg.info("intersected params %s", common_param_set)
        else:
            common_param_set = []
            pvalues = []
        formatted_data = pprint.pformat([(d, d.entries) for d in datas])
        logg.info("result datas and entries \n%s", formatted_data)
        return render_template("dataresult.html", datas=datas, params=common_param_set, pvalues=pvalues,
                               query=query_string.replace(",", ", "))


@app.route('/search/savequery', methods=["POST"])
@login_required
def save_query():
    # save query for later use (search history)
    query_name = request.form["name"]
    query_string = replace_newline_with_comma(request.form["query"])
    logg.debug("got query string %s", query_string)
    try:
        parse_query_string(query_string)
    except ParseException as p:
        flash_msg = "Error in Query (not saved): {}".format(p.message)
        flash_cat = "error"
    else:
        flash_msg, flash_cat = _save_query(query_string, query_name)

    logg.debug(flash_msg)
    flash(flash_msg, flash_cat)
    return render_template("flash_msg.html")


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
    query_history = HistoricQuery.query.order_by(HistoricQuery.created).limit(100).all()
    return render_template('search.html', query_history=query_history)


@app.route('/search/queryhistory', methods=["GET"])
@login_required
def get_query_history():
    """Function to update query history via AJAX
    """
    query_history = HistoricQuery.query.order_by(HistoricQuery.created).limit(100).all()
    return render_template('queryhistory.html', query_history=query_history)


@app.route('/searchtest')
@login_required
def searchtest():
    """ just run some test query"""
    import yamoda.query.test.testqueries as tq

    query_string = tq.testquery_sets.string
    query_dict = parse_query_string(query_string)
    result_type, query = convert_dict_query_to_sqla(query_dict)
    result = query.all_readable()

    if result_type == "sets":
        return render_template('setresult.html', sets=result)
    else:
        return render_template('dataresult.html', datas=result, params=[], pvalues=[], query=query_string)
