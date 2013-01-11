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
run_query    -- GET run query by id
get_query_history -- history update via AJAX
search   -- display search page
searchtest   -- test searching
'''

import logging as logg
import pprint
import time
import json

from flask import render_template, request, g
from flask.helpers import flash
from flask.ext.login import login_required, current_user
from parcon import ParseException

from yamoda.server import app, db, view_helpers
from yamoda.query.alchemy import convert_dict_query_to_sqla
from yamoda.query.parsing import parse_query_string, replace_newline_with_comma
from yamoda.server.database import HistoricQuery
from yamoda.query.serialization import to_json, from_json
from flask_login import AnonymousUser


# ## favorite queries displayed in layout.html

def _get_fav_queries():
    # get favorite queries
    return HistoricQuery.query.filter_by(favorite=True).all_readable()


@app.context_processor
def inject_fav_queries():
    # TODO: perhaps this isn't the best solution...
    # without that, python complains that AnonymousUser has no attribute "groups"...
    # this really looks like a problem with accesscontrol
    if current_user.is_anonymous():
        return dict(fav_queries=[])
    else:
        return dict(fav_queries=_get_fav_queries())


### helpers ###

def _save_query(query_string, query_dict, query_name):
    """Save query to DB for later use (search history)
    :return: Flash message and category for user response
    """
    logg.info("saving query '%s' to DB, name is %s", query_string, query_name)
    # don't save query if we have an identical query in the DB
    duplicate = HistoricQuery.query.filter_by(name=query_name).filter_by(query_string=query_string).all()
    logg.info("found duplicate in DB: %s", duplicate)
    if not duplicate:
        hist_query = HistoricQuery(query_string=query_string, query_json=to_json(query_dict),
                                   name=query_name, favorite=True if query_name else False,
                                   user=current_user, group=current_user.primary_group)
        db.session.add(hist_query)
        db.session.commit()
        return ("Query saved.", "info")
    else:
        return ("Query was not saved (duplicate).", "warn")


def _render_search_result(result_type, sqla_query, query_string):

    if result_type == "sets":
        sets = sqla_query.all_readable()
        logg.info("query returned %s sets", len(sets))
        logg.debug("result sets %s", sets)
        return render_template('settable.html', sets=sets)

    elif result_type == "datas":
        # XXX: no accesscontrol for datas
        datas = sqla_query.all()
        logg.info("query returned %s datas", len(datas))
        # determine common visible parameters for all rows which will be displayed on the result page
        all_param_sets = [{p for p in d.context.parameters if p.visible} for d in datas]
        if datas:
            common_param_set = set.intersection(*all_param_sets)
            entries = view_helpers.get_entries(datas, common_param_set)
            logg.info("intersected params %s", common_param_set)
        else:
            common_param_set = []
            entries = []
        formatted_data = pprint.pformat([(d, d.entries) for d in datas])
        logg.info("result datas and entries \n%s", formatted_data)
        return render_template("datatable.html", datas=datas, params=common_param_set, entries=entries)

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
        flash_msg, flash_cat = _save_query(query_string, query_dict, query_name)
        flash(flash_msg, flash_cat)

    return _render_search_result(result_type, query, query_string)


@app.route("/search/runquery/<int:query_id>", methods=["GET"])
def run_query(query_id):
    logg.info("run query with id: %s", query_id)
    hist_query = HistoricQuery.query.get_or_404(query_id)
    query_dict = from_json(hist_query.query_json)
    result_type, sqla_query = convert_dict_query_to_sqla(query_dict)
    return _render_search_result(result_type, sqla_query, hist_query.query_string)


@app.route('/search/toggle_favorite_queries', methods=["POST"])
@login_required
def toggle_favorite_queries():
    ids = request.form.getlist("ids[]")
    logg.info("ids to mark as favorite: %s", ids)
    for query_id in ids:
        hist_query = HistoricQuery.query.get(query_id)
        hist_query.favorite = False if hist_query.favorite else True
    db.session.commit()
    return ""


@app.route('/search/savequery', methods=["POST"])
@login_required
def save_query():
    # save query for later use (search history)
    query_name = request.form["name"]
    favorite = request.form["favorite"]
    query_string = replace_newline_with_comma(request.form["query"])
    logg.debug("got query string %s", query_string)
    try:
        _, query_dict = parse_query_string(query_string)
    except ParseException as p:
        flash_msg = "Error in Query (not saved): {}".format(p.message)
        flash_cat = "error"
    else:
        flash_msg, flash_cat = _save_query(query_string, query_dict, query_name, favorite)

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
        return render_template('settable.html', sets=result)
    else:
        return render_template('datatable.html', datas=result, params=[], pvalues=[], query=query_string)
