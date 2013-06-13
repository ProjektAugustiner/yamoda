#  -*- coding: utf-8 -*-
#
# yamoda, (c) 2012, see AUTHORS.  Licensed under the GNU GPL.
from mimeparse import best_match
from flask import make_response
from yamoda.server.mimerender import mimerender

"""
User related views.
"""


import logging
import json
from functools import partial
from flask import render_template, request, flash, redirect, url_for
from flask.ext.login import login_user, login_required, logout_user, \
     current_user
from sqlalchemy.exc import IntegrityError

from yamoda.server import app, db
from yamoda.server.database import User, Group

logg = logging.getLogger("yamoda.views.user")


@app.route('/login', methods=['GET'])
@mimerender(
    html=partial(render_template, "login.html"),
)
def login():
    """show login page"""
    return dict(next=request.args.get('next', ''))


def _check_user_login(request_data):
    username = request_data["username"]
    password = request_data["password"]
    remember = request_data.get("remember", False)
    logg.debug("username %s type %s password %s, type %s", username, type(username), password, type(password))
    user = User.query.filter_by(name=username).first()
    logg.debug("user found? %s", user)
    if (user is not None) and user.valid_password(password):
        login_user(user, remember=remember)
        return True
    else:
        return False


def _login_html():
    login_success = _check_user_login(request.form)
    if login_success:
        flash('Logged in successfully.', 'info')
        return redirect(request.form.get('next') or url_for('index'), 302)
    else:
        flash('Invalid password or username.', 'error')
        return render_template("login.html", next=request.args.get('next', ''))


def _login_json():
    logg.debug("request.data %s", request.data)
    login_success = _check_user_login(request.json)
    if login_success:
        return make_response(json.dumps(dict(msg="success")), 200)
    else:
        return make_response(json.dumps(dict(msg="invalid credentials")), 401)


@app.route('/login', methods=['POST'])
@mimerender(
    html=_login_html,
    json=_login_json
)
def login_post():
    """handles the user login"""
    return {}


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
