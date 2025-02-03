import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from nylas import Client
from app.config import Config
from app.models import *
from app.clear_tables import auto_migrate_database
from app.load_data import load
import os

login_manager = LoginManager()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    
    # Load config
    app.config.from_object(Config)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    
    # Import all models to ensure they're registered
    with app.app_context():
        db.create_all()
        # auto_migrate_database(app, db)  # Automatically migrate database schema if differences are detected
    
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    # Initialize Nylas client
    nylas_client = Client(
        api_key=app.config["NYLAS_API_KEY"],
        api_uri=app.config["NYLAS_API_URI"]
    )
    app.nylas_client = nylas_client

    # Configure logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    handler = logging.StreamHandler()
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    # Register blueprints
    from app.routes.main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from app.routes.auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    from app.routes.admin import admin as admin_blueprint
    app.register_blueprint(admin_blueprint)

    from app.routes.api import api as api_blueprint
    app.register_blueprint(api_blueprint)

    login_manager.user_loader(load_user)

    #with app.app_context():
        #load(db)

    return app
