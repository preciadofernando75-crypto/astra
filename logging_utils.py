"""
Logging and monitoring utilities for Astra
"""

import logging
from datetime import datetime
from functools import wraps
from flask import request
from database import APILog, db
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('astra.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger('astra')

def log_api_call(user_id, endpoint, method, status_code, response_time, tokens_used=0, error=None):
    """Log API call to database"""
    try:
        log = APILog(
            user_id=user_id,
            endpoint=endpoint,
            method=method,
            status_code=status_code,
            response_time=response_time,
            tokens_used=tokens_used,
            error_message=error
        )
        db.session.add(log)
        db.session.commit()
    except Exception as e:
        logger.error(f"Error logging API call: {str(e)}")

def log_request(f):
    """Decorator to log API requests"""
    @wraps(f)
    def decorated(*args, **kwargs):
        start_time = time.time()
        
        try:
            result = f(*args, **kwargs)
            response_time = time.time() - start_time
            
            status_code = 200
            if isinstance(result, tuple):
                status_code = result[1]
            
            logger.info(f"{request.method} {request.path} - {status_code} - {response_time:.3f}s")
            return result
        except Exception as e:
            response_time = time.time() - start_time
            logger.error(f"{request.method} {request.path} - Error: {str(e)} - {response_time:.3f}s")
            raise
    
    return decorated

def get_usage_stats(user_id, days=30):
    """Get usage statistics for a user"""
    from datetime import timedelta
    
    start_date = datetime.utcnow() - timedelta(days=days)
    
    logs = APILog.query.filter(
        APILog.user_id == user_id,
        APILog.created_at >= start_date
    ).all()
    
    total_calls = len(logs)
    total_tokens = sum(log.tokens_used for log in logs)
    avg_response_time = sum(log.response_time for log in logs) / total_calls if total_calls > 0 else 0
    error_count = len([log for log in logs if log.status_code >= 400])
    
    return {
        'total_calls': total_calls,
        'total_tokens': total_tokens,
        'avg_response_time': round(avg_response_time, 3),
        'error_count': error_count,
        'success_rate': round((total_calls - error_count) / total_calls * 100, 2) if total_calls > 0 else 0
    }
