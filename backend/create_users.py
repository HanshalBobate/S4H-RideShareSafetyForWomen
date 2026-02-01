"""
Script to create default users for S4H-1 system
Run this to manually create the demo users
"""

import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.auth import UserDatabase, create_default_users

def main():
    print("=" * 60)
    print("S4H-1 User Creation Script")
    print("=" * 60)
    
    # Initialize user database
    print("\n1. Initializing user database...")
    user_db = UserDatabase('../risk_module.db')
    print("   [OK] Database initialized")
    
    # Create default users
    print("\n2. Creating default users...")
    try:
        users = create_default_users(user_db)
        
        if users:
            print(f"   [OK] Created {len(users)} users:")
            for user in users:
                print(f"      - {user.username} ({user.role}) - {user.email}")
        else:
            print("   [WARN] No new users created (they may already exist)")
    except Exception as e:
        print(f"   [ERROR] Error creating users: {e}")
        import traceback
        traceback.print_exc()
    
    # List all users
    print("\n3. Listing all users in database...")
    try:
        all_users = user_db.get_all_users()
        print(f"   Total users: {len(all_users)}")
        for user in all_users:
            print(f"      - {user.username} ({user.role}) - {user.email}")
    except Exception as e:
        print(f"   [ERROR] Error listing users: {e}")
    
    # Test authentication
    print("\n4. Testing authentication...")
    test_credentials = [
        ('priya', 'passenger123'),
        ('admin', 'admin123'),
        ('operator1', 'operator123'),
        ('rajesh', 'driver123')
    ]
    
    for username, password in test_credentials:
        user = user_db.authenticate_user(username, password)
        if user:
            print(f"   [OK] {username}: Authentication successful")
        else:
            print(f"   [FAIL] {username}: Authentication failed")
    
    print("\n" + "=" * 60)
    print("Done!")
    print("=" * 60)

if __name__ == '__main__':
    main()

