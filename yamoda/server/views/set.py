#  -*- coding: utf-8 -*-
#
# yamoda, (c) 2012, see AUTHORS.  Licensed under the GNU GPL.

"""
Data set related views.
"""

import os
import tempfile

from flask import render_template, request, flash
from flask.ext.login import login_required, current_user

from yamoda.server import app, db
from yamoda.server.database import Set, Context
from yamoda.importer import list_importers, load_importer


@app.route('/set/<id>')
@login_required
def set(id):
    s = Set.query.get_or_404(id)
    return render_template('set.html', set=s)


@app.route('/set/<id>/import', methods=['GET', 'POST'])
@login_required
def setimport(id):
    error = None
    s = Set.query.get_or_404(id)
    if request.method == 'POST':
        to_import = []
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
        importer = load_importer(request.form['importer'])(ctx, s)
        try:
            importer.import_items(*to_import)
            db.session.commit()
        except Exception, err:
            db.session.rollback()
            error = str(err)
        else:
            flash('Import successful')
    contexts = iter(Context.query)
    return render_template('setimport.html', set=s, error=error,
                           importers=list_importers(), contexts=contexts)


@app.route('/sets')
@app.route('/sets/<which>')
@login_required
def setlist(which='mine'):
    if which == 'all':
        setlist = Set.query.all()
    else:
        setlist = Set.query.filter_by(user=current_user)
    for s in setlist:
        print s.readable()
    return render_template('setlist.html', sets=setlist)
