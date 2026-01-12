# tests/test_home.py
"""Tests for home routes.
"""

import pytest


@pytest.mark.parametrize(('username', 'password', 'message'), (
    (None, None, b' to start playing!'),
    ('test', 'test', b'Your Gotchis'),
    ('other', 'other', b'You don\'t have any Gotchis yet.'),
))
def test_index_dynamic_gotchi_list(client, auth, username, password, message):
    """Test index.
    """

    if username:
        auth.login(username, password)

    response = client.get('/')

    assert message in response.data
