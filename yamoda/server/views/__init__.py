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


@app.route('/context', methods=['GET','POST'])
@login_required
def contexttable():
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
            flash('Invalid Input','error')
        else:
            flash('Created new context: {0}'.format(name), 'info')

    contextlist = Context.query.all()
    return render_template('contexttable.html', contextlist=contextlist)


@app.route('/context/<ctx_name>')
@login_required
def context(ctx_name):
    """displays the requested context"""
    ctx = Context.query.filter_by(name=ctx_name).first_or_404()
    return render_template('context.html', context=ctx)


@app.route('/')
def index():
    """displays the main index page"""
    return render_template('index.html')


@app.route('/login', methods=['GET','POST'])
def login():
    """handles the user login"""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        remember = request.form.get("remember", "no") == "yes"

        user = User.query.filter_by(name=username).first()
        if (user is not None) and user.valid_password(password):
            login_user(user, remember=remember)
            flash('Logged in successfully.')
            return redirect(request.args.get("next") or url_for("index"))
        else:
            flash('Invalid password or username.','error')
    return render_template('login.html')


@app.route("/logout")
@login_required
def logout():
    """logs the current user out"""
    logout_user()
    return redirect(url_for("index"))


@app.route('/register', methods=['GET','POST'])
def register():
    """handles the user registration"""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm = request.form['confirm']

        try:
            # XXX: this check could also be done in the User constructor
            if not username or not password:
                raise ValueError('Empty Username or Password')
            if password != confirm:
                raise ValueError("Password mismatch")
            primary_group = Group(name=username)
            new_user = User(name=username, password=password, 
                            primary_group=primary_group)
            db.session.add(new_user)
            db.session.commit()
        except ValueError, e:
            flash(str(e), 'error')
        except IntegrityError:
            db.session.rollback()
            flash('Invalid username','error')
        else:
            login_user(new_user)
            flash('Registered successfully.')
            return redirect(request.args.get("next") or url_for("index"))
    return render_template('register.html')


@app.route('/settings')
def usersettings():
    """user settings stub"""
    return ''


@app.route('/data')
@login_required
def data_view(all=False):
    setlist = Set.query.all()
    for s in setlist:
        print s.readable()
    return render_template('setlist.html', sets=setlist)
