# gotchi/gameplay_functions.py
"""Gameplay related functions.
"""

from datetime import datetime
from dateutil.relativedelta import relativedelta

def calculate_age(birthdate):
    """Calculate age in years, months, and days from birthdate.

    Args:
        birthdate (datetime): The birthdate of the Gotchi.

    Returns:
        tuple: years, months, and days.
    """
    today = datetime.now()
    delta = relativedelta(today, birthdate)
    return delta.years, delta.months, delta.days

def leaderboard(db):
    """Retrieve the leaderboard of Gotchis based on oldest Gotchis.
    """
    leaderboard_list = db.execute(
        'SELECT Users.username, Gotchis.birthdate as gotchi_birthdate, Gotchis.name AS gotchi_name '
        'FROM Users '
        'LEFT JOIN (SELECT name, MIN(birthdate) as birthdate, owner_id FROM Gotchis '
        'GROUP BY owner_id) AS Gotchis ON Users.id = Gotchis.owner_id '
        'GROUP BY Users.id '
        'HAVING gotchi_birthdate IS NOT NULL '
        'ORDER BY Gotchis.birthdate ASC '
        'LIMIT 10 '
    ).fetchall()

    modified_leaderboard = [dict(entry) for entry in leaderboard_list]

    for entry in modified_leaderboard:
        years, months, days = calculate_age(entry['gotchi_birthdate'])

        entry['rank'] = modified_leaderboard.index(entry) + 1
        entry['gotchi_age'] = f"{years} years, {months} months, {days} days"

    return modified_leaderboard