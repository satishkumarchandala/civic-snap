"""
Database connection pooling for MongoDB
Provides connection management and helper utilities
"""
from pymongo import MongoClient
from contextlib import contextmanager
from typing import Optional
import logging
from config.settings import Config

logger = logging.getLogger(__name__)


class MongoDBPool:
    """
    MongoDB connection pool manager
    MongoDB driver handles connection pooling automatically,
    this class provides a convenient interface
    """
    
    def __init__(self, uri: str, database_name: str, pool_size: int = 50):
        self.uri = uri
        self.database_name = database_name
        self.pool_size = pool_size
        self.client = None
        self.db = None
        self._initialized = False
    
    def initialize(self):
        """Initialize MongoDB connection pool"""
        if self._initialized:
            return
        
        try:
            # MongoDB handles connection pooling internally
            self.client = MongoClient(
                self.uri,
                maxPoolSize=self.pool_size,
                minPoolSize=5,
                maxIdleTimeMS=30000,
                connectTimeoutMS=5000,
                serverSelectionTimeoutMS=5000
            )
            
            # Get database
            self.db = self.client[self.database_name]
            
            # Test connection
            self.client.admin.command('ping')
            
            self._initialized = True
            logger.info(f"MongoDB connection pool initialized (max pool size: {self.pool_size})")
            
        except Exception as e:
            logger.error(f"Failed to initialize MongoDB connection: {e}")
            raise
    
    def get_database(self):
        """Get database instance"""
        if not self._initialized:
            self.initialize()
        return self.db
    
    def get_collection(self, collection_name: str):
        """Get a specific collection"""
        if not self._initialized:
            self.initialize()
        return self.db[collection_name]
    
    def close(self):
        """Close MongoDB connection"""
        if self.client:
            self.client.close()
            self._initialized = False
            logger.info("MongoDB connections closed")
    
    def get_stats(self):
        """Get connection pool statistics"""
        if not self._initialized:
            return None
        
        try:
            server_status = self.client.admin.command('serverStatus')
            connections = server_status.get('connections', {})
            
            return {
                'current': connections.get('current'),
                'available': connections.get('available'),
                'total_created': connections.get('totalCreated'),
                'active': connections.get('active'),
                'database': self.database_name
            }
        except Exception as e:
            logger.error(f"Failed to get connection stats: {e}")
            return None


# Global connection pool instance
_db_pool: Optional[MongoDBPool] = None


def init_db_pool(uri: str = None, database_name: str = None, pool_size: int = 50):
    """Initialize the global MongoDB connection pool"""
    global _db_pool
    
    if uri is None:
        uri = Config.MONGO_URI
    if database_name is None:
        database_name = Config.MONGO_DB_NAME
    
    _db_pool = MongoDBPool(uri, database_name, pool_size)
    _db_pool.initialize()
    
    return _db_pool


def get_db_from_pool():
    """Get database instance from the pool"""
    global _db_pool
    
    if _db_pool is None:
        init_db_pool()
    
    return _db_pool.get_database()


def get_collection(collection_name: str):
    """Get a collection from the pool"""
    global _db_pool
    
    if _db_pool is None:
        init_db_pool()
    
    return _db_pool.get_collection(collection_name)


@contextmanager
def get_db_context():
    """
    Context manager for database operations
    
    Usage:
        with get_db_context() as db:
            users = db.users.find({})
    """
    db = get_db_from_pool()
    try:
        yield db
    except Exception as e:
        logger.error(f"Database operation error: {e}", exc_info=True)
        raise
    finally:
        pass  # MongoDB driver handles connection pooling


def close_db_pool():
    """Close the global database pool"""
    global _db_pool
    
    if _db_pool:
        _db_pool.close()
        _db_pool = None


# Helper functions for common operations

def get_one(collection_name: str, query: dict):
    """
    Get a single document from a collection
    
    Args:
        collection_name: Name of the collection
        query: MongoDB query dict
    
    Returns:
        Document dict or None
    """
    try:
        collection = get_collection(collection_name)
        return collection.find_one(query)
    except Exception as e:
        logger.error(f"Error fetching document from {collection_name}: {e}")
        return None


def get_many(collection_name: str, query: dict = None, limit: int = None, sort_by: str = None, sort_order: int = -1):
    """
    Get multiple documents from a collection
    
    Args:
        collection_name: Name of the collection
        query: MongoDB query dict (default: {})
        limit: Maximum number of documents to return
        sort_by: Field name to sort by
        sort_order: 1 for ascending, -1 for descending
    
    Returns:
        List of document dicts
    """
    try:
        collection = get_collection(collection_name)
        cursor = collection.find(query or {})
        
        if sort_by:
            cursor = cursor.sort(sort_by, sort_order)
        
        if limit:
            cursor = cursor.limit(limit)
        
        return list(cursor)
    except Exception as e:
        logger.error(f"Error fetching documents from {collection_name}: {e}")
        return []


def insert_one(collection_name: str, document: dict):
    """
    Insert a single document into a collection
    
    Args:
        collection_name: Name of the collection
        document: Document dict to insert
    
    Returns:
        Inserted document ID or None
    """
    try:
        collection = get_collection(collection_name)
        result = collection.insert_one(document)
        return str(result.inserted_id)
    except Exception as e:
        logger.error(f"Error inserting document into {collection_name}: {e}")
        return None


def update_one(collection_name: str, query: dict, update: dict):
    """
    Update a single document in a collection
    
    Args:
        collection_name: Name of the collection
        query: MongoDB query dict to find document
        update: Update operations dict
    
    Returns:
        Number of documents modified
    """
    try:
        collection = get_collection(collection_name)
        result = collection.update_one(query, update)
        return result.modified_count
    except Exception as e:
        logger.error(f"Error updating document in {collection_name}: {e}")
        return 0


def delete_one(collection_name: str, query: dict):
    """
    Delete a single document from a collection
    
    Args:
        collection_name: Name of the collection
        query: MongoDB query dict to find document
    
    Returns:
        Number of documents deleted
    """
    try:
        collection = get_collection(collection_name)
        result = collection.delete_one(query)
        return result.deleted_count
    except Exception as e:
        logger.error(f"Error deleting document from {collection_name}: {e}")
        return 0


def count_documents(collection_name: str, query: dict = None):
    """
    Count documents in a collection
    
    Args:
        collection_name: Name of the collection
        query: MongoDB query dict (default: {})
    
    Returns:
        Number of documents
    """
    try:
        collection = get_collection(collection_name)
        return collection.count_documents(query or {})
    except Exception as e:
        logger.error(f"Error counting documents in {collection_name}: {e}")
        return 0


# Performance monitoring

def get_pool_stats():
    """Get connection pool statistics"""
    global _db_pool
    
    if _db_pool:
        return _db_pool.get_stats()
    return None


def log_pool_stats():
    """Log connection pool statistics"""
    stats = get_pool_stats()
    if stats:
        logger.info(f"MongoDB Pool Stats: {stats}")
    else:
        logger.warning("Connection pool not initialized")
