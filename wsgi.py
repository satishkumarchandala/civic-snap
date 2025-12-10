"""
WSGI entry point for production deployment
Used by Gunicorn, uWSGI, and other WSGI servers
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set production environment
os.environ.setdefault('FLASK_ENV', 'production')

# Import create_app from run module
from run import create_app

# Create application instance
app = create_app('production')

if __name__ == '__main__':
    app.run()
