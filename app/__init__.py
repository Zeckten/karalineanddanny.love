from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from nylas import Client
from app.config import Config
from app.models import db, load_user
from flask_migrate import Migrate
from app.load_data import load

migrate = Migrate()

def create_app():
    app = Flask(__name__)
    
    # Load config
    app.config.from_object(Config)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    
    with app.app_context():
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