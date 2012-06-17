#  -*- coding: utf-8 -*-
#
# yamoda, (c) 2012, see AUTHORS.  Licensed under the GNU GPL.

"""
Data set related views.
"""

import os
import json
import tempfile

from flask import render_template, make_response, request, flash
from flask.ext.login import login_required, current_user

from yamoda.server import app, db
from yamoda.server.database import Set, Context
from yamoda.importer import list_importers, load_importer
from yamoda.importer.base import MissingInfo


@app.route('/set/<int:id>')
@login_required
def set(id):
    s = Set.query.get_readable_or_404(id)
    return render_template('set.html', set=s)


@app.route('/set/<id>/import/do', methods=['POST'])
def setimport_do(id):
    userinfo = {}
    to_import = []
    try:
        s = Set.query.get(id)
        ctx = Context.query.get(request.form['context'])
        for fstorage in request.files.itervalues():
            name = fstorage.filename
            if not name:
                continue
            fd, fname = tempfile.mkstemp()
            fd = os.fdopen(fd, 'w')
            fstorage.save(fd, 1024*1024)
            fd.close()
            to_import.append(fname)
        for key in request.form:
            if not key.startswith('ui_par_'):
                continue
            pname = key[7:]
            d = userinfo[key[3:]] = {}
            d['brief'] = request.form['ui_brief_' + pname]
            d['description'] = request.form['ui_descr_' + pname]
            d['visible'] = bool(request.form.get('ui_vis_' + pname))
            d['unit'] = request.form['ui_unit_' + pname] or None
        if not to_import:
            raise ValueError('Nothing to import.')
        importer = load_importer(request.form['importer'])(ctx, s)
        try:
            imported = importer.import_items(to_import, userinfo)
            db.session.commit()
        except MissingInfo, err:
            db.session.rollback()
            missing = sorted(err.info)
            missing.append((
                [(k, v) for (k, v) in request.form.iteritems() if k.startswith('ui_')],
                'userinfo'))
            data = render_template('import_missing.html', missing=missing)
            res = 'missing'
        except Exception, err:
            db.session.rollback()
            raise
        else:
            res = 'success'
            data = ', '.join(d.name for d in imported)
    except Exception, err:
        res = 'error'
        data = str(err)
    resp = make_response(json.dumps({'result': res, 'data': data}))
    resp.headers['Content-Type'] = 'application/json'
    return resp


@app.route('/set/<id>/import')
@login_required
def setimport(id):
    s = Set.query.get_or_404(id)
    contexts = iter(Context.query)
    return render_template('setimport.html', set=s,
                           importers=list_importers(), contexts=contexts)


@app.route('/sets')
@app.route('/sets/<which>')
@login_required
def setlist(which='mine'):
    if which == 'all':
        setlist = Set.query.all_readable()
    else:
        setlist = Set.query.filter_by(user=current_user).all_readable()
    return render_template('setlist.html', sets=setlist)
