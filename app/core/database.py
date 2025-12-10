"""
Database initialization and connection management
MongoDB connection setup for Urban Issue Reporter
"""
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
import logging
import os
from config import get_config

logger = logging.getLogger(__name__)

# Global MongoDB client and database
_mongo_client = None
_mongo_db = None


def init_db():
    """Initialize database connection with MongoDB Atlas"""
    global _mongo_client, _mongo_db
    
    try:
        config = get_config()
        mongo_uri = config.MONGO_URI
        db_name = config.MONGO_DB_NAME
        
        logger.info(f"Connecting to MongoDB: {db_name}")
        
        # Create MongoDB client
        _mongo_client = MongoClient(
            mongo_uri,
            serverSelectionTimeoutMS=5000,
            connectTimeoutMS=10000,
            socketTimeoutMS=10000,
            maxPoolSize=50,
            minPoolSize=10
        )
        
        # Test connection
        _mongo_client.admin.command('ping')
        
        # Get database
        _mongo_db = _mongo_client[db_name]
        
        # Create indexes for better performance
        _create_indexes()
        
        logger.info(f"Successfully connected to MongoDB database: {db_name}")
        
    except (ConnectionFailure, ServerSelectionTimeoutError) as e:
        logger.error(f"Failed to connect to MongoDB: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Error initializing database: {str(e)}")
        raise


def _create_indexes():
    """Create database indexes for better query performance"""
    global _mongo_db
    
    if _mongo_db is None:
        return
    
    try:
        # Issues collection indexes
        _mongo_db.issues.create_index('user_id')
        _mongo_db.issues.create_index('status')
        _mongo_db.issues.create_index('category')
        _mongo_db.issues.create_index('created_at')
        _mongo_db.issues.create_index([('location.latitude', 1), ('location.longitude', 1)])
        
        # Users collection indexes
        _mongo_db.users.create_index('email', unique=True)
        _mongo_db.users.create_index('role')
        
        # Comments collection indexes
        _mongo_db.comments.create_index('issue_id')
        _mongo_db.comments.create_index('user_id')
        
        # Organizations collection indexes
        _mongo_db.organizations.create_index('name')
        
        logger.info("Database indexes created successfully")
        
    except Exception as e:
        logger.warning(f"Error creating indexes: {str(e)}")


def get_db():
    """Get database instance"""
    global _mongo_db
    
    if _mongo_db is None:
        init_db()
    
    return _mongo_db


def close_db():
    """Close database connection"""
    global _mongo_client, _mongo_db
    
    if _mongo_client is not None:
        _mongo_client.close()
        _mongo_client = None
        _mongo_db = None
        logger.info("MongoDB connection closed")
