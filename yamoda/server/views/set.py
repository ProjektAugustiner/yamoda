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
from yamoda.server.database import Set, Context, Entry
from yamoda.importer import list_importers, load_importer


@app.route('/set/<int:id>')
@login_required
def set(id):
    s = Set.query.get_readable_or_404(id)
    # determine a context to use for displaying parameters
    params = None
    pvalues = None
    if s.datas:
        # FIXME: this is quick and dirty, and way too inefficient.  Must be
        # rewritten using fewer queries.
        ctx = s.datas[0].context
        params = [p for p in ctx.parameters if p.visible]
        pvalues = []
        for d in s.datas:
            pvalues.append([])
            for p in params:
                pvalue = Entry.query.filter_by(data=d, parameter=p).first()
                pvalues[-1].append(pvalue.value if pvalue else None)
    return render_template('set.html', set=s,
                           params=params, pvalues=pvalues)


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
        if not to_import:
            error = 'Nothing to import.'
        else:
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
        setlist = Set.query.all_readable()
    else:
        setlist = Set.query.filter_by(user=current_user).all_readable()
    return render_template('setlist.html', sets=setlist)
