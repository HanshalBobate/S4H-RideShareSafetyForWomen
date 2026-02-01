from database import Database, datetime

def init_db():
    print("Initializing Database...")
    db = Database('risk_module.db')
    db.connect()
    
    # Create all tables (users, rides, alerts, gps_data, etc.)
    db.create_tables()
    
    # Create default user if not exists
    admin = db.get_user_by_username('admin')
    if not admin:
        print("Creating admin user...")
        # Note: In real app, hash this. For now using plain text or simple hash as per auth.py
        # auth.py uses bcrypt, but here we manually insert. 
        # Actually, let's use auth.py's create_default_users if possible, or just manual mock for now.
        # Ideally we import create_default_users from auth.py
        pass
    
    db.close()
    print("Database initialized successfully.")

    # Now use auth.py to create default users properly
    from auth import UserDatabase, create_default_users
    
    # Initialize UserDatabase (which now uses database.py logic)
    user_db = UserDatabase('risk_module.db')
    
    print("Creating default users...")
    users = create_default_users(user_db)
    print(f"Created {len(users)} default users.")

    # Create dummy ride for testing frontend
    db = Database('risk_module.db')
    db.connect()
    
    # Check if ride exists
    existing_ride = db.get_ride_by_id('TR-8821')
    if not existing_ride:
        print("Creating test ride TR-8821...")
        # Get passenger and driver ids
        p = db.get_user_by_username('priya')
        d = db.get_user_by_username('rajesh')
        
        if p and d:
             db.create_ride(
                ride_id='TR-8821', 
                passenger_id=p[0], 
                driver_id=d[0],
                start_lat=21.1458, start_lon=79.0882,
                end_lat=21.1600, end_lon=79.0900
            )
             print("Test Ride created.")
    
    db.close()

if __name__ == "__main__":
    init_db()
