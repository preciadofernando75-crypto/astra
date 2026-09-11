"""
Astra - Advanced AI Assistant (Enhanced Version)
Comprehensive AI framework with authentication, file processing, and monitoring
"""

import os
from dotenv import load_dotenv
import openai
from flask import Flask, request, jsonify
from flask_cors import CORS
from functools import wraps
import time

# Import custom modules
from database import db, User, Conversation, Message, UploadedFile, init_db
from auth import token_required, role_required, api_key_required, hash_password, generate_token, verify_token
from personas import get_persona, list_personas
from file_handler import save_uploaded_file, extract_text_from_file
from logging_utils import log_api_call, log_request, get_usage_stats, logger

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
    'DATABASE_URL', 
    'sqlite:///astra.db'
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'astra-secret-key')

# Initialize Database
init_db(app)

# Configure OpenAI
openai.api_key = os.getenv('OPENAI_API_KEY')

# ==================== AUTHENTICATION ENDPOINTS ====================

@app.route('/api/auth/register', methods=['POST'])
@log_request
def register():
    """Register a new user"""
    try:
        data = request.json
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        
        if not all([username, email, password]):
            return jsonify({'error': 'Missing required fields'}), 400
        
        if User.query.filter_by(username=username).first():
            return jsonify({'error': 'Username already exists'}), 409
        
        if User.query.filter_by(email=email).first():
            return jsonify({'error': 'Email already exists'}), 409
        
        user = User(
            username=username,
            email=email,
            password_hash=hash_password(password)
        )
        
        db.session.add(user)
        db.session.commit()
        
        token = generate_token(user.id)
        
        return jsonify({
            'message': 'User registered successfully',
            'token': token,
            'user': user.to_dict()
        }), 201
    
    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/auth/login', methods=['POST'])
@log_request
def login():
    """Login user"""
    try:
        data = request.json
        username = data.get('username')
        password = data.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if not user or not user.password_hash:
            return jsonify({'error': 'Invalid credentials'}), 401
        
        from werkzeug.security import check_password_hash
        if not check_password_hash(user.password_hash, password):
            return jsonify({'error': 'Invalid credentials'}), 401
        
        token = generate_token(user.id)
        
        return jsonify({
            'message': 'Login successful',
            'token': token,
            'user': user.to_dict()
        }), 200
    
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        return jsonify({'error': str(e)}), 500

# ==================== CONVERSATION ENDPOINTS ====================

@app.route('/api/conversations', methods=['GET'])
@token_required
@log_request
def get_conversations(user):
    """Get all conversations for user"""
    try:
        conversations = Conversation.query.filter_by(user_id=user.id).all()
        return jsonify([conv.to_dict() for conv in conversations]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/conversations', methods=['POST'])
@token_required
@log_request
def create_conversation(user):
    """Create a new conversation"""
    try:
        data = request.json
        
        conversation = Conversation(
            user_id=user.id,
            title=data.get('title', 'New Conversation'),
            model=data.get('model', 'gpt-4'),
            persona=data.get('persona', 'general')
        )
        
        db.session.add(conversation)
        db.session.commit()
        
        return jsonify(conversation.to_dict()), 201
    
    except Exception as e:
        logger.error(f"Conversation creation error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/conversations/<int:conv_id>/chat', methods=['POST'])
@token_required
@log_request
def chat(user, conv_id):
    """Send message in conversation"""
    start_time = time.time()
    try:
        data = request.json
        user_message = data.get('message', '')
        
        if not user_message:
            return jsonify({'error': 'No message provided'}), 400
        
        # Get conversation
        conversation = Conversation.query.filter_by(
            id=conv_id,
            user_id=user.id
        ).first()
        
        if not conversation:
            return jsonify({'error': 'Conversation not found'}), 404
        
        # Add user message to database
        user_msg = Message(
            conversation_id=conv_id,
            role='user',
            content=user_message
        )
        db.session.add(user_msg)
        db.session.commit()
        
        # Get persona configuration
        persona = get_persona(conversation.persona)
        
        # Prepare messages for API
        messages = [
            {'role': 'system', 'content': persona['system_prompt']}
        ]
        
        # Add conversation history
        history = Message.query.filter_by(conversation_id=conv_id).all()
        for msg in history[:-1]:  # Exclude the message we just added
            messages.append({'role': msg.role, 'content': msg.content})
        
        messages.append({'role': 'user', 'content': user_message})
        
        # Call OpenAI API
        response = openai.ChatCompletion.create(
            model=conversation.model,
            messages=messages,
            temperature=persona['temperature'],
            max_tokens=persona['max_tokens']
        )
        
        assistant_message = response.choices[0].message.content
        tokens_used = response.usage.total_tokens
        
        # Save assistant response
        assistant_msg = Message(
            conversation_id=conv_id,
            role='assistant',
            content=assistant_message,
            tokens_used=tokens_used
        )
        db.session.add(assistant_msg)
        db.session.commit()
        
        response_time = time.time() - start_time
        log_api_call(user.id, '/api/chat', 'POST', 200, response_time, tokens_used)
        
        return jsonify({
            'response': assistant_message,
            'tokens_used': tokens_used,
            'conversation_id': conv_id
        }), 200
    
    except Exception as e:
        response_time = time.time() - start_time
        log_api_call(user.id, '/api/chat', 'POST', 500, response_time, error=str(e))
        logger.error(f"Chat error: {str(e)}")
        return jsonify({'error': str(e)}), 500

# ==================== FILE HANDLING ENDPOINTS ====================

@app.route('/api/files/upload', methods=['POST'])
@token_required
@log_request
def upload_file(user):
    """Upload and process a file"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        
        filepath, error = save_uploaded_file(file, user.id)
        if error:
            return jsonify({'error': error}), 400
        
        # Extract content
        content = extract_text_from_file(filepath)
        
        # Save to database
        from file_handler import get_file_type
        uploaded_file = UploadedFile(
            user_id=user.id,
            filename=file.filename,
            file_path=filepath,
            file_type=get_file_type(file.filename),
            file_size=len(content.encode('utf-8'))
        )
        
        db.session.add(uploaded_file)
        db.session.commit()
        
        return jsonify({
            'message': 'File uploaded successfully',
            'file_id': uploaded_file.id,
            'filename': file.filename,
            'file_type': uploaded_file.file_type,
            'content_preview': content[:500] + '...' if len(content) > 500 else content
        }), 201
    
    except Exception as e:
        logger.error(f"File upload error: {str(e)}")
        return jsonify({'error': str(e)}), 500

# ==================== PERSONAS ENDPOINTS ====================

@app.route('/api/personas', methods=['GET'])
@log_request
def get_personas():
    """Get available personas"""
    return jsonify(list_personas()), 200

# ==================== ANALYTICS ENDPOINTS ====================

@app.route('/api/analytics/usage', methods=['GET'])
@token_required
@log_request
def get_user_usage(user):
    """Get usage statistics for user"""
    try:
        days = request.args.get('days', 30, type=int)
        stats = get_usage_stats(user.id, days)
        return jsonify(stats), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ==================== ADMIN ENDPOINTS ====================

@app.route('/api/admin/users', methods=['GET'])
@token_required
@role_required('admin')
@log_request
def get_all_users(user):
    """Get all users (admin only)"""
    try:
        users = User.query.all()
        return jsonify([u.to_dict() for u in users]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ==================== HEALTH CHECK ====================

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'name': 'Astra Enhanced',
        'version': '2.0.0'
    }), 200

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5000)
