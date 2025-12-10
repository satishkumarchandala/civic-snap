# 🔄 MongoDB Migration Guide

## 📋 Overview

Your Urban Issue Reporter project has been successfully migrated from **SQLite** to **MongoDB**! This guide will help you set up and run the application with MongoDB.

---

## 🎯 What Changed

### Files Modified
✅ **models.py** - Completely rewritten for MongoDB using PyMongo  
✅ **db_pool.py** - Updated for MongoDB connection pooling  
✅ **config.py** - Changed database configuration  
✅ **requirements.txt** - Added `pymongo` and `dnspython`  
✅ **.env.example** - Updated with MongoDB connection strings  

### Files Backed Up
📦 **models_sqlite_backup.py** - Original SQLite models (backup)  
📦 **db_pool_sqlite_backup.py** - Original SQLite connection pool (backup)  

---

## 🚀 Quick Start

### Option 1: Local MongoDB (Recommended for Development)

#### Step 1: Install MongoDB

**Windows:**
1. Download MongoDB Community Server: https://www.mongodb.com/try/download/community
2. Run the installer (use default settings)
3. MongoDB will run as a Windows service automatically

**OR use Chocolatey:**
```powershell
choco install mongodb
```

**Verify Installation:**
```powershell
mongod --version
```

#### Step 2: Start MongoDB Service

**Windows (if not running):**
```powershell
# Start MongoDB service
net start MongoDB

# Check if running
Get-Service MongoDB
```

#### Step 3: Configure Environment

Create `.env` file from template:
```powershell
Copy-Item .env.example .env
```

Edit `.env` and ensure these settings:
```env
MONGO_URI=mongodb://localhost:27017/
MONGO_DB_NAME=urban_issues_db
```

#### Step 4: Run the Application

```powershell
# Activate virtual environment (if not already)
.\venv\Scripts\Activate.ps1

# Run the app
python app.py
```

The app will:
- ✅ Connect to MongoDB automatically
- ✅ Create indexes
- ✅ Insert default organizations
- ✅ Create admin user

---

### Option 2: MongoDB Atlas (Cloud - FREE Tier)

#### Step 1: Create MongoDB Atlas Account

1. Go to https://www.mongodb.com/cloud/atlas/register
2. Create free account
3. Create a free cluster (M0 Sandbox - FREE)

#### Step 2: Get Connection String

1. In Atlas dashboard, click **"Connect"**
2. Choose **"Connect your application"**
3. Copy the connection string (looks like):
   ```
   mongodb+srv://username:password@cluster0.xxxxx.mongodb.net/?retryWrites=true&w=majority
   ```

#### Step 3: Configure Whitelist

1. In Atlas dashboard, go to **"Network Access"**
2. Click **"Add IP Address"**
3. Add your IP or click **"Allow Access from Anywhere"** (for testing)

#### Step 4: Update Environment

Edit `.env` file:
```env
MONGO_URI=mongodb+srv://username:password@cluster0.xxxxx.mongodb.net/?retryWrites=true&w=majority
MONGO_DB_NAME=urban_issues_db
```

#### Step 5: Run Application

```powershell
python app.py
```

---

## 🔧 MongoDB Shell Commands (Optional)

### Access MongoDB Shell

```powershell
# Connect to local MongoDB
mongosh

# Or connect to Atlas
mongosh "mongodb+srv://cluster0.xxxxx.mongodb.net/" --username yourusername
```

### Useful Commands

```javascript
// Show databases
show dbs

// Use your database
use urban_issues_db

// Show collections
show collections

// Count documents
db.users.countDocuments()
db.issues.countDocuments()

// Find admin user
db.users.findOne({role: "super_admin"})

// Find all issues
db.issues.find().pretty()

// Find issues by category
db.issues.find({category: "road"})

// Get database stats
db.stats()

// Drop database (CAREFUL!)
// db.dropDatabase()
```

---

## 📊 Data Structure Comparison

### SQLite (Old)
- **Storage**: Single `.db` file
- **Structure**: Fixed schema with tables
- **Relationships**: Foreign keys
- **IDs**: Integer auto-increment

### MongoDB (New)
- **Storage**: Distributed BSON documents
- **Structure**: Flexible schema with collections
- **Relationships**: ObjectId references
- **IDs**: ObjectId (24-char hex string)

---

## 🔄 Migrating Existing Data (Optional)

If you have existing SQLite data you want to migrate:

### Option 1: Manual Migration Script

Create `migrate_sqlite_to_mongo.py`:

```python
import sqlite3
from models import get_db, User, Issue, Organization, Comment
from bson.objectid import ObjectId
from datetime import datetime

# Connect to old SQLite database
sqlite_conn = sqlite3.connect('urban_issues.db')
sqlite_conn.row_factory = sqlite3.Row

# Migrate Organizations
print("Migrating organizations...")
orgs = sqlite_conn.execute("SELECT * FROM organizations").fetchall()
org_id_map = {}
for org in orgs:
    new_org = Organization.create(org['name'], org['category'], org['description'])
    org_id_map[org['id']] = new_org

# Migrate Users
print("Migrating users...")
users = sqlite_conn.execute("SELECT * FROM users").fetchall()
user_id_map = {}
for user in users:
    org_id = org_id_map.get(user['organization_id']) if user['organization_id'] else None
    new_user = User.create(
        user['name'], 
        user['email'], 
        user['password'],  # Already hashed
        user['role'],
        org_id
    )
    user_id_map[user['id']] = new_user

# Migrate Issues
print("Migrating issues...")
issues = sqlite_conn.execute("SELECT * FROM issues").fetchall()
issue_id_map = {}
for issue in issues:
    reported_by = user_id_map.get(issue['reported_by'])
    # ... create issue with mapped IDs

print("Migration complete!")
```

### Option 2: Start Fresh

Simply delete `urban_issues.db` and run the app. MongoDB will create everything fresh.

---

## 🎨 Key Differences in Code

### Getting Data

**SQLite (Old):**
```python
conn = get_db_connection()
user = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
conn.close()
```

**MongoDB (New):**
```python
db = get_db()
user = db.users.find_one({'_id': ObjectId(user_id)})
```

### Creating Records

**SQLite (Old):**
```python
cursor = conn.execute("INSERT INTO users (...) VALUES (?, ?)", (name, email))
user_id = cursor.lastrowid
```

**MongoDB (New):**
```python
result = db.users.insert_one({'name': name, 'email': email})
user_id = str(result.inserted_id)
```

### IDs are Now Strings!

**Important:** MongoDB ObjectIDs are converted to strings in the application:
- Old: `user_id = 123` (integer)
- New: `user_id = "507f1f77bcf86cd799439011"` (string)

All routes and templates handle this automatically!

---

## 🔍 Troubleshooting

### Error: "MongoServerError: Authentication failed"

**Solution:** Check your MongoDB connection string credentials

### Error: "ServerSelectionTimeoutError"

**Causes:**
1. MongoDB service not running
2. Wrong connection string
3. Network/firewall issues

**Solutions:**
```powershell
# Check if MongoDB is running
Get-Service MongoDB

# Start MongoDB
net start MongoDB

# Check connection
mongosh --eval "db.runCommand({ ping: 1 })"
```

### Error: "Database not found"

**Solution:** MongoDB creates databases automatically. Just run the app.

### Error: "Collection not found"

**Solution:** Run `init_db()` - collections are created with indexes automatically

---

## 📈 Performance Benefits

### MongoDB Advantages

✅ **Horizontal Scaling** - Can distribute across multiple servers  
✅ **Flexible Schema** - Easy to add new fields without migrations  
✅ **Better for Large Datasets** - Handles millions of documents efficiently  
✅ **Geospatial Queries** - Built-in support for location-based searches  
✅ **Aggregation Pipeline** - Powerful data processing  
✅ **Automatic Sharding** - Distributes data automatically  

### Performance Tips

1. **Indexes are created automatically** - Check with `db.collection.getIndexes()`
2. **Connection pooling** - Configured with 50 connections by default
3. **Use projections** - Only fetch needed fields: `db.users.find({}, {'name': 1, 'email': 1})`

---

## 🛠️ Development Tools

### MongoDB Compass (GUI)

Free MongoDB GUI tool:
1. Download: https://www.mongodb.com/try/download/compass
2. Install and connect to `mongodb://localhost:27017`
3. Browse collections visually

### VS Code Extension

Install **MongoDB for VS Code**:
1. Open VS Code Extensions
2. Search "MongoDB"
3. Install official MongoDB extension
4. Connect to your database

---

## 📚 Additional Resources

- **MongoDB Documentation**: https://docs.mongodb.com/
- **PyMongo Tutorial**: https://pymongo.readthedocs.io/
- **MongoDB University**: https://university.mongodb.com/ (FREE courses)
- **MongoDB Atlas**: https://www.mongodb.com/cloud/atlas

---

## ✅ Verification Checklist

- [ ] MongoDB installed/Atlas account created
- [ ] MongoDB service running (local) or cluster active (Atlas)
- [ ] `.env` file configured with correct `MONGO_URI`
- [ ] `pymongo` and `dnspython` packages installed
- [ ] Application starts without errors
- [ ] Can login with admin credentials
- [ ] Can create new users
- [ ] Can report issues
- [ ] Can view issues on map

---

## 🔙 Rollback to SQLite

If you need to revert back to SQLite:

```powershell
# Restore SQLite files
Rename-Item "models.py" "models_mongo.py"
Rename-Item "models_sqlite_backup.py" "models.py"
Rename-Item "db_pool.py" "db_pool_mongo.py"
Rename-Item "db_pool_sqlite_backup.py" "db_pool.py"

# Update config.py to use DATABASE_NAME instead of MONGO_URI
```

---

## 🎉 Success!

Your application is now running on MongoDB! Enjoy the benefits of a modern NoSQL database.

**Questions or issues?** Check the troubleshooting section or consult MongoDB documentation.

**Happy coding! 🚀**
