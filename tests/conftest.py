"""
Test configuration and fixtures
"""
import pytest
import os
import sys
import tempfile

# Add parent directory to path to import app modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from models import init_db
from config import Config


class TestConfig(Config):
    """Test configuration"""
    TESTING = True
    DEBUG = False
    SECRET_KEY = 'test-secret-key'
    DATABASE_NAME = ':memory:'  # Use in-memory database for tests
    WTF_CSRF_ENABLED = False  # Disable CSRF for testing


@pytest.fixture
def app():
    """Create and configure a test app instance"""
    # Create temp directory for uploads
    upload_dir = tempfile.mkdtemp()
    
    TestConfig.UPLOAD_FOLDER = upload_dir
    
    # Create app
    app = create_app('default')
    app.config.from_object(TestConfig)
    
    # Setup database
    with app.app_context():
        init_db()
    
    yield app
    
    # Cleanup
    import shutil
    if os.path.exists(upload_dir):
        shutil.rmtree(upload_dir)


@pytest.fixture
def client(app):
    """Test client for the app"""
    return app.test_client()


@pytest.fixture
def runner(app):
    """CLI runner for the app"""
    return app.test_cli_runner()


@pytest.fixture
def auth_client(client):
    """Authenticated test client"""
    # Register and login a test user
    client.post('/register', data={
        'name': 'Test User',
        'email': 'test@example.com',
        'password': 'testpass123',
        'confirm_password': 'testpass123'
    })
    
    client.post('/login', data={
        'email': 'test@example.com',
        'password': 'testpass123'
    })
    
    return client
