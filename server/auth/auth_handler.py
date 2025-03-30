import json
import time
import uuid
import hashlib
from models.user_model import User

# Simple in-memory session store (for production, use a persistent store like Redis)
sessions = {}

class Session:
    def __init__(self, user_id, role, expires=3600):  # 1 hour default session
        self.session_id = str(uuid.uuid4())
        self.user_id = user_id
        self.role = role
        self.created_at = time.time()
        self.expires_at = self.created_at + expires
        self.is_active = True

def create_session(user):
    """Create a new session for a user"""
    session = Session(user['id'], user['role'])
    sessions[session.session_id] = session
    return session.session_id

def validate_session(session_id):
    """Check if a session is valid and not expired"""
    if not session_id or session_id not in sessions:
        return None
    
    session = sessions[session_id]
    if not session.is_active or time.time() > session.expires_at:
        # Session expired
        destroy_session(session_id)
        return None
    
    return session

def get_user_from_session(session_id):
    """Get user details from session"""
    session = validate_session(session_id)
    if not session:
        return None
    
    user = User.get_by_id(session.user_id)
    return user

def destroy_session(session_id):
    """Destroy a session (logout)"""
    if session_id in sessions:
        sessions[session_id].is_active = False
        del sessions[session_id]
    return True

def login(email, password):
    """Authenticate a user and create a session"""
    user = User.authenticate(email, password)
    if not user:
        return None
    
    session_id = create_session(user)
    return {
        'session_id': session_id,
        'user': {
            'id': user['id'],
            'email': user['email'],
            'first_name': user['first_name'],
            'last_name': user['last_name'],
            'role': user['role']
        }
    }

def register(first_name, last_name, email, password, role='artist'):
    """Register a new user"""
    # Check if email already exists
    existing_user = User.get_by_email(email)
    if existing_user:
        return {'success': False, 'message': 'Email already exists'}
    
    # Create new user
    user_id = User.create(
        first_name=first_name,
        last_name=last_name,
        email=email,
        password=password,
        role=role
    )
    
    if not user_id:
        return {'success': False, 'message': 'Failed to create user'}
    
    return {
        'success': True,
        'message': 'User registered successfully',
        'user_id': user_id
    }

def requires_auth(func):
    """Decorator to require authentication for a function"""
    def wrapper(request, *args, **kwargs):
        session_id = request.cookies.get('session_id')
        session = validate_session(session_id)
        
        if not session:
            return {
                'status': 401,
                'message': 'Unauthorized: Please login to continue'
            }
        
        # Set the authenticated user on the request
        request.user = get_user_from_session(session_id)
        return func(request, *args, **kwargs)
    
    return wrapper

def requires_role(roles):
    """Decorator to require specific role(s) for a function"""
    def decorator(func):
        def wrapper(request, *args, **kwargs):
            session_id = request.cookies.get('session_id')
            session = validate_session(session_id)
            
            if not session:
                return {
                    'status': 401,
                    'message': 'Unauthorized: Please login to continue'
                }
            
            if session.role not in roles:
                return {
                    'status': 403, 
                    'message': 'Forbidden: You do not have permission to access this resource'
                }
            
            # Set the authenticated user on the request
            request.user = get_user_from_session(session_id)
            return func(request, *args, **kwargs)
        
        return wrapper
    
    return decorator