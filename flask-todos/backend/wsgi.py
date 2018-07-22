# backend/wsgi.py
from todos.app import create_app
app = create_app()
