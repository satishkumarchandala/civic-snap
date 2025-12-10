"""
Rate limiting middleware for Urban Issue Reporter
Protects against abuse and DDoS attacks
"""
from functools import wraps
from flask import request, jsonify
from collections import defaultdict
from datetime import datetime, timedelta
import time


class RateLimiter:
    """
    Simple in-memory rate limiter
    For production, consider using Redis-based solution (Flask-Limiter)
    """
    
    def __init__(self):
        # Store: {ip_address: {endpoint: [(timestamp, count)]}}
        self.requests = defaultdict(lambda: defaultdict(list))
        self.cleanup_interval = 300  # Clean old entries every 5 minutes
        self.last_cleanup = time.time()
    
    def _cleanup_old_entries(self):
        """Remove old request records to prevent memory bloat"""
        current_time = time.time()
        
        if current_time - self.last_cleanup < self.cleanup_interval:
            return
        
        cutoff_time = datetime.now() - timedelta(hours=2)
        
        for ip in list(self.requests.keys()):
            for endpoint in list(self.requests[ip].keys()):
                self.requests[ip][endpoint] = [
                    (ts, count) for ts, count in self.requests[ip][endpoint]
                    if ts > cutoff_time
                ]
                
                if not self.requests[ip][endpoint]:
                    del self.requests[ip][endpoint]
            
            if not self.requests[ip]:
                del self.requests[ip]
        
        self.last_cleanup = current_time
    
    def is_allowed(self, ip_address: str, endpoint: str, limit: int, window: int) -> tuple:
        """
        Check if request is allowed based on rate limit
        
        Args:
            ip_address: Client IP address
            endpoint: Endpoint identifier
            limit: Maximum number of requests
            window: Time window in seconds
        
        Returns:
            (is_allowed, remaining_requests, reset_time)
        """
        self._cleanup_old_entries()
        
        now = datetime.now()
        window_start = now - timedelta(seconds=window)
        
        # Get requests for this IP and endpoint
        endpoint_requests = self.requests[ip_address][endpoint]
        
        # Filter requests within the time window
        recent_requests = [ts for ts, _ in endpoint_requests if ts > window_start]
        request_count = len(recent_requests)
        
        if request_count >= limit:
            # Calculate when the oldest request will expire
            oldest_request = min(recent_requests) if recent_requests else now
            reset_time = oldest_request + timedelta(seconds=window)
            return False, 0, reset_time
        
        # Add current request
        self.requests[ip_address][endpoint].append((now, 1))
        
        remaining = limit - request_count - 1
        reset_time = now + timedelta(seconds=window)
        
        return True, remaining, reset_time


# Global rate limiter instance
rate_limiter = RateLimiter()


def rate_limit(limit: int = 100, window: int = 3600, key_func=None):
    """
    Rate limiting decorator
    
    Args:
        limit: Maximum number of requests (default: 100)
        window: Time window in seconds (default: 3600 = 1 hour)
        key_func: Optional function to generate custom key (default: uses IP)
    
    Usage:
        @rate_limit(limit=30, window=60)  # 30 requests per minute
        def my_route():
            pass
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Get client identifier
            if key_func:
                client_id = key_func()
            else:
                client_id = request.remote_addr or 'unknown'
            
            # Get endpoint identifier
            endpoint = request.endpoint or request.path
            
            # Check rate limit
            is_allowed, remaining, reset_time = rate_limiter.is_allowed(
                client_id, endpoint, limit, window
            )
            
            if not is_allowed:
                # Return 429 Too Many Requests
                reset_timestamp = int(reset_time.timestamp())
                
                if request.is_json or request.path.startswith('/api/'):
                    return jsonify({
                        'success': False,
                        'error': 'Rate Limit Exceeded',
                        'message': f'Too many requests. Limit: {limit} per {window}s',
                        'retry_after': reset_timestamp
                    }), 429
                
                return jsonify({
                    'error': 'Too many requests',
                    'retry_after': reset_timestamp
                }), 429
            
            # Add rate limit headers to response
            response = f(*args, **kwargs)
            
            # If response is a tuple (response, status_code), handle it
            if isinstance(response, tuple):
                actual_response = response[0]
                status_code = response[1] if len(response) > 1 else 200
            else:
                actual_response = response
                status_code = 200
            
            # Add headers if response has headers attribute
            if hasattr(actual_response, 'headers'):
                actual_response.headers['X-RateLimit-Limit'] = str(limit)
                actual_response.headers['X-RateLimit-Remaining'] = str(remaining)
                actual_response.headers['X-RateLimit-Reset'] = str(int(reset_time.timestamp()))
            
            return response
        
        return decorated_function
    return decorator


# Predefined rate limit decorators for common use cases

def strict_rate_limit(f):
    """Strict rate limit: 30 requests per hour"""
    return rate_limit(limit=30, window=3600)(f)


def standard_rate_limit(f):
    """Standard rate limit: 100 requests per hour"""
    return rate_limit(limit=100, window=3600)(f)


def lenient_rate_limit(f):
    """Lenient rate limit: 300 requests per hour"""
    return rate_limit(limit=300, window=3600)(f)


def api_rate_limit(f):
    """API rate limit: 1000 requests per hour"""
    return rate_limit(limit=1000, window=3600)(f)


def auth_rate_limit(f):
    """Authentication rate limit: 5 attempts per minute"""
    return rate_limit(limit=5, window=60)(f)


# Usage examples in routes:
"""
from rate_limiter import rate_limit, strict_rate_limit, auth_rate_limit

@app.route('/api/data')
@rate_limit(limit=50, window=60)  # 50 requests per minute
def get_data():
    return jsonify({'data': 'example'})

@app.route('/login', methods=['POST'])
@auth_rate_limit  # 5 attempts per minute
def login():
    # Login logic
    pass

@app.route('/report', methods=['POST'])
@strict_rate_limit  # 30 requests per hour
def report_issue():
    # Report logic
    pass
"""
