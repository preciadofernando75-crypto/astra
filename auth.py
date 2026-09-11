"""
Authentication and authorization utilities for Astra
"""

from functools import wraps
from flask import request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import jwt
import os
from database import User, db

SECRET_KEY = os.getenv('SECRET_KEY', 'astra-secret-key-change-in-production')

def hash_password(password):
    """Hash a password"""
    return generate_password_hash(password)

def verify_password(password, hash):
    """Verify a password against its hash"""
    return check_password_hash(hash, password)

def generate_token(user_id, expires_in=86400):
    """Generate JWT token for user"""
    payload = {
        'user_id': user_id,
        'exp': datetime.utcnow() + timedelta(seconds=expires_in),
        'iat': datetime.utcnow()
    }
    return jwt.encode(payload, SECRET_KEY, algorithm='HS256')

def verify_token(token):
    """Verify JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return payload.get('user_id')
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def token_required(f):
    """Decorator to require valid JWT token"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(" ")[1]
            except IndexError:
                return jsonify({'error': 'Invalid token format'}), 401
        
        if not token:
            return jsonify({'error': 'Token is missing'}), 401
        
        user_id = verify_token(token)
        if not user_id:
            return jsonify({'error': 'Invalid or expired token'}), 401
        
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        return f(user, *args, **kwargs)
    
    return decorated

def role_required(required_role):
    """Decorator to require specific role"""
    def decorator(f):
        @wraps(f)
        def decorated(user, *args, **kwargs):
            if user.role != required_role and user.role != 'admin':
                return jsonify({'error': 'Insufficient permissions'}), 403
            return f(user, *args, **kwargs)
        return decorated
    return decorator

def api_key_required(f):
    """Decorator to require valid API key"""
    @wraps(f)
    def decorated(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        
        if not api_key:
            return jsonify({'error': 'API key is missing'}), 401
        
        user = User.query.filter_by(api_key=api_key).first()
        if not user:
            return jsonify({'error': 'Invalid API key'}), 401
        
        return f(user, *args, **kwargs)
    
    return decorated
