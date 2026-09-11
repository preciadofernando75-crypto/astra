"""
Unit tests for authentication
"""

import unittest
from flask import Flask
from database import db, User, init_db
from astra_enhanced import app
from auth import hash_password, verify_password, generate_token, verify_token

class AuthTestCase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app = app
        self.client = app.test_client()
        
        with app.app_context():
            init_db(app)
    
    def test_register_user(self):
        """Test user registration"""
        response = self.client.post('/api/auth/register', json={
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpass123'
        })
        self.assertEqual(response.status_code, 201)
        data = response.get_json()
        self.assertIn('token', data)
        self.assertIn('user', data)
    
    def test_login_user(self):
        """Test user login"""
        # First register
        self.client.post('/api/auth/register', json={
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpass123'
        })
        
        # Then login
        response = self.client.post('/api/auth/login', json={
            'username': 'testuser',
            'password': 'testpass123'
        })
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn('token', data)
    
    def test_password_hashing(self):
        """Test password hashing"""
        password = 'test123'
        hashed = hash_password(password)
        self.assertTrue(verify_password(password, hashed))
        self.assertFalse(verify_password('wrong', hashed))
    
    def test_token_generation(self):
        """Test JWT token generation and verification"""
        token = generate_token(user_id=1)
        user_id = verify_token(token)
        self.assertEqual(user_id, 1)

if __name__ == '__main__':
    unittest.main()
