"""
Logging configuration for Urban Issue Reporter
Provides structured logging with file rotation and different log levels
"""
import logging
import os
from logging.handlers import RotatingFileHandler
from datetime import datetime

def setup_logging(app):
    """
    Configure application logging with file rotation
    
    Creates three log files:
    - app.log: General application logs
    - error.log: Error and critical logs only
    - ml.log: Machine learning specific logs
    """
    
    # Create logs directory if it doesn't exist
    logs_dir = 'logs'
    os.makedirs(logs_dir, exist_ok=True)
    
    # Remove default Flask handlers
    app.logger.handlers.clear()
    
    # Set base log level
    app.logger.setLevel(logging.DEBUG if app.config.get('DEBUG') else logging.INFO)
    
    # Format for logs
    detailed_formatter = logging.Formatter(
        '[%(asctime)s] %(levelname)s in %(module)s.%(funcName)s:%(lineno)d - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    simple_formatter = logging.Formatter(
        '[%(asctime)s] %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # 1. Application log handler (rotating, max 10MB, keep 5 backups)
    app_handler = RotatingFileHandler(
        os.path.join(logs_dir, 'app.log'),
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5
    )
    app_handler.setLevel(logging.INFO)
    app_handler.setFormatter(detailed_formatter)
    app.logger.addHandler(app_handler)
    
    # 2. Error log handler (only errors and critical)
    error_handler = RotatingFileHandler(
        os.path.join(logs_dir, 'error.log'),
        maxBytes=10 * 1024 * 1024,
        backupCount=5
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(detailed_formatter)
    app.logger.addHandler(error_handler)
    
    # 3. Console handler for development
    if app.config.get('DEBUG'):
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)
        console_handler.setFormatter(simple_formatter)
        app.logger.addHandler(console_handler)
    
    # Log startup
    app.logger.info('=' * 80)
    app.logger.info('🚀 Urban Issue Reporter Application Starting')
    app.logger.info(f'Environment: {"Development" if app.config.get("DEBUG") else "Production"}')
    app.logger.info(f'Log directory: {os.path.abspath(logs_dir)}')
    app.logger.info('=' * 80)
    
    return app.logger


def get_ml_logger():
    """
    Get dedicated logger for ML operations
    Useful for tracking model training, predictions, and performance
    """
    ml_logger = logging.getLogger('ml_logger')
    
    if not ml_logger.handlers:
        ml_logger.setLevel(logging.INFO)
        
        # Create logs directory
        os.makedirs('logs', exist_ok=True)
        
        # ML log handler
        ml_handler = RotatingFileHandler(
            'logs/ml.log',
            maxBytes=10 * 1024 * 1024,
            backupCount=3
        )
        ml_handler.setLevel(logging.INFO)
        
        ml_formatter = logging.Formatter(
            '[%(asctime)s] ML - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        ml_handler.setFormatter(ml_formatter)
        ml_logger.addHandler(ml_handler)
    
    return ml_logger


class RequestLogger:
    """Middleware to log all HTTP requests"""
    
    def __init__(self, app):
        self.app = app
        self.logger = app.logger
    
    def __call__(self, environ, start_response):
        """Log request details"""
        method = environ.get('REQUEST_METHOD')
        path = environ.get('PATH_INFO')
        query = environ.get('QUERY_STRING')
        
        # Log request
        self.logger.info(f'Request: {method} {path}{"?" + query if query else ""}')
        
        return self.app(environ, start_response)


def log_error(logger, error, context=None):
    """
    Helper function to log errors with context
    
    Args:
        logger: Logger instance
        error: Exception object
        context: Optional dict with additional context
    """
    error_msg = f'Error: {type(error).__name__}: {str(error)}'
    
    if context:
        error_msg += f' | Context: {context}'
    
    logger.error(error_msg, exc_info=True)


def log_ml_prediction(logger, title, category_pred, priority_pred, confidence):
    """
    Log ML predictions for monitoring and debugging
    
    Args:
        logger: ML logger instance
        title: Issue title
        category_pred: Predicted category
        priority_pred: Predicted priority
        confidence: Prediction confidence score
    """
    logger.info(
        f'Prediction - Title: "{title[:50]}..." | '
        f'Category: {category_pred} | Priority: {priority_pred} | '
        f'Confidence: {confidence:.2f}'
    )


def log_priority_calculation(logger, issue_id, old_score, new_score, factors):
    """
    Log priority score calculations
    
    Args:
        logger: Logger instance
        issue_id: Issue ID
        old_score: Previous priority score
        new_score: New priority score
        factors: Dict of factor scores
    """
    logger.info(
        f'Priority Update - Issue #{issue_id} | '
        f'Score: {old_score:.2f} → {new_score:.2f} | '
        f'Factors: {factors}'
    )
