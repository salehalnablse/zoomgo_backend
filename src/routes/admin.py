from flask import Blueprint, request, jsonify, session
from src.models.booking import db, User
from werkzeug.security import check_password_hash, generate_password_hash
import hashlib

admin_bp = Blueprint('admin', __name__)

def create_admin_user():
    """Create default admin user if it doesn't exist"""
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        admin = User(
            username='admin',
            email='admin@zoomgorides.com',
            password_hash=generate_password_hash('admin123'),
            is_admin=True
        )
        db.session.add(admin)
        db.session.commit()
        print("Default admin user created: admin / admin123")

@admin_bp.route('/login', methods=['POST'])
def admin_login():
    """Admin login endpoint"""
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({'error': 'Username and password required'}), 400
        
        # Create admin user if it doesn't exist
        create_admin_user()
        
        user = User.query.filter_by(username=username).first()
        
        if not user or not user.is_admin:
            return jsonify({'error': 'Invalid credentials'}), 401
        
        # For demo purposes, use simple password check
        if username == 'admin' and password == 'admin123':
            session['admin_logged_in'] = True
            session['admin_user_id'] = user.id
            
            return jsonify({
                'success': True,
                'message': 'Login successful',
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'is_admin': user.is_admin
                }
            })
        else:
            return jsonify({'error': 'Invalid credentials'}), 401
            
    except Exception as e:
        return jsonify({'error': f'Login failed: {str(e)}'}), 500

@admin_bp.route('/logout', methods=['POST'])
def admin_logout():
    """Admin logout endpoint"""
    session.pop('admin_logged_in', None)
    session.pop('admin_user_id', None)
    return jsonify({'success': True, 'message': 'Logged out successfully'})

@admin_bp.route('/check-auth', methods=['GET'])
def check_auth():
    """Check if admin is authenticated"""
    if session.get('admin_logged_in'):
        user_id = session.get('admin_user_id')
        user = User.query.get(user_id)
        if user and user.is_admin:
            return jsonify({
                'authenticated': True,
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'is_admin': user.is_admin
                }
            })
    
    return jsonify({'authenticated': False})

def require_admin():
    """Decorator to require admin authentication"""
    def decorator(f):
        def wrapper(*args, **kwargs):
            if not session.get('admin_logged_in'):
                return jsonify({'error': 'Authentication required'}), 401
            
            user_id = session.get('admin_user_id')
            user = User.query.get(user_id)
            if not user or not user.is_admin:
                return jsonify({'error': 'Admin access required'}), 403
            
            return f(*args, **kwargs)
        wrapper.__name__ = f.__name__
        return wrapper
    return decorator

