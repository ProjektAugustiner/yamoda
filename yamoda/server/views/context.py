#  -*- coding: utf-8 -*-
#
# yamoda, (c) 2012, see AUTHORS.  Licensed under the GNU GPL.

"""
Functions:
----------
index    -- displays the main index page
login    -- handles the user login
logout   -- logs the current user out
register -- handles the user registration

"""
from flask import render_template, request, flash, redirect, url_for
from flask.ext.login import login_user, login_required, logout_user
from sqlalchemy.exc import IntegrityError

from yamoda.server import app, db
from yamoda.server.database import Context, User, Group, Set


@app.route('/context', methods=['GET', 'POST'])
@login_required
def contextlist():
    """shows every context in the database"""
    if request.method == 'POST':
        name = request.form['ctx_name']
        brief = request.form['ctx_brief']
        description = request.form['ctx_description']

        try:
            if not name or not brief:
                raise ValueError
            new_ctx = Context(name=name, brief=brief, description=description)
            db.session.add(new_ctx)
            db.session.commit()
        except (ValueError, IntegrityError):
            db.session.rollback()
            flash('Invalid Input', 'error')
        else:
            flash('Created new context: {0}'.format(name), 'info')

    contextlist = Context.query.all()
    return render_template('contextlist.html', contextlist=contextlist)


@app.route('/context/<ctx_name>')
@login_required
def context(ctx_name):
    """displays the requested context"""
    ctx = Context.query.filter_by(name=ctx_name).first_or_404()
    return render_template('context.html', context=ctx)
