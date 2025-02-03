from wsgi2 import serve
from app import create_app

app = create_app()
serve(app, host='127.0.0.1', port=8080)