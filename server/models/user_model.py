import bcrypt
from database.db_connection import execute_query

class User:
    def __init__(self, id=None, first_name=None, last_name=None, email=None, 
                 password=None, phone=None, dob=None, gender=None, 
                 address=None, role=None, created_at=None, updated_at=None):
        self.id = id
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.password = password
        self.phone = phone
        self.dob = dob
        self.gender = gender
        self.address = address
        self.role = role
        self.created_at = created_at
        self.updated_at = updated_at
    
    @staticmethod
    def hash_password(password):
        """Hash a password for storing."""
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    @staticmethod
    def check_password(hashed_password, user_password):
        """Verify a stored password against one provided by user"""
        return bcrypt.checkpw(user_password.encode('utf-8'), hashed_password.encode('utf-8'))
    
    @staticmethod
    def create(first_name, last_name, email, password, role, phone=None, dob=None, gender=None, address=None):
        """Create a new user in the database"""
        hashed_password = User.hash_password(password)
        query = """
            INSERT INTO users 
            (first_name, last_name, email, password, phone, dob, gender, address, role) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        params = (first_name, last_name, email, hashed_password, phone, dob, gender, address, role)
        return execute_query(query, params)
    
    @staticmethod
    def get_by_id(user_id):
        """Get a user by ID"""
        query = "SELECT * FROM users WHERE id = %s"
        return execute_query(query, (user_id,), fetchone=True)
    
    @staticmethod
    def get_by_email(email):
        """Get a user by email"""
        query = "SELECT * FROM users WHERE email = %s"
        return execute_query(query, (email,), fetchone=True)
    
    @staticmethod
    def get_all(page=1, per_page=10):
        """Get all users with pagination"""
        offset = (page - 1) * per_page
        query = "SELECT * FROM users LIMIT %s OFFSET %s"
        return execute_query(query, (per_page, offset), fetchall=True)
    
    @staticmethod
    def update(user_id, data):
        """Update a user's information"""
        fields = []
        params = []
        
        # Make sure we have valid data
        if not data or not isinstance(data, dict):
            print("Invalid data for user update")
            return False
        
        # Make sure user_id is valid
        if not user_id:
            print("Invalid user ID for update")
            return False
        
        for key, value in data.items():
            # Skip invalid keys and None values
            if key not in ['first_name', 'last_name', 'email', 'phone', 'dob', 'gender', 'address', 'role']:
                continue
            
            if value is not None:
                fields.append(f"{key} = %s")
                params.append(value)
        
        # Handle password separately to hash it
        if 'password' in data and data['password']:
            fields.append("password = %s")
            params.append(User.hash_password(data['password']))
        
        # Check if we have fields to update
        if not fields:
            print("No valid fields to update")
            return False
        
        # Add updated_at timestamp
        fields.append("updated_at = CURRENT_TIMESTAMP")
        
        params.append(user_id)
    
        try:
            query = f"UPDATE users SET {', '.join(fields)} WHERE id = %s"
            result = execute_query(query, params)
            print(f"User update result: {result}, Query: {query}, Params: {params}")
            return result
        except Exception as e:
            print(f"Error updating user: {e}")
            return False
    
    @staticmethod
    def delete(user_id):
        """Delete a user"""
        query = "DELETE FROM users WHERE id = %s"
        return execute_query(query, (user_id,))
    
    @staticmethod
    def count():
        """Count total number of users"""
        query = "SELECT COUNT(*) as count FROM users"
        result = execute_query(query, fetchone=True)
        return result['count'] if result else 0
        
    @staticmethod
    def authenticate(email, password):
        """Authenticate a user by email and password"""
        user = User.get_by_email(email)
        if user and User.check_password(user['password'], password):
            return user
        return None
    
    @staticmethod
    def get_by_role(role, page=1, per_page=10):
        """Get users by role with pagination"""
        offset = (page - 1) * per_page
        query = "SELECT * FROM users WHERE role = %s LIMIT %s OFFSET %s"
        return execute_query(query, (role, per_page, offset), fetchall=True)