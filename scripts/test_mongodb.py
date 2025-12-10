"""
MongoDB Connection Test Script
Run this to verify your MongoDB setup before starting the application
"""
import sys
import os
from dotenv import load_dotenv

# Load environment variables from .env file FIRST
load_dotenv()

from pymongo import MongoClient
from config import Config

def test_mongodb_connection():
    """Test MongoDB connection"""
    print("=" * 60)
    print("🔍 Testing MongoDB Connection")
    print("=" * 60)
    
    # Connection details
    print(f"\n📍 MongoDB URI: {Config.MONGO_URI}")
    print(f"📦 Database Name: {Config.MONGO_DB_NAME}")
    
    try:
        # Try to connect
        print("\n🔌 Connecting to MongoDB...")
        client = MongoClient(Config.MONGO_URI, serverSelectionTimeoutMS=5000)
        
        # Test connection with ping
        client.admin.command('ping')
        print("✅ Successfully connected to MongoDB!")
        
        # Get database
        db = client[Config.MONGO_DB_NAME]
        print(f"✅ Database '{Config.MONGO_DB_NAME}' ready")
        
        # List collections (if any)
        collections = db.list_collection_names()
        if collections:
            print(f"\n📚 Existing collections: {', '.join(collections)}")
        else:
            print("\n📚 No collections yet (will be created on first run)")
        
        # Get server info
        server_info = client.server_info()
        print(f"\n🖥️  MongoDB Version: {server_info['version']}")
        
        # Get database stats
        stats = db.command("dbstats")
        print(f"💾 Database Size: {stats.get('dataSize', 0) / 1024:.2f} KB")
        print(f"📊 Collections: {stats.get('collections', 0)}")
        
        # Test write operation
        print("\n🧪 Testing write operation...")
        test_collection = db['_connection_test']
        test_collection.insert_one({'test': 'connection', 'status': 'success'})
        test_collection.delete_one({'test': 'connection'})
        print("✅ Write operation successful!")
        
        # Close connection
        client.close()
        
        print("\n" + "=" * 60)
        print("🎉 MongoDB Setup Complete!")
        print("=" * 60)
        print("\n✅ You can now run: python app.py")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Connection Failed!")
        print(f"Error: {str(e)}")
        print("\n🔧 Troubleshooting Steps:")
        print("1. Make sure MongoDB is installed")
        print("2. Check if MongoDB service is running:")
        print("   - Windows: Get-Service MongoDB")
        print("   - Start: net start MongoDB")
        print("3. Verify connection string in .env file")
        print("4. For MongoDB Atlas:")
        print("   - Check network access whitelist")
        print("   - Verify username/password")
        print("   - Ensure correct connection string format")
        print("\n📖 See MONGODB_SETUP.md for detailed instructions")
        
        return False

if __name__ == "__main__":
    success = test_mongodb_connection()
    sys.exit(0 if success else 1)
