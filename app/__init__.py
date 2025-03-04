from flask import Flask
from .config import Config


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Import routes
    from .routes import app as routes_blueprint

    app.register_blueprint(routes_blueprint)

    return app
