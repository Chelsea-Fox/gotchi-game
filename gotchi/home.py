# gotchi/home.py
"""home blueprint for the main, non gameplay pages.
"""

from flask import Blueprint, render_template
from gotchi.db import get_db
from gotchi.gameplay_functions import leaderboard

bp = Blueprint('home', __name__)

@bp.route('/')
def index():
    """Home page route.
    """
    db = get_db()

    return render_template('home/index.html', leaderboard=leaderboard(db))
