"""
Simple script to create all default users via the registration API
This bypasses database locking issues by using the API
"""

import requests
import json

API_BASE_URL = 'http://localhost:5000/api'

def create_user(username, email, password, role, phone):
    """Create a user via the registration API"""
    try:
        response = requests.post(
            f'{API_BASE_URL}/register',
            headers={'Content-Type': 'application/json'},
            json={
                'username': username,
                'email': email,
                'password': password,
                'role': role,
                'phone': phone
            }
        )
        
        data = response.json()
        
        if data.get('success'):
            print(f"[OK] Created user: {username} ({role})")
            return True
        else:
            print(f"[SKIP] {username}: {data.get('message', 'Already exists')}")
            return False
    except Exception as e:
        print(f"[ERROR] {username}: {e}")
        return False

def main():
    print("=" * 60)
    print("S4H-1 User Creation via API")
    print("=" * 60)
    print("\nMake sure the Flask server is running on http://localhost:5000")
    print("\nCreating users...\n")
    
    users = [
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
    
    created = 0
    skipped = 0
    
    for user in users:
        if create_user(**user):
            created += 1
        else:
            skipped += 1
    
    print("\n" + "=" * 60)
    print(f"Summary: Created {created} users, Skipped {skipped} (already exist)")
    print("=" * 60)
    
    print("\nDemo Credentials:")
    print("-" * 60)
    for user in users:
        print(f"  {user['username']:12} / {user['password']:15} ({user['role']})")
    print("-" * 60)

if __name__ == '__main__':
    main()
