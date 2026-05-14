from flask import Flask
from app.config import Config

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    from app.auth.routes import auth_bp
    from app.dashboard.routes import dashboard_bp
    from app.documents.routes import documents_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(documents_bp)

    return app