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
from yamoda.server.database import User


@app.route('/')
def index():
    """displays the main index page"""
    return render_template('index.html')


@app.route('/login', methods=['GET','POST'])
def login():
    """handles the user login"""
    error = None
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
            error = 'Invalid password or username.'
    return render_template('login.html', error=error)


@app.route("/logout")
@login_required
def logout():
    """logs the current user out"""
    logout_user()
    return redirect(url_for("index"))


@app.route('/register', methods=['GET','POST'])
def register():
    """handles the user registration"""
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        try:
            # XXX: this check could also be done in the User constructor
            if not username or not password:
                raise ValueError
            new_user = User(name=username, password=password)
            db.session.add(new_user)
            db.session.commit()
        except (ValueError, IntegrityError):
            db.session.rollback()
            error = 'Invalid username or password is empty.'
        else:
            login_user(new_user)
            flash('Registered successfully.')
            return redirect(request.args.get("next") or url_for("index"))
    return render_template('register.html', error=error)
