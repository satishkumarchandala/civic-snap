"""
Configuration settings for Urban Issue Reporter
Environment-based configuration management
"""
import os
from datetime import timedelta


class Config:
    """Base configuration class"""
    # Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # Upload settings
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'uploads')
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5MB max file size (reduced for memory optimization)
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    
    # MongoDB settings
    MONGO_URI = os.environ.get('MONGO_URI') or 'mongodb+srv://satishchandala834_db_user:0MivD44lzk3kCcqk@cluster0.izh4its.mongodb.net/'
    MONGO_DB_NAME = os.environ.get('MONGO_DB_NAME') or 'urban_issues_db'
    
    # Email configuration
    MAIL_SERVER = os.environ.get('MAIL_SERVER') or 'smtp.gmail.com'
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() == 'true'
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME') or 'satishchandala834@gmail.com'
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD') or 'oqqv jvjk byzf kbhn'
    
    # Session settings
    SESSION_COOKIE_SECURE = False
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    
    # ML Models
    ML_MODELS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'models')
    
    # Logging
    LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
    
    # Admin user default credentials
    DEFAULT_ADMIN_NAME = 'Admin User'
    DEFAULT_ADMIN_EMAIL = 'admin@example.com'
    DEFAULT_ADMIN_PASSWORD = 'admin123'


class DevelopmentConfig(Config):
    """Development environment configuration"""
    DEBUG = True
    TESTING = False
    HOST = '0.0.0.0'
    PORT = 5000


class ProductionConfig(Config):
    """Production environment configuration"""
    DEBUG = False
    TESTING = False
    
    # Force secure settings in production
    SESSION_COOKIE_SECURE = True
    SECRET_KEY = os.environ.get('SECRET_KEY')  # Must be set in production
    
    # Stricter security
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Strict'


class TestingConfig(Config):
    """Testing environment configuration"""
    DEBUG = True
    TESTING = True
    MONGO_DB_NAME = 'urban_issues_test_db'


# Configuration dictionary
config_by_name = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}


def get_config(config_name=None):
    """Get configuration class by name"""
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    
    return config_by_name.get(config_name, DevelopmentConfig)
