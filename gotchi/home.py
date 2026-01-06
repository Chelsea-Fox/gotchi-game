# gotchi/home.py
"""home blueprint for the main, non gameplay pages.
"""

from flask import (
    Blueprint, render_template#, request, url_for, flash, g, redirect
)
#from werkzeug.exceptions import abort

#from gotchi.auth import login_required
#from gotchi.db import get_db

bp = Blueprint('home', __name__)

@bp.route('/')
def index():
    """Home page route.
    """
    return render_template('home/index.html')
