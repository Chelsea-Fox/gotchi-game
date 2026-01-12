# gotchi/background_tasks/hunger.py
"""Module to manage hunger levels of Gotchis in the game.
"""

from gotchi.extensions import scheduler
from gotchi.db import get_db
from gotchi.gameplay_config import GAMEPLAY_CONFIG
from gotchi.gameplay_functions import death_check_and_set


@scheduler.task(
    "interval",
    id="hunger",
    seconds=60,
    max_instances=1,
)
def task():
    """Task manager for hunger tasks
    """
    print(f"{__name__} Started", flush=True)

    with scheduler.app.app_context():
        hunger_decrementer()
        health_decrementer()
        death_check_and_set()

    print(f"{__name__} Done", flush=True)


def hunger_decrementer():
    """
    Manages the hunger levels of Gotchis.
    """

    # Lower hunger by hunger_decrease_amount (min of 0) if
    # last_fed is older than hunger_decrease_interval_minutes.
    #
    # If Hunger level is:
    # <= starving_threshold: set status to "starving"
    # <= hungry_threshold: set status to "hungry"
    # > full_threshold: set status to "full"
    # else: set status to "normal"
    db = get_db()

    db.execute('UPDATE Gotchis SET'
               ' hunger = CASE WHEN hunger <= ? THEN 0 ELSE hunger - ? END,'
               ' hunger_status = CASE'
               ' WHEN hunger <= ? THEN "starving"'
               ' WHEN hunger <= ? THEN "hungry"'
               ' WHEN hunger >= ? THEN "full"'
               ' ELSE "normal"'
               ' END'
               ' WHERE deathdate IS NULL'
               ' AND hunger > 0'
               ' AND ROUND((JULIANDAY(CURRENT_TIMESTAMP) - JULIANDAY(last_fed)) * 86400) >= ?',
               (
                   GAMEPLAY_CONFIG["hunger_decrease_amount"],
                   GAMEPLAY_CONFIG["hunger_decrease_amount"],
                   GAMEPLAY_CONFIG["starving_threshold"],
                   GAMEPLAY_CONFIG["hungry_threshold"],
                   GAMEPLAY_CONFIG["full_threshold"],
                   GAMEPLAY_CONFIG["hunger_decrease_interval_seconds"],
               ))
    db.commit()


def health_decrementer():
    """
    Manages the health levels of Gotchis, based on hunger actions.
    """

    # Lower health by health_decrease_when_starving (min of 0) if Gotchi is starving.

    db = get_db()

    db.execute('UPDATE Gotchis SET'
               ' health = CASE WHEN health <= ? THEN 0 ELSE health - ? END'
               ' WHERE deathdate IS NULL'
               ' AND hunger = ?',
               (
                   GAMEPLAY_CONFIG["health_decrease_when_starving"],
                   GAMEPLAY_CONFIG["health_decrease_when_starving"],
                   GAMEPLAY_CONFIG["starving_threshold"],
               ))
    db.commit()
