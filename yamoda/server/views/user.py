#  -*- coding: utf-8 -*-
#
# yamoda, (c) 2012, see AUTHORS.  Licensed under the GNU GPL.

"""
User related views.
"""

from flask import render_template, request, flash, redirect, url_for
from flask.ext.login import login_user, login_required, logout_user, \
     current_user
from sqlalchemy.exc import IntegrityError

from yamoda.server import app, db
from yamoda.server.database import User, Group


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
            return redirect(request.form.get('next') or url_for('index'))
        else:
            flash('Invalid password or username.', 'error')
    return render_template('login.html', next=request.args.get('next', ''))


@app.route("/logout")
@login_required
def logout():
    """logs the current user out"""
    logout_user()
    return redirect(url_for("index"))


@app.route('/register', methods=['GET', 'POST'])
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
            flash('Invalid username', 'error')
        else:
            login_user(new_user)
            flash('Registered successfully.')
            return redirect(request.args.get("next") or url_for("index"))
    return render_template('register.html')


@app.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    """Render the user settings page."""
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'pwchange':
            old_pw = request.form['old_password']
            password = request.form['password']
            confirm = request.form['confirm']
            if not current_user.valid_password(old_pw):
                flash('Old password incorrect.', 'error')
            elif password != confirm:
                flash('New passwords do not match.', 'error')
            elif not password:
                flash('New password is empty.', 'error')
            else:
                current_user.password = password
                db.session.commit()
                flash('Password changed successfully.')
    return render_template('settings.html', user=current_user)
