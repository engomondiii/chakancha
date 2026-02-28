"""
Custom middleware for logging all API requests and responses
"""

import logging
import time
import json

logger = logging.getLogger('chatbot')


class RequestLoggingMiddleware:
    """
    Logs all incoming API requests and outgoing responses
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Skip logging for static files and admin
        if request.path.startswith('/static/') or request.path.startswith('/admin/'):
            return self.get_response(request)
        
        # Start timer
        start_time = time.time()
        
        # Log request
        logger.info(f"→ {request.method} {request.path} from {request.META.get('REMOTE_ADDR')}")
        
        # Process request
        response = self.get_response(request)
        
        # Calculate duration
        duration = time.time() - start_time
        duration_ms = int(duration * 1000)
        
        # Log response
        logger.info(
            f"← {request.method} {request.path} "
            f"Status: {response.status_code} "
            f"Duration: {duration_ms}ms"
        )
        
        # Add response time header
        response['X-Response-Time'] = f"{duration_ms}ms"
        
        return response


class CORSLoggingMiddleware:
    """
    Logs CORS requests for debugging
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        if request.method == 'OPTIONS':
            logger.debug(
                f"CORS preflight: {request.META.get('HTTP_ORIGIN')} → {request.path}"
            )
        
        response = self.get_response(request)
        return response