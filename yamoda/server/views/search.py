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
from yamoda.query import *


@app.route('/search', methods=["POST"])
@login_required
def do_search():
    logg.debug(request)
    query_string = request.form["query"]
    logg.debug("got query string %s", query_string)
    query_dict = parse_query_string(query_string)
    logg.debug("query dict %s", query_dict)
    result_type, query = convert_dict_query_to_sqla(query_dict)
    logg.debug("result type %s, query %s", result_type, query)

    if result_type == "sets":
        sets = query.all_readable()
        logg.info("query returned %s sets", len(sets))
        logg.debug("result sets %s", sets)
        return render_template('setlist.html', sets=sets)
    elif result_type == "datas":
        # XXX: no accesscontrol for datas
        datas = query.all()
        logg.info("query returned %s datas", len(datas))
        formatted_data = pprint.pformat([(d, d.entries) for d in datas])
        logg.info("result datas and entries \n%s", formatted_data)
        return "query returned {} datas".format(len(datas))
#        return render_template('searchresult_data.html', datas=datas)


@app.route('/search', methods=["GET"])
@login_required
def search():
    return render_template('search.html')


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
