# gotchi/__init__.py
"""Application Factory for the Flask instance.
"""

import os
import sys
from multiprocessing import Process
from flask import Flask

from .extensions import scheduler

from . import db, auth, home, game


def create_app(test_config=None):
    """Create and configure the Flask application.

    Args:
        test_config (str, optional): Path to the test config.py file. Defaults to None.

    Returns:
        app (Flask): Flask application instance
    """

    def is_debug_mode():
        """Get app debug status."""
        debug = os.environ.get("FLASK_DEBUG")
        if not debug:
            return os.environ.get("FLASK_ENV") == "development"
        return debug.lower() not in ("0", "false", "no")

    def is_werkzeug_reloader_process():
        """Get werkzeug status."""
        return os.environ.get("WERKZEUG_RUN_MAIN") == "true"

    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'gotchi-game.sqlite'),
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # simple test page that says hello
    @app.route('/hello')
    def hello():
        return 'Hello, World!'

    db.init_app(app)

    app.register_blueprint(auth.bp)

    app.register_blueprint(home.bp)
    app.add_url_rule('/', endpoint='index')

    app.register_blueprint(game.bp)

    scheduler.init_app(app)
    with app.app_context():
        # If in debug mode, make sure to only run one process
        if is_debug_mode() and not is_werkzeug_reloader_process():
            pass
        else:
            from .background_tasks import hunger

            scheduler.start()

    return app
