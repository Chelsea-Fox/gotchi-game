# tests/conftest.py
"""Configuration for pytest.
"""

import os
import tempfile
import pytest
from gotchi import create_app
from gotchi.db import get_db, init_db

with open(os.path.join(os.path.dirname(__file__), 'data.sql'), 'rb') as f:
    _data_sql = f.read().decode('utf8')


@pytest.fixture
def app():
    """An application for the tests.
    """
    db_fd, db_path = tempfile.mkstemp()

    app = create_app({
        'TESTING': True,
        'DATABASE': db_path,
    })

    with app.app_context():
        init_db()
        get_db().executescript(_data_sql)

    yield app

    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def client(app):
    """A test client for the app.
    """
    return app.test_client()


@pytest.fixture
def runner(app):
    """A test runner for the app's Click commands.
    """
    return app.test_cli_runner()


class AuthActions(object):
    """Helper for authentication actions in tests.
    """

    def __init__(self, client):
        self._client = client

    def login(self, username='test', password='test'):
        """Log in with the given username and password.
        """
        return self._client.post(
            '/auth/login',
            data={'username': username, 'password': password}
        )

    def logout(self):
        """Log out.
        """
        return self._client.get('/auth/logout')


@pytest.fixture
def auth(client):
    """Authentication actions for tests.
    """
    return AuthActions(client)
