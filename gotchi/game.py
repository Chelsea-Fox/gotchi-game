# gotchi/game.py
"""game blueprint for gameplay related pages.
"""

from flask import Blueprint, flash, redirect, render_template, g, request, url_for
from gotchi.db import get_db
from gotchi.auth import login_required
from gotchi.gameplay_functions import calculate_age, format_age, verify_gotchi_owner

bp = Blueprint('game', __name__)


@login_required
@bp.route('/gotchis')
def gotchi_list():
    """Game page route.
    """
    db = get_db()

    gotchis = db.execute(
        'SELECT g.id, g.name, g.birthdate'
        ' FROM Gotchis g JOIN Users u ON g.owner_id = u.id'
        ' WHERE u.id = ?'
        ' ORDER BY g.birthdate DESC', (g.user['id'],)
    ).fetchall()

    modified_gotchi_list = [dict(entry) for entry in gotchis]

    for entry in modified_gotchi_list:
        entry['age'] = format_age(calculate_age(entry['birthdate']))

    return render_template('game/index.html', gotchi_list=modified_gotchi_list)


@login_required
@bp.route('/new', methods=('GET', 'POST'))
def new_gotchi():
    """Route to create a new gotchi.
    """
    if request.method == 'GET':
        return render_template('game/new.html')

    ## POST handling ##
    name = request.form['name'] or "Gotchi"

    db = get_db()

    # Insert the new gotchi
    db.execute(
        'INSERT INTO Gotchis (name, owner_id)'
        ' VALUES (?, ?)',
        (name, g.user['id'])
    )
    db.commit()

    # Select the new gotchi's id
    gotchi_id = db.execute(
        'SELECT id FROM Gotchis WHERE owner_id = ? ORDER BY birthdate DESC LIMIT 1',
        (g.user['id'],)
    ).fetchone()['id']

    return redirect(url_for("game.play", gotchi_id=gotchi_id))


@login_required
@bp.route('/delete/<int:gotchi_id>', methods=('GET', 'POST'))
def delete_gotchi(gotchi_id):
    """Route to delete a gotchi.
    """

    if not verify_gotchi_owner(gotchi_id, g.user['id']):
        error = "Gotchi does not belong to you."
        flash(error)
        return redirect(url_for("game.gotchi_list"))

    db = get_db()

    gotchi_name = db.execute(
        'SELECT name FROM Gotchis WHERE id = ?',
        (gotchi_id,)
    ).fetchone()['name']

    if request.method == 'GET':
        return render_template('game/delete.html', gotchi_id=gotchi_id, gotchi_name=gotchi_name)

    ## POST handling ##
    db.execute(
        'DELETE FROM Gotchis WHERE id = ?',
        (gotchi_id,)
    )
    db.commit()

    return redirect(url_for("game.gotchi_list"))
