# gotchi/home.py
"""home blueprint for the main, non gameplay pages.
"""

from flask import Blueprint, render_template, g
from gotchi.gameplay_functions import leaderboard
from gotchi.db import get_db

bp = Blueprint('home', __name__)

@bp.route('/')
def index():
    """Home page route.
    """
    has_gotchis = False

    if g.user:
        db = get_db()
        gotchi_count = db.execute(
            'SELECT COUNT(*) FROM Gotchis WHERE owner_id = ?', (g.user['id'],)
        ).fetchone()[0]

        has_gotchis = gotchi_count > 0

    return render_template('home/index.html', leaderboard=leaderboard(), has_gotchis=has_gotchis)
