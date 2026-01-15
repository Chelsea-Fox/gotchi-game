# gotchi/gameplay_functions.py
"""Gameplay related functions.
"""

from datetime import datetime
from dateutil.relativedelta import relativedelta
from flask import Blueprint, g, redirect, request, url_for
from gotchi.db import get_db
from gotchi.auth import login_required
from gotchi.gameplay_config import GAMEPLAY_CONFIG


bp = Blueprint('gameplay', __name__, url_prefix='/gameplay')


def calculate_age(birthdate, deathdate=None, comparison_date=None):
    """Calculate age in years, months, and days from birthdate.

    Args:
        birthdate (datetime or string): The birthdate of the Gotchi.
        deathdate (datetime or string, optional): The deathdate of the Gotchi.
        comparison_date (datetime, optional): overridable comparison date for testing.
    Returns:
        relativedelta: Age difference as a relativedelta object.
    """

    if not comparison_date:
        comparison_date = datetime.now()

    if isinstance(birthdate, str):
        birthdate = datetime.fromisoformat(birthdate)

    if deathdate:
        if isinstance(deathdate, str):
            deathdate = datetime.fromisoformat(deathdate)
        comparison_date = deathdate

    delta = relativedelta(comparison_date, birthdate)

    return delta


def format_age(delta):
    """Format age from relativedelta into a human-readable string.

    Args:
        delta (relativedelta): Age difference as a relativedelta object.
    Returns:
        string: Human-readable age.
    """
    if delta.years > 0:
        return f"{delta.years} years, {delta.months} months, {delta.days} days"
    if delta.months > 0:
        return f"{delta.months} months, {delta.days} days"
    if delta.days > 0:
        return f"{delta.days} days {delta.hours} hours"
    if delta.hours > 0:
        return f"{delta.hours} hours, {delta.minutes} minutes"
    if delta.minutes > 0:
        return f"{delta.minutes} minutes"

    return "Just born!"


def leaderboard():
    """Retrieve the leaderboard of Gotchis based on oldest Gotchis.
    """
    db = get_db()

    gotchi_list = db.execute(
        'SELECT Users.username, Gotchis.birthdate as gotchi_birthdate, Gotchis.deathdate'
        ' as gotchi_deathdate , Gotchis.name AS gotchi_name'
        ' FROM Gotchis'
        ' LEFT JOIN Users ON Users.id = Gotchis.owner_id'
    ).fetchall()

    leaderboard_list = [dict(entry) for entry in gotchi_list]

    for entry in leaderboard_list:
        entry['gotchi_age'] = calculate_age(
            entry['gotchi_birthdate'], entry['gotchi_deathdate'])

    modified_leaderboard = sorted(leaderboard_list, key=lambda x: (
        x['gotchi_age'].years, x['gotchi_age'].months, x['gotchi_age'].days,
        x['gotchi_age'].hours, x['gotchi_age'].minutes, x['gotchi_age'].seconds), reverse=True)

    for entry in modified_leaderboard:
        entry['gotchi_age'] = format_age(entry['gotchi_age'])
        entry['gotchi_alive_dead'] = 'Alive' if entry['gotchi_deathdate'] is None else 'Dead'
        entry['rank'] = modified_leaderboard.index(entry) + 1

    leaderboard_users = []
    formatted_leaderboard = []
    for entry in modified_leaderboard:
        if len(formatted_leaderboard) == 10:
            break

        if entry['username'] not in leaderboard_users:
            leaderboard_users.append(entry['username'])
            formatted_leaderboard.append(entry)

    return formatted_leaderboard


def verify_gotchi_owner(gotchi_id, user_id):
    """Verify if a user is the owner of a Gotchi.

    Args:
        gotchi_id (int): Gotchi ID to verify.
        user_id (int): User ID to verify against.

    Returns:
        bool: Wether the user is the owner of the Gotchi.
    """
    db = get_db()

    gotchi = db.execute(
        'SELECT owner_id FROM Gotchis WHERE id = ?',
        (gotchi_id,)
    ).fetchone()

    if gotchi is None:
        return False

    return gotchi['owner_id'] == user_id


def death_check_and_set():
    """Checks if a Gotchi has died, and sets its deathdate accordingly.
    """
    db = get_db()

    db.execute('UPDATE Gotchis SET'
               ' deathdate = CURRENT_TIMESTAMP'
               ' WHERE deathdate IS NULL'
               ' AND health = 0')
    db.commit()


@login_required
@bp.route('/feed', methods=['POST'])
def feed_gotchi():
    """Feeds a gotchi by a set ammount.

    Args:
        gotchi_id (int): Gotchi ID to feed.
    """
    gotchi_id = request.form['gotchi_id']

    if verify_gotchi_owner(gotchi_id, g.user['id']):
        db = get_db()

        db.execute(
            'UPDATE Gotchis'
            ' SET hunger = CASE WHEN hunger + ? > 100 THEN 100 ELSE hunger + ? END'
            ' WHERE id = ?',
            (
                GAMEPLAY_CONFIG["hunger_increase_on_feed"],
                GAMEPLAY_CONFIG["hunger_increase_on_feed"],
                gotchi_id,
            )
        )
        db.commit()

    hunger_status_setter()

    return redirect(url_for("game.play", gotchi_id=gotchi_id))


def hunger_status_setter():
    """
    Manages the hunger status of Gotchis.
    """

    # If Hunger level is:
    # <= starving_threshold: set status to "starving"
    # <= hungry_threshold: set status to "hungry"
    # > full_threshold: set status to "full"
    # else: set status to "normal"
    db = get_db()

    db.execute('UPDATE Gotchis SET'
               ' hunger_status = CASE'
               ' WHEN hunger <= ? THEN "starving"'
               ' WHEN hunger <= ? THEN "hungry"'
               ' WHEN hunger >= ? THEN "full"'
               ' ELSE "normal"'
               ' END'
               ' WHERE deathdate IS NULL',
               (
                   GAMEPLAY_CONFIG["starving_threshold"],
                   GAMEPLAY_CONFIG["hungry_threshold"],
                   GAMEPLAY_CONFIG["full_threshold"],
               ))
    db.commit()
