# tests/test_gameplay_functions.py
"""Tests for gameplay functions.
"""

from datetime import datetime
from dateutil.relativedelta import relativedelta
import pytest
from gotchi.db import get_db
from gotchi.gameplay_functions import format_age, verify_gotchi_owner, calculate_age, death_check_and_set


@pytest.mark.parametrize(('gotchi_id', 'user_id', 'expected_result'), (
    (1, 1, True),
    (1, 2, False),
    (999, 1, False),
))
def test_verify_gotchi_owner(app, gotchi_id, user_id, expected_result):
    """Test verifying a gotchis owner.
    """

    with app.app_context():
        result = verify_gotchi_owner(gotchi_id, user_id)

        assert result == expected_result


def test_death_check_and_set(app):
    """Test that a gotchi gets their deathdate set.
    """

    with app.app_context():
        db = get_db()
        db.execute(
            "UPDATE Gotchis SET health = 0 WHERE id = 1",
        )
        db.commit()

        death_check_and_set()

        assert db.execute('SELECT deathdate from Gotchis WHERE id = 1').fetchone()[
            'deathdate'] is not None


@pytest.mark.parametrize(('birthdate', 'deathdate', 'expected_result'), (
    ("2026-01-01T00:00:00.00", None, relativedelta(days=1)),
    (datetime(2026, 1, 1), "2027-01-01T00:00:00.00", relativedelta(years=1)),
    (datetime(2026, 1, 1), datetime(2026, 2, 1), relativedelta(months=1)),
))
def test_calculate_age(birthdate, deathdate, expected_result):
    """Test date calculations"""

    assert calculate_age(birthdate, deathdate, datetime(
        2026, 1, 2)) == expected_result


@pytest.mark.parametrize(('delta', 'expected_result'), (
    (relativedelta(minutes=0), "Just born!"),
    (relativedelta(minutes=1), "1 minutes"),
    (relativedelta(hours=1), "1 hours, 0 minutes"),
    (relativedelta(days=1), "1 days 0 hours"),
    (relativedelta(months=1), "1 months, 0 days"),
    (relativedelta(years=1), "1 years, 0 months, 0 days"),
))
def test_format_age(delta, expected_result):
    """Test formatting of age deltas.
    """
    assert format_age(delta) == expected_result
