"""
Unit tests for validation utilities
"""
import pytest
from validators import Validator, ValidationError, validate_or_error


class TestValidator:
    """Test Validator class methods"""
    
    def test_validate_email_valid(self):
        """Test email validation with valid emails"""
        valid, error = Validator.validate_email("test@example.com")
        assert valid is True
        assert error is None
        
        valid, error = Validator.validate_email("user.name+tag@example.co.uk")
        assert valid is True
    
    def test_validate_email_invalid(self):
        """Test email validation with invalid emails"""
        valid, error = Validator.validate_email("")
        assert valid is False
        assert "required" in error.lower()
        
        valid, error = Validator.validate_email("invalid-email")
        assert valid is False
        
        valid, error = Validator.validate_email("@example.com")
        assert valid is False
    
    def test_validate_password(self):
        """Test password validation"""
        valid, error = Validator.validate_password("pass123")
        assert valid is True
        
        valid, error = Validator.validate_password("short")
        assert valid is False
        assert "6 characters" in error
        
        valid, error = Validator.validate_password("")
        assert valid is False
    
    def test_validate_coordinates(self):
        """Test GPS coordinates validation"""
        valid, error = Validator.validate_coordinates(40.7128, -74.0060)
        assert valid is True
        
        valid, error = Validator.validate_coordinates(0, 0)
        assert valid is False
        assert "valid location" in error.lower()
        
        valid, error = Validator.validate_coordinates(100, 0)
        assert valid is False
        
        valid, error = Validator.validate_coordinates(40.7128, 200)
        assert valid is False
    
    def test_validate_category(self):
        """Test category validation"""
        valid, error = Validator.validate_category("road")
        assert valid is True
        
        valid, error = Validator.validate_category("electricity")
        assert valid is True
        
        valid, error = Validator.validate_category("invalid_category")
        assert valid is False
        
        valid, error = Validator.validate_category("")
        assert valid is False
    
    def test_validate_priority(self):
        """Test priority validation"""
        valid, error = Validator.validate_priority("high")
        assert valid is True
        
        valid, error = Validator.validate_priority("critical")
        assert valid is True
        
        valid, error = Validator.validate_priority("invalid")
        assert valid is False
    
    def test_validate_rating(self):
        """Test rating validation"""
        valid, error = Validator.validate_rating(5)
        assert valid is True
        
        valid, error = Validator.validate_rating(10)
        assert valid is True
        
        valid, error = Validator.validate_rating(0)
        assert valid is False
        
        valid, error = Validator.validate_rating(11)
        assert valid is False
        
        valid, error = Validator.validate_rating("not a number")
        assert valid is False
    
    def test_validate_issue_data(self):
        """Test complete issue data validation"""
        valid_data = {
            'title': 'Test Issue Title',
            'description': 'This is a test description with enough characters',
            'category': 'road',
            'priority': 'medium',
            'latitude': 40.7128,
            'longitude': -74.0060,
            'address': '123 Main Street'
        }
        
        is_valid, errors = Validator.validate_issue_data(valid_data)
        assert is_valid is True
        assert len(errors) == 0
        
        # Test with invalid data
        invalid_data = {
            'title': 'Too',
            'description': 'Short',
            'category': 'invalid',
            'priority': 'wrong',
            'latitude': 0,
            'longitude': 0,
            'address': ''
        }
        
        is_valid, errors = Validator.validate_issue_data(invalid_data)
        assert is_valid is False
        assert len(errors) > 0
        assert 'title' in errors
        assert 'description' in errors
        assert 'category' in errors
    
    def test_validate_user_registration(self):
        """Test user registration data validation"""
        valid_data = {
            'name': 'John Doe',
            'email': 'john@example.com',
            'password': 'password123',
            'confirm_password': 'password123'
        }
        
        is_valid, errors = Validator.validate_user_registration(valid_data)
        assert is_valid is True
        assert len(errors) == 0
        
        # Test password mismatch
        invalid_data = valid_data.copy()
        invalid_data['confirm_password'] = 'different'
        
        is_valid, errors = Validator.validate_user_registration(invalid_data)
        assert is_valid is False
        assert 'confirm_password' in errors
    
    def test_sanitize_text(self):
        """Test text sanitization"""
        clean = Validator.sanitize_text("<script>alert('xss')</script>Hello")
        assert "<script>" not in clean
        assert "Hello" in clean
        
        clean = Validator.sanitize_text("  Whitespace test  ")
        assert clean == "Whitespace test"
    
    def test_validate_or_error_helper(self):
        """Test validate_or_error helper function"""
        # Should not raise for valid data
        validate_or_error(Validator.validate_email, "test@example.com")
        
        # Should raise ValidationError for invalid data
        with pytest.raises(ValidationError):
            validate_or_error(Validator.validate_email, "invalid-email")


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
