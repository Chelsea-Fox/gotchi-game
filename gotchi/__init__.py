# gotchi/__init__.py
"""Application Factory for the Flask instance.
"""

import os
import atexit

from flask import Flask

from .extensions import scheduler
from . import db, auth, home, game, gameplay_functions


def create_app(test_config=None):
    """Create and configure the Flask application.

    Args:
        test_config (str, optional): Path to the test config.py file. Defaults to None.

    Returns:
        app (Flask): Flask application instance
    """

    print(test_config, flush=True)

    def is_debug_mode():  # pragma: no cover
        """Get app debug status."""
        debug = os.environ.get("FLASK_DEBUG")
        if not debug:
            return os.environ.get("FLASK_ENV") == "development"
        return debug.lower() not in ("0", "false", "no")

    def is_werkzeug_reloader_process():  # pragma: no cover
        """Get werkzeug status."""
        return os.environ.get("WERKZEUG_RUN_MAIN") == "true"

    @atexit.register
    def at_shutdown():  # pragma: no cover
        # Ensure scheduler is shutdown at exit
        if scheduler.running:
            scheduler.shutdown()

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
    app.register_blueprint(gameplay_functions.bp)

    with app.app_context():  # pragma: no cover
        # If in debug mode, make sure to only run one process, and dont run when testing.
        print(test_config, flush=True)
        if is_debug_mode() and not is_werkzeug_reloader_process() and test_config is None:
            pass
        else:
            if scheduler.app is None:
                scheduler.init_app(app)

            from .background_tasks import hunger  # noqa: C0415,W0611 pylint:disable=import-outside-toplevel,unused-import

            if not scheduler.running:
                scheduler.start()

    return app
