# Testing Guide

## Running Tests

### Install Test Dependencies
```bash
pip install pytest pytest-flask pytest-cov
```

### Run All Tests
```bash
pytest
```

### Run Specific Test File
```bash
pytest tests/test_validators.py
```

### Run with Coverage Report
```bash
pytest --cov=. --cov-report=html
```

### Run with Verbose Output
```bash
pytest -v
```

### Run Specific Test
```bash
pytest tests/test_validators.py::TestValidator::test_validate_email_valid
```

## Test Structure

```
tests/
├── conftest.py           # Pytest configuration and fixtures
├── test_validators.py    # Validation utilities tests
├── test_routes.py        # Route integration tests
└── README.md            # This file
```

## Writing New Tests

### Example Test Function
```python
def test_example(client):
    """Test description"""
    response = client.get('/endpoint')
    assert response.status_code == 200
    assert b'expected content' in response.data
```

### Available Fixtures
- `app`: Flask application instance
- `client`: Test client for making requests
- `auth_client`: Authenticated test client
- `runner`: CLI runner

## Best Practices

1. **Test naming**: Use descriptive names starting with `test_`
2. **Isolation**: Each test should be independent
3. **Assertions**: Use clear, specific assertions
4. **Coverage**: Aim for > 80% code coverage
5. **Documentation**: Add docstrings to test functions

## Continuous Integration

Add this to your CI/CD pipeline:
```yaml
- name: Run tests
  run: |
    pip install pytest pytest-flask pytest-cov
    pytest --cov=. --cov-report=xml
```

## Future Tests to Add

- [ ] ML model prediction tests
- [ ] Priority scoring algorithm tests
- [ ] Database operation tests
- [ ] Email sending tests
- [ ] File upload tests
- [ ] Admin functionality tests
- [ ] API endpoint tests
