"""
Main application routes - home, issues, and general functionality
"""
from flask import render_template, request, jsonify, redirect, url_for, flash, session, send_from_directory, Response
from werkzeug.utils import secure_filename
from datetime import datetime
import os
import uuid
import base64
from app.models.models import Issue, Comment, User, get_db_connection
from app.utils.utils import send_email_notification, generate_issue_report_email, generate_comment_email, allowed_file

def init_routes(app):
    """Initialize main routes"""
    
    @app.route('/health')
    def health_check():
        """Health check endpoint for monitoring"""
        return jsonify({'status': 'healthy', 'service': 'urban-issues-reporter'}), 200
    
    @app.route('/uploads/<filename>')
    def uploaded_file(filename):
        """Serve uploaded images from database"""
        # Get image from database
        db = get_db_connection()
        image_doc = db.images.find_one({'filename': filename})
        
        if image_doc and image_doc.get('image_data'):
            # Decode base64 image data
            image_binary = base64.b64decode(image_doc['image_data'])
            return Response(image_binary, mimetype=image_doc.get('mime_type', 'image/jpeg'))
        
        # Fallback: try to serve from file system if exists (for backward compatibility)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        if os.path.exists(file_path):
            return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
        
        return 'Image not found', 404
    
    @app.route('/')
    def index():
        """Home page with issue listing and statistics"""
        # Get statistics for the homepage - count only regular citizens, not admins
        total_users = User.get_citizen_count()
        total_issues = Issue.get_count()
        
        # Get filters from query params
        category = request.args.get('category', '')
        status = request.args.get('status', '')
        search = request.args.get('search', '')
        
        # Organization category to issue category mapping
        org_to_issue_category_map = {
            'electricity': 'electricity',
            'water': 'water',
            'road': 'road',
            'transport': 'transport',
            'sanitation': 'sanitation',
            'dustbin': 'sanitation',  # Map dustbin to sanitation
            'others': 'others',
            'general': None  # General can see all categories
        }
        
        # Check if user is logged in and get their organization category
        user_org_category = None
        if 'user_id' in session:
            user = User.get_by_id(session['user_id'])
            if user and (User.is_org_admin(user) or User.is_org_staff(user)):
                # Get user's organization category to filter issues
                if user.get('organization_id'):
                    db = get_db_connection()
                    from bson.objectid import ObjectId
                    org = db.organizations.find_one({'_id': ObjectId(user['organization_id'])})
                    if org:
                        org_category = org['category']
                        # Map organization category to issue category
                        user_org_category = org_to_issue_category_map.get(org_category)
        
        # If user is org admin/staff and no category filter is specified, 
        # filter by their organization category (unless they're general admin)
        if user_org_category and not category:
            category = user_org_category
        
        # Get filtered issues
        issues = Issue.get_all(category, status, search)
        
        return render_template('index.html', issues=issues, 
                             current_category=category, current_status=status, search_term=search,
                             total_users=total_users, total_issues=total_issues,
                             user_org_category=user_org_category)
    
    @app.route('/report', methods=['GET', 'POST'])
    def report_issue():
        """Report new issue"""
        if 'user_id' not in session:
            flash('Please login to report issues!', 'error')
            return redirect(url_for('login'))
        
        # Check if user profile is complete
        user = User.get_by_id(session['user_id'])
        if not User.is_profile_complete(user):
            missing_fields = User.get_missing_profile_fields(user)
            flash(f'Please complete your profile before reporting issues. Missing: {", ".join(missing_fields)}', 'error')
            return redirect(url_for('profile'))
        
        if request.method == 'POST':
            title = request.form['title']
            description = request.form['description']
            category = request.form['category']
            priority = request.form['priority']
            latitude = float(request.form['latitude'])
            longitude = float(request.form['longitude'])
            address = request.form['address']
            
            # Handle file upload with compression
            image_filename = None
            if 'image' in request.files:
                file = request.files['image']
                if file and file.filename and allowed_file(file.filename):
                    try:
                        from PIL import Image
                        import io
                        
                        filename = str(uuid.uuid4()) + '.jpg'  # Always save as JPEG
                        
                        # Open and compress image
                        img = Image.open(file.stream)
                        
                        # Convert RGBA to RGB if necessary
                        if img.mode in ('RGBA', 'LA', 'P'):
                            background = Image.new('RGB', img.size, (255, 255, 255))
                            if img.mode == 'P':
                                img = img.convert('RGBA')
                            background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                            img = background
                        
                        # Resize if too large (max 1200px width/height)
                        max_size = 1200
                        if img.width > max_size or img.height > max_size:
                            img.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
                        
                        # Compress and save to bytes
                        img_byte_arr = io.BytesIO()
                        img.save(img_byte_arr, format='JPEG', quality=85, optimize=True)
                        img_byte_arr.seek(0)
                        
                        # Encode to base64
                        image_base64 = base64.b64encode(img_byte_arr.read()).decode('utf-8')
                        
                        # Save to MongoDB
                        from app.models.models import get_db_connection as get_db
                        db = get_db()
                        db.images.insert_one({
                            'filename': filename,
                            'image_data': image_base64,
                            'mime_type': 'image/jpeg',
                            'created_at': datetime.utcnow()
                        })
                        
                        image_filename = filename
                    except Exception as e:
                        print(f"Error processing image: {e}")
                        import traceback
                        traceback.print_exc()
                        flash('Error uploading image. Please try a different image.', 'warning')
            
            # Save to database
            issue_id = Issue.create(title, description, category, priority, latitude, longitude, 
                                  address, image_filename, session['user_id'])
            
            # Calculate initial priority score
            try:
                from app.services.priority_scoring import PriorityScoring, ImageAnalysis
                
                # Get the created issue
                issue = Issue.get_by_id(issue_id)
                
                # Analyze image if present
                if image_filename:
                    ai_severity = ImageAnalysis.analyze_issue_image(
                        image_filename, 
                        category
                    )
                    if ai_severity:
                        # Update issue with AI severity score
                        db = get_db_connection()
                        from bson.objectid import ObjectId
                        db.issues.update_one(
                            {'_id': ObjectId(issue_id)},
                            {'$set': {'ai_severity_score': ai_severity}}
                        )
                        
                        # Refresh issue data
                        issue = Issue.get_by_id(issue_id)
                
                # Calculate comprehensive priority score
                priority_data = PriorityScoring.calculate_overall_priority_score(issue)
                Issue.update_priority_score(issue_id, priority_data)
                
            except Exception as e:
                print(f"Warning: Could not calculate priority score: {e}")
            
            # Send notification email to user
            email_body = generate_issue_report_email(
                session['user_name'], title, category, priority, address, issue_id
            )
            send_email_notification(session['user_email'], f"📋 Issue Reported: {title}", email_body, app.config)
            
            flash('Issue reported successfully! Confirmation email sent!', 'success')
            return redirect(url_for('issue_detail', issue_id=issue_id))
        
        return render_template('report.html')
    
    @app.route('/issue/<int:issue_id>')
    def issue_detail(issue_id):
        """Issue detail page"""
        # Get issue details
        issue = Issue.get_by_id(issue_id)
        
        if not issue:
            flash('Issue not found!', 'error')
            return redirect(url_for('index'))
        
        # Get comments
        comments = Comment.get_by_issue_id(issue_id)
        
        # Check if current user has upvoted this issue
        user_has_upvoted = False
        if 'user_id' in session:
            user_has_upvoted = Issue.has_user_upvoted(issue_id, session['user_id'])
        
        return render_template('issue_detail.html', issue=issue, comments=comments, user_has_upvoted=user_has_upvoted)
    
    @app.route('/add_comment/<int:issue_id>', methods=['POST'])
    def add_comment(issue_id):
        """Add comment to issue"""
        if 'user_id' not in session:
            flash('Please login to comment!', 'error')
            return redirect(url_for('login'))
        
        # Check if user profile is complete (except for admins)
        if not session.get('is_admin'):
            user = User.get_by_id(session['user_id'])
            if not User.is_profile_complete(user):
                missing_fields = User.get_missing_profile_fields(user)
                flash(f'Please complete your profile before commenting. Missing: {", ".join(missing_fields)}', 'error')
                return redirect(url_for('profile'))
        
        content = request.form['content']
        is_official = 1 if session.get('is_admin') else 0
        
        # Add comment
        Comment.create(issue_id, session['user_id'], content, is_official)
        
        # Get issue details for email notification
        issue = Issue.get_by_id(issue_id)
        
        # Send email notification to issue reporter
        if issue and issue['reporter_email'] and issue['reporter_email'] != session.get('user_email'):
            email_body = generate_comment_email(
                issue['reporter_name'], issue['title'], session['user_name'], 
                content, issue_id, is_official
            )
            comment_type = "Official Response" if is_official else "New Comment"
            send_email_notification(issue['reporter_email'], 
                                  f"💬 {comment_type}: {issue['title']}", email_body, app.config)
        
        flash('Comment added successfully!', 'success')
        return redirect(url_for('issue_detail', issue_id=issue_id))
    
    @app.route('/upvote/<int:issue_id>', methods=['POST'])
    def upvote_issue(issue_id):
        """Upvote an issue"""
        if 'user_id' not in session:
            return jsonify({'error': 'Login required'}), 401
            
        # Check if user profile is complete
        user = User.get_by_id(session['user_id'])
        if not User.is_profile_complete(user):
            missing_fields = User.get_missing_profile_fields(user)
            return jsonify({'error': f'Please complete your profile before upvoting. Missing: {", ".join(missing_fields)}'}), 400
        
        result = Issue.upvote(issue_id, session['user_id'])
        
        if 'error' in result:
            return jsonify(result), 400
        
        return jsonify(result)
    
    @app.route('/demo')
    def demo():
        """Interactive demo showing how to report an issue"""
        return render_template('demo.html')
