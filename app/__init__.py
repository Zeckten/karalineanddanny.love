from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from nylas import Client
from app.config import Config
from app.models import db, load_user
from flask_migrate import Migrate

migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    migrate.init_app(app, db)

    login_manager = LoginManager(app)
    login_manager.login_view = 'login'

    # Initialize Nylas client
    nylas_client = Client(
        api_key=app.config["NYLAS_API_KEY"],
        api_uri=app.config["NYLAS_API_URI"]
    )
    app.nylas_client = nylas_client  # Attach the client to the app instance

    # Register blueprints or routes
    from app.routes import register_routes
    register_routes(app)

    
    login_manager.user_loader(load_user)


    return app