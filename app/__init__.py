from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from nylas import Client
from app.config import Config
from app.models import *
from app.load_data import load

def create_app():
    app = Flask(__name__)
    
    # Load config
    app.config.from_object(Config)

    # Initialize extensions
    db.init_app(app)
    
    # Import all models to ensure they're registered  # Import all models here
    
    with app.app_context():
        recreate_changed_tables(app, db)
        db.create_all()
    
    login_manager = LoginManager(app)
    login_manager.login_view = 'login'

    # Initialize Nylas client
    nylas_client = Client(
        api_key=app.config["NYLAS_API_KEY"],
        api_uri=app.config["NYLAS_API_URI"]
    )
    app.nylas_client = nylas_client

    # Register blueprints
    from app.routes import register_routes
    register_routes(app)

    from app.api import api as api_blueprint
    app.register_blueprint(api_blueprint)

    login_manager.user_loader(load_user)

    with app.app_context():
        load(db)

    return app
