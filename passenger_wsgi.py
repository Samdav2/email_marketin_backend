import os
import sys

# Add the project directory to sys.path using absolute path
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

# Import the FastAPI app
try:
    from app.main import app
    from a2wsgi import ASGIMiddleware

    # Wrap the FastAPI (ASGI) app with a2wsgi (WSGI)
    # Phusion Passenger looks for 'application' or 'app' by default
    application = ASGIMiddleware(app)
except Exception as e:
    # Log errors to a file for debugging on the server
    with open(os.path.join(SCRIPT_DIR, 'passenger_debug.log'), 'a') as f:
        import datetime
        f.write(f"[{datetime.datetime.now()}] Deployment Error: {str(e)}\n")
    raise e
