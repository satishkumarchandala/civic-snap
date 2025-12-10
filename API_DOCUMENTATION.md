# 🔌 API Documentation - Urban Issue Reporter

## Base URL
```
Development: http://localhost:5000
Production: https://your-domain.com
```

## Authentication
Most endpoints require authentication via session cookies. Admin endpoints require admin role.

### Response Format
All API responses follow this format:
```json
{
  "success": true|false,
  "data": {...},
  "message": "Optional message",
  "error": "Error details (if failed)"
}
```

---

## 📍 Main Routes

### GET /
**Description:** Home page with issue listing and statistics

**Query Parameters:**
- `category` (optional): Filter by category (road, electricity, water, etc.)
- `status` (optional): Filter by status (pending, in-progress, resolved)
- `search` (optional): Search in title and description

**Response:** HTML page

---

### GET /report
**Description:** Issue reporting form

**Authentication:** Required

**Response:** HTML form

---

### POST /report
**Description:** Submit a new issue

**Authentication:** Required

**Request Body (form-data):**
```json
{
  "title": "string (5-200 chars)",
  "description": "string (10-5000 chars)",
  "category": "road|electricity|water|sanitation|transport|infrastructure|environment|others",
  "priority": "low|medium|high|critical",
  "latitude": "float (-90 to 90)",
  "longitude": "float (-180 to 180)",
  "address": "string (max 500 chars)",
  "image": "file (optional, max 16MB, png|jpg|jpeg|gif)"
}
```

**Validation:**
- Title: 5-200 characters
- Description: 10-5000 characters
- Category: Must be valid category
- Priority: Must be valid priority level
- Coordinates: Valid GPS coordinates (not 0,0)
- Image: Optional, must be image file, max 16MB

**Success Response:**
```json
{
  "success": true,
  "issue_id": 123,
  "message": "Issue reported successfully"
}
```

**Error Response:**
```json
{
  "success": false,
  "errors": {
    "title": "Title must be at least 5 characters",
    "location": "Please provide valid location coordinates"
  }
}
```

---

### GET /issue/<int:issue_id>
**Description:** View detailed issue information

**Parameters:**
- `issue_id`: Issue ID (required)

**Response:** HTML page with issue details

---

### GET /issues_map
**Description:** Interactive map view of all issues

**Authentication:** Required

**Response:** HTML page with map

---

## 🔐 Authentication Routes

### GET /login
**Description:** Login page

**Response:** HTML login form

---

### POST /login
**Description:** User login

**Request Body (form-data):**
```json
{
  "email": "string (valid email)",
  "password": "string"
}
```

**Success Response:** Redirect to home page

**Error Response:** Redirect to login with error message

**Rate Limit:** 5 attempts per minute

---

### GET /register
**Description:** Registration page

**Response:** HTML registration form

---

### POST /register
**Description:** User registration

**Request Body (form-data):**
```json
{
  "name": "string (2-100 chars)",
  "email": "string (valid email, unique)",
  "password": "string (min 6 chars)",
  "confirm_password": "string (must match password)"
}
```

**Validation:**
- Name: 2-100 characters
- Email: Valid format, not already registered
- Password: Minimum 6 characters
- Passwords must match

**Success Response:** Redirect to login

**Error Response:** Redirect to register with error message

**Rate Limit:** 30 requests per hour

---

### GET /logout
**Description:** User logout

**Authentication:** Required

**Response:** Redirect to login page

---

## 👤 Profile Routes

### GET /profile
**Description:** View user profile

**Authentication:** Required

**Response:** HTML profile page

---

### POST /profile
**Description:** Update user profile

**Authentication:** Required

**Request Body (form-data):**
```json
{
  "name": "string (optional)",
  "phone": "string (optional, valid phone number)",
  "bio": "string (optional, max 500 chars)",
  "location": "string (optional)",
  "profile_picture": "file (optional, max 16MB)"
}
```

**Success Response:** Redirect to profile

**Error Response:** Redirect to profile with error message

---

## 🔧 Admin Routes

### GET /admin
**Description:** Admin dashboard

**Authentication:** Required (admin role)

**Response:** HTML admin dashboard

---

### GET /admin/organizations
**Description:** Manage organizations

**Authentication:** Required (super_admin role)

**Response:** HTML organizations page

---

### POST /admin/organizations
**Description:** Create new organization

**Authentication:** Required (super_admin role)

**Request Body (form-data):**
```json
{
  "name": "string (unique)",
  "category": "string",
  "description": "string (optional)"
}
```

**Success Response:** Redirect to organizations page

---

### POST /admin/update_issue/<int:issue_id>
**Description:** Update issue status or assignment

**Authentication:** Required (admin role)

**Request Body (form-data):**
```json
{
  "status": "pending|in-progress|resolved|rejected (optional)",
  "assigned_to": "int (user_id, optional)",
  "admin_response": "string (optional)"
}
```

**Success Response:** Redirect to admin dashboard

---

## 🤖 ML Routes

### GET /admin/ml
**Description:** ML model management dashboard

**Authentication:** Required (admin role)

**Response:** HTML ML dashboard

---

### POST /admin/ml/train
**Description:** Train ML models with current data

**Authentication:** Required (admin role)

**Request Body:** None

**Success Response:** Redirect to ML dashboard

**Note:** Training requires at least 10 issues in database

---

### POST /admin/ml/predict
**Description:** Test ML prediction with sample text

**Authentication:** Required (admin role)

**Request Body (form-data):**
```json
{
  "title": "string",
  "description": "string"
}
```

**Success Response:**
```json
{
  "category": {
    "category": "electricity",
    "confidence": 0.95,
    "method": "ml_model"
  },
  "priority": {
    "priority": "high",
    "confidence": 0.87,
    "method": "ml_model"
  },
  "explanation": {
    "category_reasoning": ["Found electricity keywords: power, light"],
    "priority_reasoning": ["Found high urgency indicators: urgent, broken"]
  }
}
```

---

### POST /admin/ml/batch-update
**Description:** Update all existing issues with ML predictions

**Authentication:** Required (admin role)

**Request Body:** None

**Success Response:** Redirect to ML dashboard with count

---

### GET /api/ml/predict
**Description:** Get ML predictions (AJAX endpoint)

**Authentication:** Optional

**Query Parameters:**
- `title`: Issue title
- `description`: Issue description

**Success Response:**
```json
{
  "category": {
    "category": "road",
    "confidence": 0.92
  },
  "priority": {
    "priority": "medium",
    "confidence": 0.78
  }
}
```

**Rate Limit:** 100 requests per hour

---

## 📊 Priority Routes

### GET /priority/dashboard
**Description:** Priority dashboard showing high-priority issues

**Authentication:** Required

**Response:** HTML priority dashboard

---

### POST /api/priority/calculate/<int:issue_id>
**Description:** Calculate/recalculate priority for an issue

**Authentication:** Required

**Parameters:**
- `issue_id`: Issue ID (required)

**Success Response:**
```json
{
  "success": true,
  "priority_data": {
    "final_score": 7.85,
    "priority_level": "high",
    "factor_scores": {
      "severity": 8.5,
      "location": 9.0,
      "reports_count": 6.0,
      "age": 5.0,
      "safety_impact": 7.0
    },
    "duplicate_count": 4
  }
}
```

**Rate Limit:** 100 requests per hour

---

### POST /api/priority/vote
**Description:** Submit citizen severity vote

**Authentication:** Required

**Request Body (JSON):**
```json
{
  "issue_id": 123,
  "severity_rating": 8
}
```

**Validation:**
- `severity_rating`: Integer between 1 and 10

**Success Response:**
```json
{
  "success": true,
  "message": "Vote submitted successfully"
}
```

**Rate Limit:** 30 requests per hour

---

### POST /api/priority/mark-duplicate
**Description:** Mark two issues as duplicates

**Authentication:** Required

**Request Body (JSON):**
```json
{
  "issue_id": 123,
  "duplicate_issue_id": 456
}
```

**Success Response:**
```json
{
  "success": true,
  "message": "Issues marked as duplicates"
}
```

---

### POST /api/priority/batch-calculate
**Description:** Recalculate priorities for all issues

**Authentication:** Required (admin role)

**Request Body:** None

**Success Response:**
```json
{
  "success": true,
  "updated_count": 250,
  "message": "Priorities recalculated for 250 issues"
}
```

---

### GET /api/priority/stats
**Description:** Get priority statistics

**Authentication:** Optional

**Success Response:**
```json
{
  "success": true,
  "stats": {
    "critical": 15,
    "high": 42,
    "medium": 98,
    "low": 34,
    "total": 189,
    "avg_score": 6.2
  }
}
```

---

## 💬 Comment Routes

### POST /issue/<int:issue_id>/comment
**Description:** Add comment to an issue

**Authentication:** Required

**Parameters:**
- `issue_id`: Issue ID (required)

**Request Body (form-data):**
```json
{
  "comment": "string (10-2000 chars)"
}
```

**Success Response:** Redirect to issue detail page

**Rate Limit:** 30 requests per hour

---

## 📁 Upload Routes

### GET /uploads/<filename>
**Description:** Serve uploaded images

**Parameters:**
- `filename`: Image filename

**Response:** Image file

**Note:** Images are served from the `uploads/` directory

---

## 🔒 Security Features

### Rate Limiting
- **Authentication endpoints:** 5 attempts per minute
- **Issue submission:** 30 per hour
- **API endpoints:** 100 per hour
- **Admin operations:** 300 per hour

### Input Validation
All form inputs are validated:
- Email format validation
- Password strength requirements
- Text length constraints
- File size limits (16MB)
- GPS coordinate validation
- Category/priority enum validation

### Error Handling
- Custom error pages (404, 500, etc.)
- Detailed error messages in development
- Generic error messages in production
- All errors logged with context

---

## 📝 Status Codes

- `200 OK`: Successful request
- `400 Bad Request`: Invalid input data
- `401 Unauthorized`: Authentication required
- `403 Forbidden`: Insufficient permissions
- `404 Not Found`: Resource not found
- `405 Method Not Allowed`: Wrong HTTP method
- `413 Payload Too Large`: File exceeds 16MB
- `429 Too Many Requests`: Rate limit exceeded
- `500 Internal Server Error`: Server error
- `503 Service Unavailable`: Service temporarily down

---

## 🚀 Best Practices

### For Clients
1. Always check `success` field in responses
2. Handle error messages appropriately
3. Respect rate limits
4. Validate data before sending
5. Use proper authentication

### For Developers
1. Use validation utilities from `validators.py`
2. Apply rate limiters to sensitive endpoints
3. Log all errors with context
4. Use database connection pool
5. Follow RESTful conventions

---

## 📞 Support
For API issues or questions:
- Check logs in `logs/` directory
- Review error messages in responses
- Contact: admin@example.com

---

## 🔄 Versioning
Current API Version: 1.0

Future versions will be accessed via `/api/v2/` prefix.
