# tests/test_auth.py
"""Tests for authentication routes.
"""

import pytest
from flask import g, session
from gotchi.db import get_db

def test_register(client, app):
    """Test user registration.
    """
    assert client.get('/auth/register').status_code == 200
    response = client.post(
        '/auth/register', data={'username': 'a', 'password': 'a'}
    )
    assert response.headers["Location"] == "/auth/login"

    with app.app_context():
        assert get_db().execute(
            "SELECT * FROM Users WHERE username = 'a'",
        ).fetchone() is not None


@pytest.mark.parametrize(('username', 'password', 'message'), (
    ('', '', b'Username is required.'),
    ('a', '', b'Password is required.'),
    ('test', 'test', b'Username already in use.'),
))
def test_register_validate_input(client, username, password, message):
    """Test registration input validation.
    """
    response = client.post(
        '/auth/register',
        data={'username': username, 'password': password}
    )
    assert message in response.data

def test_login(client, auth):
    """Test user login.
    """
    assert client.get('/auth/login').status_code == 200
    response = auth.login()
    assert response.headers["Location"] == "/"

    with client:
        client.get('/')
        assert session['user_id'] == 1
        assert g.user['username'] == 'test'

@pytest.mark.parametrize(('username', 'password', 'message'), (
    ('a', 'test', b'Incorrect username.'),
    ('test', 'a', b'Incorrect password.'),
))
def test_login_validate_input(auth, username, password, message):
    """Test login input validation.
    """
    response = auth.login(username, password)
    assert message in response.data

def test_logout(client, auth):
    """Test user logout.
    """
    auth.login()

    with client:
        auth.logout()
        assert 'user_id' not in session
