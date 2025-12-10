"""
Error handlers and middleware for Urban Issue Reporter
Provides global error handling and custom error pages
"""
from flask import render_template, jsonify, request
from werkzeug.exceptions import HTTPException
import traceback


def register_error_handlers(app):
    """Register all error handlers with the Flask app"""
    
    @app.errorhandler(400)
    def bad_request(error):
        """Handle 400 Bad Request errors"""
        app.logger.warning(f'Bad Request: {request.url} - {str(error)}')
        
        if request.is_json or request.path.startswith('/api/'):
            return jsonify({
                'success': False,
                'error': 'Bad Request',
                'message': 'The request could not be understood by the server'
            }), 400
        
        return render_template('errors/400.html', error=error), 400
    
    @app.errorhandler(401)
    def unauthorized(error):
        """Handle 401 Unauthorized errors"""
        app.logger.warning(f'Unauthorized access attempt: {request.url}')
        
        if request.is_json or request.path.startswith('/api/'):
            return jsonify({
                'success': False,
                'error': 'Unauthorized',
                'message': 'Authentication required'
            }), 401
        
        return render_template('errors/401.html', error=error), 401
    
    @app.errorhandler(403)
    def forbidden(error):
        """Handle 403 Forbidden errors"""
        app.logger.warning(f'Forbidden access attempt: {request.url}')
        
        if request.is_json or request.path.startswith('/api/'):
            return jsonify({
                'success': False,
                'error': 'Forbidden',
                'message': 'You do not have permission to access this resource'
            }), 403
        
        return render_template('errors/403.html', error=error), 403
    
    @app.errorhandler(404)
    def not_found(error):
        """Handle 404 Not Found errors"""
        app.logger.info(f'404 Not Found: {request.url}')
        
        if request.is_json or request.path.startswith('/api/'):
            return jsonify({
                'success': False,
                'error': 'Not Found',
                'message': 'The requested resource was not found'
            }), 404
        
        return render_template('errors/404.html', error=error), 404
    
    @app.errorhandler(405)
    def method_not_allowed(error):
        """Handle 405 Method Not Allowed errors"""
        app.logger.warning(f'Method Not Allowed: {request.method} {request.url}')
        
        if request.is_json or request.path.startswith('/api/'):
            return jsonify({
                'success': False,
                'error': 'Method Not Allowed',
                'message': f'The {request.method} method is not allowed for this endpoint'
            }), 405
        
        return render_template('errors/405.html', error=error), 405
    
    @app.errorhandler(413)
    def request_entity_too_large(error):
        """Handle 413 Request Entity Too Large errors"""
        app.logger.warning(f'File too large: {request.url}')
        
        if request.is_json or request.path.startswith('/api/'):
            return jsonify({
                'success': False,
                'error': 'File Too Large',
                'message': 'The uploaded file exceeds the maximum size limit (16MB)'
            }), 413
        
        return render_template('errors/413.html', error=error), 413
    
    @app.errorhandler(429)
    def rate_limit_exceeded(error):
        """Handle 429 Too Many Requests errors"""
        app.logger.warning(f'Rate limit exceeded: {request.remote_addr} - {request.url}')
        
        if request.is_json or request.path.startswith('/api/'):
            return jsonify({
                'success': False,
                'error': 'Rate Limit Exceeded',
                'message': 'Too many requests. Please try again later.'
            }), 429
        
        return render_template('errors/429.html', error=error), 429
    
    @app.errorhandler(500)
    def internal_server_error(error):
        """Handle 500 Internal Server Error"""
        app.logger.error(f'Internal Server Error: {request.url}')
        app.logger.error(traceback.format_exc())
        
        if request.is_json or request.path.startswith('/api/'):
            return jsonify({
                'success': False,
                'error': 'Internal Server Error',
                'message': 'An unexpected error occurred. Please try again later.'
            }), 500
        
        return render_template('errors/500.html', error=error), 500
    
    @app.errorhandler(503)
    def service_unavailable(error):
        """Handle 503 Service Unavailable errors"""
        app.logger.error(f'Service Unavailable: {request.url}')
        
        if request.is_json or request.path.startswith('/api/'):
            return jsonify({
                'success': False,
                'error': 'Service Unavailable',
                'message': 'The service is temporarily unavailable. Please try again later.'
            }), 503
        
        return render_template('errors/503.html', error=error), 503
    
    @app.errorhandler(Exception)
    def handle_unexpected_error(error):
        """Handle any unexpected errors"""
        app.logger.critical(f'Unexpected error: {type(error).__name__}: {str(error)}')
        app.logger.critical(traceback.format_exc())
        
        # Don't expose internal error details in production
        if app.config.get('DEBUG'):
            error_message = str(error)
        else:
            error_message = 'An unexpected error occurred'
        
        if request.is_json or request.path.startswith('/api/'):
            return jsonify({
                'success': False,
                'error': 'Unexpected Error',
                'message': error_message
            }), 500
        
        return render_template('errors/500.html', error=error), 500


class RateLimitExceeded(Exception):
    """Custom exception for rate limiting"""
    pass


def create_error_response(error_code: int, message: str, details: dict = None):
    """
    Create standardized error response
    
    Args:
        error_code: HTTP status code
        message: Error message
        details: Optional additional details
    
    Returns:
        JSON response tuple (response, status_code)
    """
    response = {
        'success': False,
        'error': message,
        'code': error_code
    }
    
    if details:
        response['details'] = details
    
    return jsonify(response), error_code
