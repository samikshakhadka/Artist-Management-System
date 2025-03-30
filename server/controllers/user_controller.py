from models.user_model import User
from auth.auth_handler import requires_role
import datetime

def serialize_datetime(obj):
    """Convert datetime objects to ISO format strings in a dictionary or list."""
    if isinstance(obj, dict):
        for key, value in obj.items():
            if isinstance(value, (datetime.date, datetime.datetime)):
                obj[key] = value.isoformat()
            elif isinstance(value, dict):
                serialize_datetime(value)
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, dict):
                        serialize_datetime(item)
    elif isinstance(obj, list):
        for item in obj:
            if isinstance(item, dict):
                serialize_datetime(item)
    return obj

def register_user_routes(route):
    """Register all user-related routes with the router"""
    
    @route('/api/users', methods=['GET'])
    @requires_role(['super_admin'])
    def get_users(request):
        """Get all users with pagination"""
        page = int(request.query_params.get('page', 1))
        per_page = int(request.query_params.get('per_page', 10))
        
        users = User.get_all(page, per_page)
        total = User.count()
        
        # Remove password hash from response
        for user in users:
            if 'password' in user:
                del user['password']
        
        # Serialize datetime objects to strings
        serialize_datetime(users)
        
        return {
            'status': 200,
            'body': {
                'users': users,
                'pagination': {
                    'page': page,
                    'per_page': per_page,
                    'total': total,
                    'total_pages': (total + per_page - 1) // per_page
                }
            }
        }
    
    @route('/api/users', methods=['POST'])
    @requires_role(['super_admin'])
    def create_user(request):
        """Create a new user"""
        data = request.json_data or request.form_data
        
        required_fields = ['first_name', 'last_name', 'email', 'password', 'role']
        for field in required_fields:
            if field not in data or not data[field]:
                return {
                    'status': 400,
                    'body': {'success': False, 'message': f'{field} is required'}
                }
        
        # Validate role
        valid_roles = ['super_admin', 'artist_manager', 'artist']
        if data['role'] not in valid_roles:
            return {
                'status': 400,
                'body': {'success': False, 'message': 'Invalid role'}
            }
        
        # Check if email already exists
        existing_user = User.get_by_email(data['email'])
        if existing_user:
            return {
                'status': 400,
                'body': {'success': False, 'message': 'Email already exists'}
            }
        
        # Create user
        user_id = User.create(
            first_name=data['first_name'],
            last_name=data['last_name'],
            email=data['email'],
            password=data['password'],
            role=data['role'],
            phone=data.get('phone'),
            dob=data.get('dob'),
            gender=data.get('gender'),
            address=data.get('address')
        )
        
        if not user_id:
            return {
                'status': 500,
                'body': {'success': False, 'message': 'Failed to create user'}
            }
        
        return {
            'status': 201,
            'body': {
                'success': True,
                'message': 'User created successfully',
                'user_id': user_id
            }
        }
    
    @route('/api/users/{id}', methods=['GET'])
    @requires_role(['super_admin'])
    def get_user(request):
        """Get a user by ID"""
        user_id = request.path.split('/')[-1]
        
        user = User.get_by_id(user_id)
        if not user:
            return {
                'status': 404,
                'body': {'success': False, 'message': 'User not found'}
            }
        
        # Remove password hash from response
        if 'password' in user:
            del user['password']
        
        # Serialize datetime objects to strings
        serialize_datetime(user)
        
        return {
            'status': 200,
            'body': {'user': user}
        }
    
    @route('/api/users/{id}', methods=['PUT'])
    @requires_role(['super_admin'])
    def update_user(request):
        """Update a user"""
        user_id = request.path.split('/')[-1]
        data = request.json_data or request.form_data
        
        # Check if user exists
        user = User.get_by_id(user_id)
        if not user:
            return {
                'status': 404,
                'body': {'success': False, 'message': 'User not found'}
            }
        
        # Validate role if provided
        if 'role' in data:
            valid_roles = ['super_admin', 'artist_manager', 'artist']
            if data['role'] not in valid_roles:
                return {
                    'status': 400,
                    'body': {'success': False, 'message': 'Invalid role'}
                }
        
        # Check if email is changed and already exists
        if 'email' in data and data['email'] != user['email']:
            existing_user = User.get_by_email(data['email'])
            if existing_user:
                return {
                    'status': 400,
                    'body': {'success': False, 'message': 'Email already exists'}
                }
        
        # Update user
        result = User.update(user_id, data)
        if not result:
            return {
                'status': 500,
                'body': {'success': False, 'message': 'Failed to update user'}
            }
        
        return {
            'status': 200,
            'body': {
                'success': True,
                'message': 'User updated successfully'
            }
        }
    
    @route('/api/users/{id}', methods=['DELETE'])
    @requires_role(['super_admin'])
    def delete_user(request):
        """Delete a user"""
        user_id = request.path.split('/')[-1]
        
        # Check if user exists
        user = User.get_by_id(user_id)
        if not user:
            return {
                'status': 404,
                'body': {'success': False, 'message': 'User not found'}
            }
        
        # Prevent deleting the last super_admin
        if user['role'] == 'super_admin':
            super_admins = User.get_by_role('super_admin')
            if len(super_admins) <= 1:
                return {
                    'status': 400,
                    'body': {
                        'success': False,
                        'message': 'Cannot delete the last super admin'
                    }
                }
        
        # Delete user
        result = User.delete(user_id)
        if not result:
            return {
                'status': 500,
                'body': {'success': False, 'message': 'Failed to delete user'}
            }
        
        return {
            'status': 200,
            'body': {
                'success': True,
                'message': 'User deleted successfully'
            }
        }
    
    @route('/api/profile', methods=['GET'])
    def get_profile(request):
        """Get current user's profile"""
        if not request.user:
            return {
                'status': 401,
                'body': {'success': False, 'message': 'Unauthorized'}
            }
        
        # Remove password hash from response
        user = dict(request.user)
        if 'password' in user:
            del user['password']
        
        # Serialize datetime objects to strings
        serialize_datetime(user)
        
        return {
            'status': 200,
            'body': {'user': user}
        }
    
    @route('/api/profile', methods=['PUT'])
    def update_profile(request):
        """Update current user's profile"""
        if not request.user:
            return {
                'status': 401,
                'body': {'success': False, 'message': 'Unauthorized'}
            }
        
        data = request.json_data or request.form_data
        user_id = request.user['id']
        
        # Prevent updating role
        if 'role' in data:
            del data['role']
        
        # Check if email is changed and already exists
        if 'email' in data and data['email'] != request.user['email']:
            existing_user = User.get_by_email(data['email'])
            if existing_user:
                return {
                    'status': 400,
                    'body': {'success': False, 'message': 'Email already exists'}
                }
        
        # Update user
        result = User.update(user_id, data)
        if not result:
            return {
                'status': 500,
                'body': {'success': False, 'message': 'Failed to update profile'}
            }
        
        return {
            'status': 200,
            'body': {
                'success': True,
                'message': 'Profile updated successfully'
            }
        }