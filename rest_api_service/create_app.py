from flask import Flask
# from flask_migrate import Migrate

from db import db
from config import Config, ProdConfig
from blueprints.api import blueprint


def create_app(config_object: Config):
    """
    An application factory, explained here:
    https://flask.palletsprojects.com/en/3.0.x/patterns/appfactories/
    """
    app = Flask(__name__.split('.')[0])
    app.url_map.strict_slashes = False
    app.config.from_object(config_object)
    _register_extensions(app)
    _register_blueprints(app)
    return app

def _register_extensions(app: Flask):
    """Register Flask extensions."""
    db.init_app(app)
    # Migrate().init_app(app, db)

def _register_blueprints(app: Flask):
    """Register Flask blueprints."""
    app.register_blueprint(blueprint)
