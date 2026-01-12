# gotchi/gameplay_functions.py
"""Gameplay related functions.
"""

from datetime import datetime
from dateutil.relativedelta import relativedelta

from gotchi.db import get_db


def calculate_age(birthdate, deathdate=None):
    """Calculate age in years, months, and days from birthdate.

    Args:
        birthdate (datetime or string): The birthdate of the Gotchi.
        deathdate (datetime or string, optional): The deathdate of the Gotchi.
    Returns:
        relativedelta: Age difference as a relativedelta object.
    """
    comparison_date = datetime.now()

    if isinstance(birthdate, str):
        birthdate = datetime.fromisoformat(birthdate)
        comparison_date = datetime.now()

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
        ' GROUP BY Users.id'
        ' HAVING gotchi_birthdate IS NOT NULL'
        ' ORDER BY Gotchis.birthdate ASC'
    ).fetchall()

    leaderboard_list = [dict(entry) for entry in gotchi_list]

    for entry in leaderboard_list:
        entry['gotchi_age'] = calculate_age(entry['gotchi_birthdate'])

    modified_leaderboard = sorted(leaderboard_list, key=lambda x: (
        x['gotchi_age'].years, x['gotchi_age'].months, x['gotchi_age'].days), reverse=True)

    for entry in modified_leaderboard[:10]:
        entry['gotchi_age'] = format_age(
            calculate_age(entry['gotchi_birthdate']))
        entry['gotchi_alive_dead'] = 'Alive' if entry['gotchi_deathdate'] is None else 'Dead'
        entry['rank'] = modified_leaderboard.index(entry) + 1

    return modified_leaderboard


def verify_gotchi_owner(gotchi_id, user_id):
    """Verify if a user is the owner of a Gotchi.

    Args:
        gotchi_id (_type_): Gotchi ID to verify.
        user_id (_type_): User ID to verify against.

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
