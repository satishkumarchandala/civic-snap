"""
Integration tests for main routes
"""
import pytest
from flask import session


class TestMainRoutes:
    """Test main application routes"""
    
    def test_home_page(self, client):
        """Test home page loads"""
        response = client.get('/')
        assert response.status_code == 200
        assert b'Urban Issue Reporter' in response.data or b'Issues' in response.data
    
    def test_login_page(self, client):
        """Test login page loads"""
        response = client.get('/login')
        assert response.status_code == 200
        assert b'login' in response.data.lower() or b'email' in response.data.lower()
    
    def test_register_page(self, client):
        """Test registration page loads"""
        response = client.get('/register')
        assert response.status_code == 200
        assert b'register' in response.data.lower() or b'sign up' in response.data.lower()
    
    def test_report_requires_login(self, client):
        """Test that report page requires authentication"""
        response = client.get('/report', follow_redirects=False)
        assert response.status_code == 302  # Redirect to login
    
    def test_user_registration(self, client):
        """Test user registration flow"""
        response = client.post('/register', data={
            'name': 'Test User',
            'email': 'newuser@example.com',
            'password': 'testpass123',
            'confirm_password': 'testpass123'
        }, follow_redirects=True)
        
        assert response.status_code == 200
    
    def test_user_login(self, client):
        """Test user login flow"""
        # First register
        client.post('/register', data={
            'name': 'Login Test',
            'email': 'logintest@example.com',
            'password': 'testpass123',
            'confirm_password': 'testpass123'
        })
        
        # Then login
        response = client.post('/login', data={
            'email': 'logintest@example.com',
            'password': 'testpass123'
        }, follow_redirects=True)
        
        assert response.status_code == 200
    
    def test_logout(self, auth_client):
        """Test logout functionality"""
        response = auth_client.get('/logout', follow_redirects=True)
        assert response.status_code == 200
        
        # Should redirect to login after logout
        response = auth_client.get('/report', follow_redirects=False)
        assert response.status_code == 302


class TestErrorHandling:
    """Test error handling"""
    
    def test_404_error(self, client):
        """Test 404 page"""
        response = client.get('/nonexistent-page')
        assert response.status_code == 404
    
    def test_405_error(self, client):
        """Test 405 method not allowed"""
        response = client.put('/')
        assert response.status_code == 405


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
