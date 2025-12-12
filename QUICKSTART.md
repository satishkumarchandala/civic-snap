# 🚀 Quick Start Guide - Urban Issue Reporter

## Prerequisites Checklist

Before running the application, ensure you have:

- ✅ Python 3.8+ installed
- ✅ MongoDB running (local or Atlas cloud)
- ✅ Virtual environment created (`venv` folder)
- ✅ Dependencies installed

## Option 1: Quick Start (Windows)

Simply double-click:
```
start.bat
```

This will automatically:
1. Activate the virtual environment
2. Check MongoDB connection
3. Verify dependencies
4. Start the application

## Option 2: Manual Start

### Windows:
```powershell
# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Run the application
python run.py
```

### Linux/Mac:
```bash
# Activate virtual environment
source venv/bin/activate

# Run the application
python run.py
```

## Access the Application

Once started, open your browser to:
- **URL**: http://localhost:5000
- **Admin Login**:
  - Email: `admin@example.com`
  - Password: `admin123`

## Default Features Available

✅ **User Features:**
- Register and login
- Complete profile
- Report issues with GPS and photos
- View issue map
- Upvote issues
- Comment on issues

✅ **Admin Features:**
- View all issues dashboard
- Update issue status
- View on map
- Manage users and organizations
- ML automation dashboard
- Bulk operations

## Environment Configuration

Create a `.env` file (optional) to customize:

```env
# Flask Configuration
FLASK_ENV=development
SECRET_KEY=your-secret-key-here
HOST=0.0.0.0
PORT=5000

# MongoDB Configuration
MONGO_URI=mongodb+srv://your-connection-string
MONGO_DB_NAME=urban_issues_db

# Email Configuration (for notifications)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
```

## Troubleshooting

### Issue: "Cannot connect to MongoDB"
**Solution**: 
- Ensure MongoDB service is running locally: `net start MongoDB`
- OR check your Atlas connection string in `config/settings.py`

### Issue: "Module not found"
**Solution**: 
```bash
pip install -r requirements.txt
```

### Issue: "Port 5000 already in use"
**Solution**: 
- Change port in `.env` file: `PORT=5001`
- OR kill the process using port 5000

### Issue: "Permission denied for uploads"
**Solution**: 
- Ensure `uploads/` folder exists and is writable
- Application will auto-create on first run

## Development Mode vs Production

**Development** (default):
- Debug mode ON
- Detailed error messages
- Auto-reload on code changes
- Console logging

**Production**:
```bash
export FLASK_ENV=production
python run.py
```

Or use Gunicorn:
```bash
gunicorn wsgi:app --workers 4 --bind 0.0.0.0:5000
```

## Testing the Application

Run tests:
```bash
pytest tests/
```

## Key Directories

- `app/routes/` - All API endpoints and routes
- `app/models/` - Database models (MongoDB)
- `app/services/` - ML and business logic
- `templates/` - HTML pages
- `static/` - CSS, JS, images
- `uploads/` - User uploaded images
- `logs/` - Application logs
- `models/` - ML model files

## Support

For issues or questions:
1. Check `logs/error.log` for detailed errors
2. Review `PROJECT_ARCHITECTURE.md` for system design
3. See `API_DOCUMENTATION.md` for API details

---

**Ready to make your city better! 🌟**
