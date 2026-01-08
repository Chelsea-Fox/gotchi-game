# gotchi/__init__.py
"""Application Factory for the Flask instance.
"""

import os
from flask import Flask

from gotchi.background_tasks.task_manager import TaskManager

from . import db, auth, home, game


def create_app(test_config=None):
    """Create and configure the Flask application.

    Args:
        test_config (str, optional): Path to the test config.py file. Defaults to None.

    Returns:
        app (Flask): Flask application instance
    """

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

    task_manager = TaskManager()
    task_manager.start_background_tasks()

    app.register_blueprint(auth.bp)

    app.register_blueprint(home.bp)
    app.add_url_rule('/', endpoint='index')

    app.register_blueprint(game.bp)

    return app
