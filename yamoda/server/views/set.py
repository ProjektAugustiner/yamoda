#  -*- coding: utf-8 -*-
#
# yamoda, (c) 2012, see AUTHORS.  Licensed under the GNU GPL.
from yamoda.server.database.datamodel import Data

"""
Data set related views.
set: render a data set (HTML or JSON)
sets: show a list of all sets 
"""

import logging
import os
import tempfile

from flask import render_template, request, flash, redirect, url_for, jsonify
from flask.ext.login import login_required, current_user
from werkzeug.exceptions import NotFound

from yamoda.server import app, db, view_helpers
from yamoda.server.database import Set, Context
from yamoda.importer import list_importers, load_importer
from yamoda.importer.base import MissingInfo, ImporterError
from yamoda.server.mimerender import html_json_mimerender


logg = logging.getLogger(__name__)

#### set


def _render_set_json(sett, **kw):
    data_uris = [url_for("data", data_id=d.id) for d in set.datas]
    child_uris = [url_for("set", set_id=c.id) for c in set.children]
    return jsonify(id=set.id,
            name=sett.name,
            data_uris=data_uris,
            child_uris=child_uris)


@app.route('/sets/<int:set_id>')
@login_required
@html_json_mimerender("set.html", _render_set_json)
def set(set_id):
    s = Set.query.get_readable(set_id)
    if not s:
        raise NotFound()
    # determine a context to use for displaying parameters
    if s.datas:
        ctx = s.datas[0].context
        params = [p for p in ctx.parameters if p.visible]
        entries = view_helpers.get_entries(s.datas, params)
    else:
        params = []
        entries = []
    return dict(set=s, params=params, entries=entries, num_entries=len(entries))


#### sets

def _render_sets_json(sets):
    return jsonify(set_uris=[url_for("set", set_id=s.id) for s in sets])


@app.route('/sets')
@app.route('/sets/<which>')
@login_required
@html_json_mimerender("setlist_display.html", _render_sets_json)
def sets(which='mine'):
    if which == 'all':
        setlist = Set.query.all_readable()
    else:
        setlist = Set.query.filter_by(user=current_user).all_readable()
    return dict(sets=setlist)


#### setimport

@app.route('/sets/<int:set_id>/import')
@login_required
def setimport(set_id):
    s = Set.query.get_or_404(set_id)
    contexts = iter(Context.query)
    return render_template('setimport.html', set=s,
                           importers=list_importers(), contexts=contexts)


@app.route('/sets/<int:set_id>/import/do', methods=['POST'])
@login_required
def setimport_do(set_id):
    userinfo = {}
    filenames = []
    orig_names = []
    try:
        s = Set.query.get(set_id)
        for ffield in sorted(request.files):
            for fstorage in request.files.getlist(ffield):
                name = fstorage.filename
                if not name:
                    continue
                # XXX tempfile is not deleted anywere
                fd, fname = tempfile.mkstemp()
                fd = os.fdopen(fd, 'w')
                fstorage.save(fd, 1024 * 1024)
                fd.close()
                filenames.append(fname)
                orig_names.append(name)
        for key in request.form:
            if not key.startswith('ui_par_'):
                continue
            pname = key[7:]
            d = userinfo[key[3:]] = {}
            d['brief'] = request.form['ui_brief_' + pname]
            d['description'] = request.form['ui_descr_' + pname]
            d['visible'] = bool(request.form.get('ui_vis_' + pname))
            d['unit'] = request.form['ui_unit_' + pname] or None
        if not filenames:
            raise ValueError('Nothing to import.')
        importer = load_importer(request.form['importer'])(target=s)
        try:
            imported = importer.import_items(filenames, orig_names, userinfo)
            db.session.commit()
        except MissingInfo as err:
            db.session.rollback()
            missing = sorted(err.info)
            existing_userinfo = [(k, v) for (k, v) in request.form.iteritems()
                                 if k.startswith('ui_')]
            missing.append((existing_userinfo, 'userinfo'))
            data = render_template('import_missing.html', missing=missing)
            res = 'missing'
        except ImporterError as err:
            db.session.rollback()
            raise
        else:
            res = 'success'
            if len(imported) <= 10:
                data = 'New datas created: ' + \
                    ', '.join(d.name for d in imported) + '.'
            else:
                data = '%d new datas created.' % len(imported)
    except ImporterError as err:
        res = 'error'
        data = str(err)
    return jsonify(result=res, data=data)


#### setcreate

@app.route('/set/create', methods=['POST'])
@login_required
def create_set():
    name = request.form['name']
    s = Set(name=name, user=current_user, group=current_user.primary_group)
    parent_set_id = request.form.get("parent_set_id")
    logg.info("creating new set with name '%s', parent is '%s'", name, parent_set_id)
    if parent_set_id is not None:
        parent_set = Set.query.get(parent_set_id)
        parent_set.children.append(s)
    data_ids = [int(i) for i in request.form.get("data_ids").split(",")]
    logg.debug("data_ids to add %s", data_ids)
    datas = []
    for data_id in data_ids:
        datas.append(Data.query.get(data_id))
    s.datas = datas
    db.session.add(s)
    db.session.commit()
    flash('New dataset successfully created.', 'success')
    return redirect(url_for('set', set_id=s.id))



