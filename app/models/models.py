"""
Database models and initialization for Urban Issue Reporter - MongoDB Version
"""
from pymongo import MongoClient, ASCENDING, DESCENDING
from pymongo.errors import DuplicateKeyError
from bson.objectid import ObjectId
from datetime import datetime
from werkzeug.security import generate_password_hash
from config.settings import Config
import json

# Global MongoDB client and database
_mongo_client = None
_mongo_db = None

def get_db():
    """Get MongoDB database connection"""
    global _mongo_client, _mongo_db
    
    if _mongo_db is None:
        _mongo_client = MongoClient(Config.MONGO_URI)
        _mongo_db = _mongo_client[Config.MONGO_DB_NAME]
    
    return _mongo_db

def init_db():
    """Initialize MongoDB database with indexes and default data"""
    db = get_db()
    
    # Create collections and indexes
    
    # Organizations collection
    db.organizations.create_index([("name", ASCENDING)], unique=True)
    db.organizations.create_index([("category", ASCENDING)])
    
    # Users collection
    db.users.create_index([("email", ASCENDING)], unique=True)
    db.users.create_index([("role", ASCENDING)])
    db.users.create_index([("organization_id", ASCENDING)])
    
    # Issues collection
    db.issues.create_index([("category", ASCENDING)])
    db.issues.create_index([("status", ASCENDING)])
    db.issues.create_index([("priority_score", DESCENDING)])
    db.issues.create_index([("created_at", DESCENDING)])
    db.issues.create_index([("reported_by", ASCENDING)])
    db.issues.create_index([("latitude", ASCENDING), ("longitude", ASCENDING)])
    # Text index for search
    db.issues.create_index([("title", "text"), ("description", "text")])
    
    # Comments collection
    db.comments.create_index([("issue_id", ASCENDING)])
    db.comments.create_index([("user_id", ASCENDING)])
    db.comments.create_index([("created_at", DESCENDING)])
    
    # User upvotes collection
    db.user_upvotes.create_index([("user_id", ASCENDING), ("issue_id", ASCENDING)], unique=True)
    db.user_upvotes.create_index([("issue_id", ASCENDING)])
    
    # Citizen votes collection
    db.citizen_votes.create_index([("issue_id", ASCENDING), ("user_id", ASCENDING), ("vote_type", ASCENDING)], unique=True)
    
    # Duplicate reports collection
    db.duplicate_reports.create_index([("issue_id", ASCENDING), ("duplicate_issue_id", ASCENDING)], unique=True)
    
    # Priority logs collection
    db.priority_logs.create_index([("issue_id", ASCENDING)])
    db.priority_logs.create_index([("created_at", DESCENDING)])
    
    # Create default organizations if not exist
    organizations_data = [
        {'name': 'Government Main Body', 'category': 'general', 'description': 'Main government administrative body'},
        {'name': 'Electric Department', 'category': 'electricity', 'description': 'Electricity and power related issues'},
        {'name': 'Water Department', 'category': 'water', 'description': 'Water supply and drainage issues'},
        {'name': 'Road Department', 'category': 'road', 'description': 'Road and transportation infrastructure'},
        {'name': 'Transport Department', 'category': 'transport', 'description': 'Public transportation services'},
        {'name': 'Sanitation Department', 'category': 'sanitation', 'description': 'Waste management and cleanliness'},
        {'name': 'Others Department', 'category': 'others', 'description': 'Other civic issues'}
    ]
    
    for org_data in organizations_data:
        try:
            org_data['created_at'] = datetime.utcnow()
            db.organizations.insert_one(org_data)
        except DuplicateKeyError:
            pass  # Organization already exists
    
    # Create super admin user if not exists
    if not db.users.find_one({'email': Config.DEFAULT_ADMIN_EMAIL}):
        admin_password = generate_password_hash(Config.DEFAULT_ADMIN_PASSWORD)
        db.users.insert_one({
            'name': Config.DEFAULT_ADMIN_NAME,
            'email': Config.DEFAULT_ADMIN_EMAIL,
            'password': admin_password,
            'role': 'super_admin',
            'organization_id': None,
            'phone': None,
            'bio': None,
            'profile_picture': None,
            'location': None,
            'created_at': datetime.utcnow()
        })
    
    print(f"✅ MongoDB database initialized successfully")


class User:
    """User model class"""
    
    @staticmethod
    def _doc_to_dict(doc):
        """Convert MongoDB document to dictionary with string ID"""
        if doc:
            doc['id'] = str(doc['_id'])
            del doc['_id']
            # Convert ObjectId references to strings
            if 'organization_id' in doc and doc['organization_id']:
                doc['organization_id'] = str(doc['organization_id'])
        return doc
    
    @staticmethod
    def get_by_email(email):
        """Get user by email"""
        db = get_db()
        user = db.users.find_one({'email': email})
        return User._doc_to_dict(user) if user else None
    
    @staticmethod
    def get_by_id(user_id):
        """Get user by ID"""
        db = get_db()
        try:
            user = db.users.find_one({'_id': ObjectId(user_id)})
            return User._doc_to_dict(user) if user else None
        except:
            return None
    
    @staticmethod
    def get_all():
        """Get all users"""
        db = get_db()
        users = list(db.users.find().sort('created_at', DESCENDING))
        
        # Add organization details
        for user in users:
            if user.get('organization_id'):
                org = db.organizations.find_one({'_id': ObjectId(user['organization_id'])})
                if org:
                    user['organization_name'] = org['name']
                    user['organization_category'] = org['category']
            User._doc_to_dict(user)
        
        return users
    
    @staticmethod
    def get_by_role(role):
        """Get users by role"""
        db = get_db()
        users = list(db.users.find({'role': role}).sort('created_at', DESCENDING))
        return [User._doc_to_dict(user) for user in users]
    
    @staticmethod
    def get_by_organization(org_id):
        """Get users by organization"""
        db = get_db()
        users = list(db.users.find({'organization_id': ObjectId(org_id)}).sort('created_at', DESCENDING))
        return [User._doc_to_dict(user) for user in users]
    
    @staticmethod
    def update_role(user_id, role, organization_id=None):
        """Update user role and organization"""
        db = get_db()
        update_data = {'role': role}
        if organization_id:
            update_data['organization_id'] = ObjectId(organization_id)
        else:
            update_data['organization_id'] = None
        
        db.users.update_one(
            {'_id': ObjectId(user_id)},
            {'$set': update_data}
        )
    
    @staticmethod
    def is_admin(user):
        """Check if user has admin privileges"""
        return user and user.get('role') in ['super_admin', 'org_admin', 'org_staff']
    
    @staticmethod
    def is_super_admin(user):
        """Check if user is super admin"""
        return user and user.get('role') == 'super_admin'
    
    @staticmethod
    def is_org_admin(user):
        """Check if user is organization admin"""
        return user and user.get('role') == 'org_admin'
    
    @staticmethod
    def is_org_staff(user):
        """Check if user is organization staff"""
        return user and user.get('role') == 'org_staff'
    
    @staticmethod
    def create(name, email, password, role='user', organization_id=None):
        """Create new user"""
        db = get_db()
        hashed_password = generate_password_hash(password)
        
        user_doc = {
            'name': name,
            'email': email,
            'password': hashed_password,
            'role': role,
            'organization_id': ObjectId(organization_id) if organization_id else None,
            'phone': None,
            'bio': None,
            'profile_picture': None,
            'location': None,
            'created_at': datetime.utcnow()
        }
        
        result = db.users.insert_one(user_doc)
        return str(result.inserted_id)
    
    @staticmethod
    def get_count():
        """Get total user count (all users including admins)"""
        db = get_db()
        return db.users.count_documents({})
    
    @staticmethod
    def get_citizen_count():
        """Get count of regular users only (excludes admin roles)"""
        db = get_db()
        return db.users.count_documents({'role': 'user'})
    
    @staticmethod
    def update_profile(user_id, name=None, phone=None, bio=None, location=None, profile_picture=None):
        """Update user profile information"""
        db = get_db()
        update_data = {}
        
        if name is not None:
            update_data['name'] = name
        if phone is not None:
            update_data['phone'] = phone
        if bio is not None:
            update_data['bio'] = bio
        if location is not None:
            update_data['location'] = location
        if profile_picture is not None:
            update_data['profile_picture'] = profile_picture
        
        if update_data:
            db.users.update_one(
                {'_id': ObjectId(user_id)},
                {'$set': update_data}
            )
        
        return True
    
    @staticmethod
    def update_password(user_id, new_password):
        """Update user password"""
        db = get_db()
        hashed_password = generate_password_hash(new_password)
        db.users.update_one(
            {'_id': ObjectId(user_id)},
            {'$set': {'password': hashed_password}}
        )
        return True
    
    @staticmethod
    def is_profile_complete(user):
        """Check if user has completed all required profile information"""
        if not user:
            return False
        
        required_fields = ['name', 'email', 'phone', 'location']
        
        for field in required_fields:
            value = user.get(field)
            if not value or (isinstance(value, str) and value.strip() == ''):
                return False
        
        return True
    
    @staticmethod
    def get_missing_profile_fields(user):
        """Get list of missing profile fields for a user"""
        if not user:
            return ['Full Name', 'Email Address', 'Phone Number', 'Location/Address']
        
        required_fields = {
            'name': 'Full Name',
            'email': 'Email Address',
            'phone': 'Phone Number',
            'location': 'Location/Address'
        }
        
        missing_fields = []
        for field, label in required_fields.items():
            value = user.get(field)
            if not value or (isinstance(value, str) and value.strip() == ''):
                missing_fields.append(label)
        
        return missing_fields


class Issue:
    """Issue model class"""
    
    @staticmethod
    def _doc_to_dict(doc):
        """Convert MongoDB document to dictionary with string ID"""
        if doc:
            doc['id'] = str(doc['_id'])
            del doc['_id']
            # Convert ObjectId references to strings
            if 'reported_by' in doc and doc['reported_by']:
                doc['reported_by'] = str(doc['reported_by'])
            if 'assigned_to' in doc and doc['assigned_to']:
                doc['assigned_to'] = str(doc['assigned_to'])
        return doc
    
    @staticmethod
    def get_all(category=None, status=None, search=None):
        """Get all issues with optional filters"""
        db = get_db()
        query = {}
        
        if category and category != 'all':
            query['category'] = category
        
        if status and status != 'all':
            query['status'] = status
        
        if search:
            query['$text'] = {'$search': search}
        
        issues = list(db.issues.find(query).sort('created_at', DESCENDING))
        
        # Add reporter name
        for issue in issues:
            if issue.get('reported_by'):
                user = db.users.find_one({'_id': ObjectId(issue['reported_by'])})
                if user:
                    issue['reporter_name'] = user['name']
            Issue._doc_to_dict(issue)
        
        return issues
    
    @staticmethod
    def get_by_id(issue_id):
        """Get issue by ID"""
        db = get_db()
        try:
            issue = db.issues.find_one({'_id': ObjectId(issue_id)})
            if issue:
                # Add reporter details
                if issue.get('reported_by'):
                    user = db.users.find_one({'_id': ObjectId(issue['reported_by'])})
                    if user:
                        issue['reporter_name'] = user['name']
                        issue['reporter_email'] = user['email']
                return Issue._doc_to_dict(issue)
        except:
            return None
        return None
    
    @staticmethod
    def create(title, description, category, priority, latitude, longitude, address, image_filename, reported_by):
        """Create new issue with ML predictions"""
        # Try to import ML models (graceful fallback if not available)
        try:
            from ml_models import get_ml_predictions
            ml_available = True
        except ImportError:
            print("⚠️  ML models not available, using provided values")
            ml_available = False
        
        # Use ML predictions if available
        if ml_available:
            predictions = get_ml_predictions(title, description, category)
            
            if not category or category == 'auto':
                category = predictions['category']['category']
                print(f"🤖 ML predicted category: {category} (confidence: {predictions['category']['confidence']:.2f})")
            
            if not priority or priority == 'auto':
                priority = predictions['priority']['priority']
                print(f"🎯 ML predicted priority: {priority} (confidence: {predictions['priority']['confidence']:.2f})")
        
        db = get_db()
        
        issue_doc = {
            'title': title,
            'description': description,
            'category': category,
            'priority': priority,
            'status': 'pending',
            'latitude': latitude,
            'longitude': longitude,
            'address': address,
            'image': image_filename,
            'reported_by': ObjectId(reported_by),
            'assigned_to': None,
            'priority_score': 5.0,
            'priority_level': 'medium',
            'priority_breakdown': None,
            'ai_severity_score': None,
            'location_importance_score': None,
            'duplicate_reports_count': 0,
            'upvotes': 0,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow(),
            'last_priority_update': datetime.utcnow()
        }
        
        result = db.issues.insert_one(issue_doc)
        return str(result.inserted_id)
    
    @staticmethod
    def update_status(issue_id, status):
        """Update issue status"""
        db = get_db()
        db.issues.update_one(
            {'_id': ObjectId(issue_id)},
            {'$set': {'status': status, 'updated_at': datetime.utcnow()}}
        )
    
    @staticmethod
    def upvote(issue_id, user_id):
        """Add upvote to issue (only once per user)"""
        db = get_db()
        
        # Check if user has already upvoted
        existing = db.user_upvotes.find_one({
            'user_id': ObjectId(user_id),
            'issue_id': ObjectId(issue_id)
        })
        
        if existing:
            return {'error': 'You have already upvoted this issue', 'already_upvoted': True}
        
        # Add upvote record
        db.user_upvotes.insert_one({
            'user_id': ObjectId(user_id),
            'issue_id': ObjectId(issue_id),
            'created_at': datetime.utcnow()
        })
        
        # Increment upvote count
        result = db.issues.find_one_and_update(
            {'_id': ObjectId(issue_id)},
            {'$inc': {'upvotes': 1}},
            return_document=True
        )
        
        return {'upvotes': result['upvotes'], 'success': True}
    
    @staticmethod
    def has_user_upvoted(issue_id, user_id):
        """Check if user has already upvoted this issue"""
        if not user_id:
            return False
        
        db = get_db()
        result = db.user_upvotes.find_one({
            'user_id': ObjectId(user_id),
            'issue_id': ObjectId(issue_id)
        })
        return result is not None
    
    @staticmethod
    def get_count():
        """Get total issue count"""
        db = get_db()
        return db.issues.count_documents({})
    
    @staticmethod
    def get_count_by_user(user_id):
        """Get issue count for a specific user"""
        db = get_db()
        return db.issues.count_documents({'reported_by': ObjectId(user_id)})
    
    @staticmethod
    def get_by_category(category):
        """Get issues by category"""
        db = get_db()
        issues = list(db.issues.find({'category': category}).sort('created_at', DESCENDING))
        return [Issue._doc_to_dict(issue) for issue in issues]
    
    @staticmethod
    def get_for_organization(user_role, org_category=None, status=None):
        """Get issues based on user role and organization"""
        db = get_db()
        query = {}
        
        # Super admin can see all issues
        if user_role != 'super_admin' and org_category:
            query['category'] = org_category
        
        if status and status != 'all':
            query['status'] = status
        
        issues = list(db.issues.find(query).sort('created_at', DESCENDING))
        return [Issue._doc_to_dict(issue) for issue in issues]
    
    @staticmethod
    def get_stats():
        """Get issue statistics"""
        db = get_db()
        total_issues = db.issues.count_documents({})
        pending_issues = db.issues.count_documents({'status': 'pending'})
        resolved_issues = db.issues.count_documents({'status': 'resolved'})
        recent_issues = list(db.issues.find().sort('created_at', DESCENDING).limit(10))
        
        # Add reporter names
        for issue in recent_issues:
            if issue.get('reported_by'):
                user = db.users.find_one({'_id': ObjectId(issue['reported_by'])})
                if user:
                    issue['reporter_name'] = user['name']
            Issue._doc_to_dict(issue)
        
        return {
            'total_issues': total_issues,
            'pending_issues': pending_issues,
            'resolved_issues': resolved_issues,
            'recent_issues': recent_issues
        }
    
    @staticmethod
    def update_priority_score(issue_id, priority_data):
        """Update issue priority score and related data"""
        db = get_db()
        
        # Get current priority data for logging
        current = db.issues.find_one({'_id': ObjectId(issue_id)}, {'priority_score': 1, 'priority_level': 1})
        
        # Update priority data
        db.issues.update_one(
            {'_id': ObjectId(issue_id)},
            {
                '$set': {
                    'priority_score': priority_data['final_score'],
                    'priority_level': priority_data['priority_level'],
                    'priority_breakdown': json.dumps(priority_data),
                    'last_priority_update': datetime.utcnow()
                }
            }
        )
        
        # Log priority change
        if current:
            db.priority_logs.insert_one({
                'issue_id': ObjectId(issue_id),
                'old_priority_score': current.get('priority_score'),
                'new_priority_score': priority_data['final_score'],
                'old_priority_level': current.get('priority_level'),
                'new_priority_level': priority_data['priority_level'],
                'trigger_reason': 'automatic_recalculation',
                'created_at': datetime.utcnow()
            })
        
        return True
    
    @staticmethod
    def get_priority_sorted(limit=None, category=None, status=None):
        """Get issues sorted by priority score (highest first)"""
        db = get_db()
        query = {}
        
        if category and category != 'all':
            query['category'] = category
        
        if status and status != 'all':
            query['status'] = status
        
        cursor = db.issues.find(query).sort([('priority_score', DESCENDING), ('created_at', DESCENDING)])
        
        if limit:
            cursor = cursor.limit(limit)
        
        issues = list(cursor)
        return [Issue._doc_to_dict(issue) for issue in issues]
    
    @staticmethod
    def get_critical_issues(limit=10):
        """Get critical priority issues (score >= 8.0)"""
        db = get_db()
        issues = list(db.issues.find({
            'priority_score': {'$gte': 8.0},
            'status': {'$ne': 'resolved'}
        }).sort([('priority_score', DESCENDING), ('created_at', ASCENDING)]).limit(limit))
        
        return [Issue._doc_to_dict(issue) for issue in issues]
    
    @staticmethod
    def recalculate_all_priorities():
        """Recalculate priority scores for all unresolved issues"""
        from priority_scoring import PriorityScoring
        
        db = get_db()
        issues = list(db.issues.find({'status': {'$ne': 'resolved'}}))
        
        updated_count = 0
        for issue in issues:
            issue_data = Issue._doc_to_dict(issue)
            priority_data = PriorityScoring.calculate_overall_priority_score(issue_data)
            
            db.issues.update_one(
                {'_id': issue['_id']},
                {
                    '$set': {
                        'priority_score': priority_data['final_score'],
                        'priority_level': priority_data['priority_level'],
                        'priority_breakdown': json.dumps(priority_data),
                        'last_priority_update': datetime.utcnow()
                    }
                }
            )
            updated_count += 1
        
        return updated_count


class Organization:
    """Organization model class"""
    
    @staticmethod
    def _doc_to_dict(doc):
        """Convert MongoDB document to dictionary with string ID"""
        if doc:
            doc['id'] = str(doc['_id'])
            del doc['_id']
        return doc
    
    @staticmethod
    def get_all():
        """Get all organizations"""
        db = get_db()
        orgs = list(db.organizations.find().sort('name', ASCENDING))
        return [Organization._doc_to_dict(org) for org in orgs]
    
    @staticmethod
    def get_by_id(org_id):
        """Get organization by ID"""
        db = get_db()
        try:
            org = db.organizations.find_one({'_id': ObjectId(org_id)})
            return Organization._doc_to_dict(org) if org else None
        except:
            return None
    
    @staticmethod
    def get_by_category(category):
        """Get organization by category"""
        db = get_db()
        org = db.organizations.find_one({'category': category})
        return Organization._doc_to_dict(org) if org else None
    
    @staticmethod
    def create(name, category, description=""):
        """Create new organization"""
        db = get_db()
        org_doc = {
            'name': name,
            'category': category,
            'description': description,
            'created_at': datetime.utcnow()
        }
        result = db.organizations.insert_one(org_doc)
        return str(result.inserted_id)


class Comment:
    """Comment model class"""
    
    @staticmethod
    def _doc_to_dict(doc):
        """Convert MongoDB document to dictionary with string ID"""
        if doc:
            doc['id'] = str(doc['_id'])
            del doc['_id']
            if 'issue_id' in doc and doc['issue_id']:
                doc['issue_id'] = str(doc['issue_id'])
            if 'user_id' in doc and doc['user_id']:
                doc['user_id'] = str(doc['user_id'])
        return doc
    
    @staticmethod
    def get_by_issue_id(issue_id):
        """Get all comments for an issue"""
        db = get_db()
        comments = list(db.comments.find({'issue_id': ObjectId(issue_id)}).sort('created_at', ASCENDING))
        
        # Add user names
        for comment in comments:
            if comment.get('user_id'):
                user = db.users.find_one({'_id': ObjectId(comment['user_id'])})
                if user:
                    comment['user_name'] = user['name']
            Comment._doc_to_dict(comment)
        
        return comments
    
    @staticmethod
    def create(issue_id, user_id, content, is_official=0):
        """Create new comment"""
        db = get_db()
        comment_doc = {
            'issue_id': ObjectId(issue_id),
            'user_id': ObjectId(user_id),
            'content': content,
            'is_official': is_official,
            'created_at': datetime.utcnow()
        }
        result = db.comments.insert_one(comment_doc)
        return str(result.inserted_id)
    
    @staticmethod
    def get_count_by_user(user_id):
        """Get comment count for a specific user"""
        db = get_db()
        return db.comments.count_documents({'user_id': ObjectId(user_id)})


# For backward compatibility, keep get_db_connection as alias
def get_db_connection():
    """Backward compatibility - returns MongoDB database"""
    return get_db()
