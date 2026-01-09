# gotchi/background_tasks/hunger.py
"""Module to manage hunger levels of Gotchis in the game.
"""


from datetime import datetime
from gotchi.db import get_db
from gotchi.gameplay_config import GameplayConfig


def task(app):
    """
    A background task that manages the hunger levels of Gotchis.
    This function is intended to be run periodically to decrease
    the hunger level of each Gotchi.
    """

    # Lower hunger by hunger_decrease_amount if
    # last_fed is older than hunger_decrease_interval_minutes.
    #
    # If Hunger level is:
    # <= starving_threshold: set status to "starving"
    # <= hungry_threshold: set status to "hungry"
    # > full_threshold: set status to "full"
    # else: set status to "normal"

    try:
        db = get_db()
        db.execute('UPDATE gotchis'
                   ' SET hunger = hunger - ?,'
                   ' hunger_status = CASE'
                   ' WHEN hunger <= ? THEN "starving"'
                   ' WHEN hunger <= ? THEN "hungry"'
                   ' WHEN hunger >= ? THEN "full"'
                   ' ELSE "normal"'
                   ' END'
                   ' WHERE deathdate IS NULL'
                   ' AND ROUND((JULIANDAY(CURRENT_TIMESTAMP) - JULIANDAY(last_fed)) * 86400) <= ?',
                   (
                       GameplayConfig["hunger_decrease_amount"],
                       GameplayConfig["hungry_threshold"],
                       GameplayConfig["starving_threshold"],
                       GameplayConfig["full_threshold"],
                       GameplayConfig["hunger_decrease_interval_seconds"],
                   ))
        return "Success"
    except Exception as e:
        return f"Error: {e}"
