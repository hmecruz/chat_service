from flask import Flask
from .static_routes_events import static_routes_bp

def register_static_routes(app: Flask):
    """
    Registers the static frontend routes to the Flask app.
    """
    app.register_blueprint(static_routes_bp)
