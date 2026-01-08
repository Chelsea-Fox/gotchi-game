# gotchi/auth.py
"""auth blueprint for user registration and login.
"""

import functools
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from gotchi.db import get_db

bp = Blueprint('auth', __name__, url_prefix='/auth')


@bp.route('/register', methods=('GET', 'POST'))
def register():
    """Route to register a new user.
    """
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None

        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'

        if error is None:
            try:
                db.execute(
                    "INSERT INTO Users (username, password) VALUES (?, ?)",
                    (username, generate_password_hash(password)),
                )
                db.commit()
            except db.IntegrityError:
                error = "Username already in use."
            else:
                user = db.execute(
                    'SELECT * FROM Users WHERE username = ?', (username,)
                ).fetchone()

                session.clear()
                session['user_id'] = user['id']

                return redirect(url_for("home.index"))

        flash(error)

    return render_template('auth/register.html')


@bp.route('/login', methods=('GET', 'POST'))
def login():
    """Route to log in an existing user.
    """
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None
        user = db.execute(
            'SELECT * FROM Users WHERE username = ?', (username,)
        ).fetchone()

        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect password.'

        if error is None:
            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for('index'))

        flash(error)

    return render_template('auth/login.html')


@bp.before_app_request
def load_logged_in_user():
    """Load the logged-in user from the session.
    """
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT * FROM Users WHERE id = ?', (user_id,)
        ).fetchone()


@bp.route('/logout')
def logout():
    """Log out the current user.
    """
    session.clear()
    return redirect(url_for('index'))


def login_required(view):
    """Wrapper to ensure a user is logged in before accessing a view.

    Args:
        view (view (Flask)): Wrapped view function.
    """
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view


@bp.route('/delete_account', methods=('GET', 'POST'))
@login_required
def delete_account():
    """Route to delete a users account.
    """
    if request.method == 'POST':
        password = request.form['password']
        error = None
        db = get_db()
        user = db.execute(
            'SELECT * FROM Users WHERE id = ?', (g.user['id'],)
        ).fetchone()

        if not check_password_hash(user['password'], password):
            error = 'Incorrect password.'

        if error is None:
            db.execute('DELETE FROM Users WHERE id = ?', (g.user['id'],))
            db.commit()
            session.clear()
            return redirect(url_for('index'))

        flash(error)

    return render_template('auth/delete_account.html')
