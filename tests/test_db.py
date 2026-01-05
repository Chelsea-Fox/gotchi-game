# tests/test_db.py
"""Tests for gotchi.db module.
"""

import sqlite3
import pytest
from gotchi.db import get_db


def test_get_close_db(app):
    """Test getting and closing the database connection.
    """
    with app.app_context():
        db = get_db()
        assert db is get_db()

    with pytest.raises(sqlite3.ProgrammingError) as e:
        db.execute('SELECT 1')

    assert 'closed' in str(e.value)

def test_init_db_command(runner, monkeypatch):
    """Test the init-db command.
    """
    class Recorder:
        """Helper class to record if init_db was called.
        """
        called = False

    def fake_init_db():
        Recorder.called = True

    monkeypatch.setattr('gotchi.db.init_db', fake_init_db)
    result = runner.invoke(args=['init-db'])
    assert 'Initialized' in result.output
    assert Recorder.called
