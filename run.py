"""
Main application runner
Supports both development and production modes
"""
import os
import sys
from flask import Flask
from dotenv import load_dotenv

# Add project root to path
sys.path.insert(0, os.path.dirname(__file__))

# Load environment variables
load_dotenv()

def create_app(config_name=None):
    """Application factory function"""
    from config import get_config
    from app.core import error_handlers
    from app.core.logging_config import setup_logging
    from app.routes import init_routes
    from app.models.models import init_db
    import json
    
    # Create Flask app
    app = Flask(__name__,
                template_folder='templates',
                static_folder='static')
    
    # Load configuration
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    
    config_class = get_config(config_name)
    app.config.from_object(config_class)
    
    # Ensure required directories exist
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['ML_MODELS_DIR'], exist_ok=True)
    os.makedirs(app.config['LOG_DIR'], exist_ok=True)
    
    # Setup logging
    setup_logging(app)
    
    # Initialize database
    init_db()
    
    # Register error handlers
    error_handlers.register_error_handlers(app)
    
    # Add custom Jinja2 filters
    @app.template_filter('from_json')
    def from_json_filter(value):
        """Convert JSON string to Python object"""
        try:
            if isinstance(value, str):
                return json.loads(value)
            return value
        except (ValueError, TypeError):
            return {}
    
    # Register routes
    init_routes(app)
    
    app.logger.info(f'Flask application initialized in {config_name} mode')
    
    return app


if __name__ == '__main__':
    app = create_app()
    
    # Get host and port from config or environment
    host = os.environ.get('HOST', app.config.get('HOST', '0.0.0.0'))
    port = int(os.environ.get('PORT', app.config.get('PORT', 5000)))
    debug = app.config.get('DEBUG', False)
    
    print(f"🚀 Starting Urban Issue Reporter on http://{host}:{port}")
    print(f"📝 Environment: {os.environ.get('FLASK_ENV', 'development')}")
    print(f"🔧 Debug mode: {debug}")
    
    app.run(host=host, port=port, debug=debug)
