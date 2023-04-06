import os

from flask import Flask


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE={
            'host': 'localhost',
            'user': 'root',
            'password': 'Zha15067258783',
            'database': 'studentshomework',
        }
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # a simple page that says hello
    @app.route('/hello')
    def hello():
        return 'Hello, World!'

    from . import db
    db.init_app(app)

    from . import auth
    app.register_blueprint(auth.bp)

    from . import student
    app.register_blueprint(student.bp)
    app.add_url_rule('/', endpoint='index')

    from . import admin
    app.register_blueprint(admin.bp)

    return app
