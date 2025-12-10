"""
Input validation utilities for Urban Issue Reporter
Provides reusable validation functions for forms and API inputs
"""
import re
from typing import Dict, List, Tuple, Any, Optional
from werkzeug.datastructures import FileStorage

class ValidationError(Exception):
    """Custom exception for validation errors"""
    pass


class Validator:
    """Collection of validation methods"""
    
    # Constants
    EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    PHONE_REGEX = re.compile(r'^\+?1?\d{9,15}$')
    
    VALID_CATEGORIES = ['road', 'electricity', 'water', 'sanitation', 'transport', 
                       'infrastructure', 'environment', 'others']
    VALID_PRIORITIES = ['low', 'medium', 'high', 'critical']
    VALID_STATUSES = ['pending', 'in-progress', 'resolved', 'rejected']
    VALID_ROLES = ['user', 'org_staff', 'org_admin', 'super_admin']
    
    ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB
    
    @staticmethod
    def validate_email(email: str) -> Tuple[bool, Optional[str]]:
        """
        Validate email address format
        
        Returns:
            (is_valid, error_message)
        """
        if not email:
            return False, "Email is required"
        
        if len(email) > 254:
            return False, "Email is too long"
        
        if not Validator.EMAIL_REGEX.match(email):
            return False, "Invalid email format"
        
        return True, None
    
    @staticmethod
    def validate_password(password: str, min_length: int = 6) -> Tuple[bool, Optional[str]]:
        """
        Validate password strength
        
        Args:
            password: Password to validate
            min_length: Minimum password length (default: 6)
        
        Returns:
            (is_valid, error_message)
        """
        if not password:
            return False, "Password is required"
        
        if len(password) < min_length:
            return False, f"Password must be at least {min_length} characters"
        
        if len(password) > 128:
            return False, "Password is too long (max 128 characters)"
        
        # Optional: Check for complexity
        # has_upper = any(c.isupper() for c in password)
        # has_lower = any(c.islower() for c in password)
        # has_digit = any(c.isdigit() for c in password)
        # if not (has_upper and has_lower and has_digit):
        #     return False, "Password must contain uppercase, lowercase, and digits"
        
        return True, None
    
    @staticmethod
    def validate_name(name: str, field_name: str = "Name") -> Tuple[bool, Optional[str]]:
        """Validate name field"""
        if not name or not name.strip():
            return False, f"{field_name} is required"
        
        if len(name.strip()) < 2:
            return False, f"{field_name} must be at least 2 characters"
        
        if len(name) > 100:
            return False, f"{field_name} is too long (max 100 characters)"
        
        return True, None
    
    @staticmethod
    def validate_phone(phone: str, required: bool = False) -> Tuple[bool, Optional[str]]:
        """Validate phone number"""
        if not phone:
            if required:
                return False, "Phone number is required"
            return True, None
        
        # Remove spaces and dashes
        cleaned = phone.replace(' ', '').replace('-', '').replace('(', '').replace(')', '')
        
        if not Validator.PHONE_REGEX.match(cleaned):
            return False, "Invalid phone number format"
        
        return True, None
    
    @staticmethod
    def validate_coordinates(latitude: Any, longitude: Any) -> Tuple[bool, Optional[str]]:
        """Validate GPS coordinates"""
        try:
            lat = float(latitude)
            lng = float(longitude)
        except (TypeError, ValueError):
            return False, "Coordinates must be valid numbers"
        
        if not (-90 <= lat <= 90):
            return False, "Latitude must be between -90 and 90"
        
        if not (-180 <= lng <= 180):
            return False, "Longitude must be between -180 and 180"
        
        # Check if coordinates are not default (0, 0)
        if lat == 0 and lng == 0:
            return False, "Please provide valid location coordinates"
        
        return True, None
    
    @staticmethod
    def validate_category(category: str) -> Tuple[bool, Optional[str]]:
        """Validate issue category"""
        if not category:
            return False, "Category is required"
        
        if category.lower() not in Validator.VALID_CATEGORIES:
            return False, f"Invalid category. Must be one of: {', '.join(Validator.VALID_CATEGORIES)}"
        
        return True, None
    
    @staticmethod
    def validate_priority(priority: str) -> Tuple[bool, Optional[str]]:
        """Validate priority level"""
        if not priority:
            return False, "Priority is required"
        
        if priority.lower() not in Validator.VALID_PRIORITIES:
            return False, f"Invalid priority. Must be one of: {', '.join(Validator.VALID_PRIORITIES)}"
        
        return True, None
    
    @staticmethod
    def validate_status(status: str) -> Tuple[bool, Optional[str]]:
        """Validate issue status"""
        if not status:
            return False, "Status is required"
        
        if status.lower() not in Validator.VALID_STATUSES:
            return False, f"Invalid status. Must be one of: {', '.join(Validator.VALID_STATUSES)}"
        
        return True, None
    
    @staticmethod
    def validate_text_field(text: str, field_name: str, min_length: int = 10, 
                           max_length: int = 5000) -> Tuple[bool, Optional[str]]:
        """Validate text fields (title, description, etc.)"""
        if not text or not text.strip():
            return False, f"{field_name} is required"
        
        text_length = len(text.strip())
        
        if text_length < min_length:
            return False, f"{field_name} must be at least {min_length} characters"
        
        if text_length > max_length:
            return False, f"{field_name} is too long (max {max_length} characters)"
        
        return True, None
    
    @staticmethod
    def validate_image_file(file: FileStorage) -> Tuple[bool, Optional[str]]:
        """Validate uploaded image file"""
        if not file or not file.filename:
            return True, None  # File is optional
        
        # Check file extension
        if '.' not in file.filename:
            return False, "File must have an extension"
        
        ext = file.filename.rsplit('.', 1)[1].lower()
        if ext not in Validator.ALLOWED_IMAGE_EXTENSIONS:
            return False, f"Invalid file type. Allowed: {', '.join(Validator.ALLOWED_IMAGE_EXTENSIONS)}"
        
        # Check file size (if available)
        file.seek(0, 2)  # Seek to end
        size = file.tell()
        file.seek(0)  # Reset to beginning
        
        if size > Validator.MAX_FILE_SIZE:
            return False, f"File too large. Maximum size: {Validator.MAX_FILE_SIZE // (1024*1024)}MB"
        
        return True, None
    
    @staticmethod
    def validate_issue_data(data: Dict) -> Tuple[bool, Dict[str, str]]:
        """
        Validate complete issue submission data
        
        Returns:
            (is_valid, errors_dict)
        """
        errors = {}
        
        # Validate title
        is_valid, error = Validator.validate_text_field(
            data.get('title', ''), 'Title', min_length=5, max_length=200
        )
        if not is_valid:
            errors['title'] = error
        
        # Validate description
        is_valid, error = Validator.validate_text_field(
            data.get('description', ''), 'Description', min_length=10, max_length=5000
        )
        if not is_valid:
            errors['description'] = error
        
        # Validate category
        is_valid, error = Validator.validate_category(data.get('category', ''))
        if not is_valid:
            errors['category'] = error
        
        # Validate priority
        is_valid, error = Validator.validate_priority(data.get('priority', ''))
        if not is_valid:
            errors['priority'] = error
        
        # Validate coordinates
        is_valid, error = Validator.validate_coordinates(
            data.get('latitude'), data.get('longitude')
        )
        if not is_valid:
            errors['location'] = error
        
        # Validate address
        if not data.get('address', '').strip():
            errors['address'] = "Address is required"
        elif len(data.get('address', '')) > 500:
            errors['address'] = "Address is too long (max 500 characters)"
        
        return len(errors) == 0, errors
    
    @staticmethod
    def validate_user_registration(data: Dict) -> Tuple[bool, Dict[str, str]]:
        """
        Validate user registration data
        
        Returns:
            (is_valid, errors_dict)
        """
        errors = {}
        
        # Validate name
        is_valid, error = Validator.validate_name(data.get('name', ''))
        if not is_valid:
            errors['name'] = error
        
        # Validate email
        is_valid, error = Validator.validate_email(data.get('email', ''))
        if not is_valid:
            errors['email'] = error
        
        # Validate password
        is_valid, error = Validator.validate_password(data.get('password', ''), min_length=6)
        if not is_valid:
            errors['password'] = error
        
        # Validate password confirmation
        if data.get('password') != data.get('confirm_password'):
            errors['confirm_password'] = "Passwords do not match"
        
        return len(errors) == 0, errors
    
    @staticmethod
    def sanitize_text(text: str) -> str:
        """
        Sanitize text input to prevent XSS
        Remove potentially dangerous characters
        """
        if not text:
            return ""
        
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', '', text)
        
        # Remove script tags content
        text = re.sub(r'<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>', '', text, flags=re.IGNORECASE)
        
        # Trim whitespace
        text = text.strip()
        
        return text
    
    @staticmethod
    def validate_rating(rating: Any, min_val: int = 1, max_val: int = 10) -> Tuple[bool, Optional[str]]:
        """Validate rating value (for severity voting)"""
        try:
            rating_int = int(rating)
        except (TypeError, ValueError):
            return False, f"Rating must be a number between {min_val} and {max_val}"
        
        if not (min_val <= rating_int <= max_val):
            return False, f"Rating must be between {min_val} and {max_val}"
        
        return True, None


def validate_or_error(validation_func, *args, **kwargs):
    """
    Helper function to validate and raise ValidationError if invalid
    
    Usage:
        validate_or_error(Validator.validate_email, email)
    """
    is_valid, error = validation_func(*args, **kwargs)
    if not is_valid:
        raise ValidationError(error)
    return True
