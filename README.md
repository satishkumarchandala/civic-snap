# Urban Issue Reporter - Modular Flask Application

## 🔄 Now Using MongoDB!

This application has been migrated from SQLite to **MongoDB** for better scalability and performance.  
📖 See [MONGODB_SETUP.md](MONGODB_SETUP.md) for detailed setup instructions.

## 🏗️ Project Structure

```
urban-flask-app/
├── app.py                          # Main application entry point
├── config.py                       # Configuration settings
├── models.py                       # Database models and operations
├── utils.py                        # Utility functions
├── auth_utils.py                   # Authentication utilities
├── requirements.txt                # Project dependencies
├── .gitignore                      # Git ignore rules
├── README.md                       # Project documentation
│
├── routes/                         # Route modules
│   ├── __init__.py                # Route initialization
│   ├── main.py                    # Main routes (home, issues, map)
│   ├── auth.py                    # Authentication routes
│   ├── admin.py                   # Admin routes
│   ├── admin_groups.py            # Admin group management
│   ├── profile.py                 # User profile routes
│   ├── ml_routes.py               # ML automation routes
│   └── priority_routes.py         # Priority scoring routes
│
├── static/                         # Static assets
│   ├── css/                       # Stylesheets
│   │   └── style.css
│   ├── js/                        # JavaScript files
│   │   └── app.js
│   └── images/                    # Image assets
│
├── templates/                      # HTML templates
│   ├── base.html                  # Base template
│   ├── index.html                 # Home page
│   ├── login.html                 # Login page
│   ├── register.html              # Registration page
│   ├── profile.html               # User profile
│   ├── issues_map.html            # Issues map view
│   ├── issue_detail.html          # Issue details
│   ├── admin.html                 # Admin dashboard
│   ├── manage_organizations.html  # Organization management
│   ├── report.html                # Issue reporting
│   └── admin/                     # Admin templates
│       ├── groups.html            # Group management
│       └── ml_dashboard.html      # ML dashboard
│
├── models/                         # ML models storage
└── uploads/                        # User uploaded files
```

**Database:** MongoDB (NoSQL document database)

## ✅ Successfully Refactored Features

## 📋 Key Features

### 🔧 Core Functionality
- ✅ **User Management**: Registration, authentication, and profile management
- ✅ **Issue Reporting**: Create issues with image uploads and geolocation
- ✅ **Interactive Map**: View issues on a map with proximity detection
- ✅ **Issue Tracking**: Filter, search, and manage urban issues
- ✅ **Admin Dashboard**: Complete admin panel for issue management
- ✅ **Priority Scoring**: Automated issue prioritization system
- ✅ **ML Automation**: Machine learning models for prediction and classification
- ✅ **Group Management**: Organization and group-based issue handling
- ✅ **Email Notifications**: Automated email alerts for issue updates
- ✅ **Comment System**: Discussion threads on issues with admin responses
- ✅ **Categories**: Road, Transport, Sanitation, Infrastructure, Water, Electricity, Environment, Other

### 🤖 Advanced Features
- **Machine Learning Integration**: Automated issue classification and priority prediction
- **Geographic Clustering**: Issue proximity detection and grouping
- **Priority Scoring**: Dynamic priority calculation based on multiple factors
- **Issue Merging**: Smart detection and merging of duplicate issues

## 🚀 Running the Application

### Prerequisites
- **MongoDB**: Install locally or use MongoDB Atlas (cloud)
  - Local: https://www.mongodb.com/try/download/community
  - Atlas: https://www.mongodb.com/cloud/atlas/register (FREE tier available)

### Setup Steps

1. **Install MongoDB** (if running locally):
   ```powershell
   # Windows with Chocolatey
   choco install mongodb
   
   # Or download from MongoDB website
   ```

2. **Start MongoDB Service**:
   ```powershell
   net start MongoDB
   ```

3. **Install Python Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Environment**:
   - Copy `.env.example` to `.env`
   - Update MongoDB connection settings:
     ```env
     MONGO_URI=mongodb://localhost:27017/
     MONGO_DB_NAME=urban_issues_db
     ```

5. **Run the Application**:
   ```bash
   python app.py
   ```

6. **Access the Application**:
   - Open: http://localhost:5000
   - Admin Login: admin@example.com / admin123

📖 **Detailed MongoDB Setup**: See [MONGODB_SETUP.md](MONGODB_SETUP.md)

## 🧪 Testing Status

✅ **Application successfully tested and verified**
- All routes functional
- Database operations working
- Email system operational
- Admin panel accessible
- Template rendering correct
- No runtime errors

## 🛠️ Technical Stack

- **Backend**: Flask (Python web framework)
- **Database**: SQLite
- **Frontend**: HTML, CSS, JavaScript
- **ML Libraries**: scikit-learn, joblib
- **Email**: SMTP (Gmail)
- **Maps**: Leaflet.js / Google Maps integration
- **Authentication**: Flask sessions with password hashing

## 📝 Configuration

Key configuration settings are in `config.py`:
- Database path
- Upload folder location
- Email SMTP settings
- Secret key for sessions

## 🎯 Project Benefits

- **Clean Architecture**: Modular design with separation of concerns
- **Maintainability**: Easy to locate and modify specific functionality
- **Scalability**: Simple to add new features without affecting existing code
- **Production Ready**: Environment-based configuration and proper error handling

## 📋 Notes

- The application uses SQLite database stored in `urban_issues.db`
- Email notifications are configured for Gmail SMTP (update credentials in `config.py`)
- File uploads are stored in the `uploads/` directory
- ML models are saved in the `models/` directory
- The `.gitignore` file excludes sensitive files, virtual environment, and cache