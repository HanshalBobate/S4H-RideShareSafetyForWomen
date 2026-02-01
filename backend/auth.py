"""
User Authentication Module for S4H-1
Handles user management, authentication, and authorization
"""

from flask_login import UserMixin
import bcrypt
import jwt
from datetime import datetime, timedelta
import sqlite3
import os

class User(UserMixin):
    """User model for authentication"""
    
    def __init__(self, id, username, email, password_hash, role, phone=None, is_active=True):
        self.id = id
        self.username = username
        self.email = email
        self.password_hash = password_hash
        self.role = role  # passenger, driver, operator, admin
        self.phone = phone
        self._active = is_active  # Use _active to avoid conflict with UserMixin
    
    @property
    def is_active(self):
        """Override UserMixin's is_active property"""
        return self._active
    
    def get_id(self):
        """Return user ID as string for Flask-Login"""
        return str(self.id)
    
    def to_dict(self):
        """Convert user to dictionary"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'phone': self.phone,
            'is_active': self._active
        }
    
    @staticmethod
    def hash_password(password):
        """Hash a password using bcrypt"""
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    @staticmethod
    def check_password(password, password_hash):
        """Verify a password against its hash"""
        return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))


class UserDatabase:
    """Database operations for user management"""
    
    def __init__(self, db_path='../risk_module.db'):
        self.db_path = db_path
        self.init_database()
    
    def get_connection(self):
        """Get database connection"""
        return sqlite3.connect(self.db_path)
    
    def init_database(self):
        """Initialize users table"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL,
                phone TEXT,
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def create_user(self, username, email, password, role='passenger', phone=None):
        """Create a new user"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            password_hash = User.hash_password(password)
            
            cursor.execute('''
                INSERT INTO users (username, email, password_hash, role, phone)
                VALUES (?, ?, ?, ?, ?)
            ''', (username, email, password_hash, role, phone))
            
            user_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            return self.get_user_by_id(user_id)
        
        except sqlite3.IntegrityError as e:
            return None  # User already exists
    
    def get_user_by_id(self, user_id):
        """Get user by ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return User(
                id=row[0],
                username=row[1],
                email=row[2],
                password_hash=row[3],
                role=row[4],
                phone=row[5],
                is_active=bool(row[6])
            )
        return None
    
    def get_user_by_username(self, username):
        """Get user by username"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return User(
                id=row[0],
                username=row[1],
                email=row[2],
                password_hash=row[3],
                role=row[4],
                phone=row[5],
                is_active=bool(row[6])
            )
        return None
    
    def get_user_by_email(self, email):
        """Get user by email"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return User(
                id=row[0],
                username=row[1],
                email=row[2],
                password_hash=row[3],
                role=row[4],
                phone=row[5],
                is_active=bool(row[6])
            )
        return None
    
    def authenticate_user(self, username, password):
        """Authenticate user with username and password"""
        user = self.get_user_by_username(username)
        
        if user and User.check_password(password, user.password_hash):
            return user
        return None
    
    def update_user(self, user_id, **kwargs):
        """Update user information"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Build update query dynamically
        fields = []
        values = []
        
        for key, value in kwargs.items():
            if key in ['username', 'email', 'role', 'phone', 'is_active']:
                fields.append(f"{key} = ?")
                values.append(value)
        
        if fields:
            query = f"UPDATE users SET {', '.join(fields)} WHERE id = ?"
            values.append(user_id)
            
            cursor.execute(query, values)
            conn.commit()
        
        conn.close()
        return self.get_user_by_id(user_id)
    
    def delete_user(self, user_id):
        """Delete user (soft delete by setting is_active to False)"""
        return self.update_user(user_id, is_active=False)
    
    def get_all_users(self, role=None):
        """Get all users, optionally filtered by role"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        if role:
            cursor.execute('SELECT * FROM users WHERE role = ? AND is_active = 1', (role,))
        else:
            cursor.execute('SELECT * FROM users WHERE is_active = 1')
        
        rows = cursor.fetchall()
        conn.close()
        
        users = []
        for row in rows:
            users.append(User(
                id=row[0],
                username=row[1],
                email=row[2],
                password_hash=row[3],
                role=row[4],
                phone=row[5],
                is_active=bool(row[6])
            ))
        
        return users


def create_default_users(user_db):
    """Create default users for testing"""
    default_users = [
        {
            'username': 'admin',
            'email': 'admin@s4h1.com',
            'password': 'admin123',
            'role': 'admin',
            'phone': '+91-9876543210'
        },
        {
            'username': 'operator1',
            'email': 'operator@s4h1.com',
            'password': 'operator123',
            'role': 'operator',
            'phone': '+91-9876543211'
        },
        {
            'username': 'priya',
            'email': 'priya@example.com',
            'password': 'passenger123',
            'role': 'passenger',
            'phone': '+91-9876543212'
        },
        {
            'username': 'rajesh',
            'email': 'rajesh@example.com',
            'password': 'driver123',
            'role': 'driver',
            'phone': '+91-9876543213'
        }
    ]
    
    created_users = []
    for user_data in default_users:
        user = user_db.create_user(
            username=user_data['username'],
            email=user_data['email'],
            password=user_data['password'],
            role=user_data['role'],
            phone=user_data['phone']
        )
        if user:
            created_users.append(user)
    
    return created_users


# JWT Token utilities
SECRET_KEY = 'your-secret-key-change-in-production'

def generate_token(user_id, role):
    """Generate JWT token for user"""
    payload = {
        'user_id': user_id,
        'role': role,
        'exp': datetime.utcnow() + timedelta(days=1)  # Token expires in 1 day
    }
    return jwt.encode(payload, SECRET_KEY, algorithm='HS256')

def verify_token(token):
    """Verify JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None  # Token expired
    except jwt.InvalidTokenError:
        return None  # Invalid token
