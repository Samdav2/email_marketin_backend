import os
import sys

# Add the project directory to the sys.path
sys.path.insert(0, os.path.dirname(__file__))

# Import the FastAPI app
from app.main import app
from a2wsgi import ASGIMiddleware

# Wrap the FastAPI (ASGI) app with a2wsgi (WSGI)
application = ASGIMiddleware(app)
