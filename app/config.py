from dotenv import load_dotenv
import os
from nylas.models.auth import URLForAuthenticationConfig
from nylas.models.auth import CodeExchangeRequest

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    NYLAS_CLIENT_ID = os.getenv("NYLAS_CLIENT_ID")
    NYLAS_API_KEY = os.getenv("NYLAS_API_KEY")
    NYLAS_API_URI = os.getenv("NYLAS_API_URI", "https://api.nylas.com")
    NYLAS_CALLBACK_URI = os.getenv("NYLAS_CALLBACK_URI")