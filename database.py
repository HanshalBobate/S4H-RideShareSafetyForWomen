# database.py
# This handles database operations

import sqlite3
from datetime import datetime

class Database:
    def __init__(self, db_name='risk_module.db'):
        self.db_name = db_name
        self.conn = None
        self.cursor = None
    
    def connect(self):
        # Connect to database
        print(f"Connecting to database: {self.db_name}")
        self.conn = sqlite3.connect(self.db_name)
        self.cursor = self.conn.cursor()
        print("Connected!\n")
    
    def create_tables(self):
        # Create tables for GPS data and risk results
        
        print("Creating tables...")
        
        # Table 1: GPS Data
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS gps_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                latitude REAL NOT NULL,
                longitude REAL NOT NULL,
                speed REAL NOT NULL,
                timestamp INTEGER NOT NULL,
                stopped_seconds INTEGER NOT NULL,
                scenario TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Table 2: Risk Results
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS risk_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                gps_data_id INTEGER NOT NULL,
                risk_score REAL NOT NULL,
                risk_level TEXT NOT NULL,
                zone_name TEXT NOT NULL,
                zone_type TEXT NOT NULL,
                crime_weight REAL NOT NULL,
                reasons TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (gps_data_id) REFERENCES gps_data(id)
            )
        ''')
        
        # Table 3: Statistics
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS statistics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                total_points INTEGER,
                safe_count INTEGER,
                low_count INTEGER,
                medium_count INTEGER,
                high_count INTEGER,
                critical_count INTEGER,
                average_risk REAL,
                generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Table 4: Users
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL, -- passenger, driver, operator, admin
                phone TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Table 5: Rides
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS rides (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ride_id TEXT UNIQUE NOT NULL, -- TR-XXXX
                passenger_id INTEGER,
                driver_id INTEGER,
                start_lat REAL,
                start_lon REAL,
                end_lat REAL,
                end_lon REAL,
                current_lat REAL,
                current_lon REAL,
                status TEXT DEFAULT 'active', -- active, safe, completed
                risk_score REAL DEFAULT 0,
                risk_level TEXT DEFAULT 'safe',
                start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (passenger_id) REFERENCES users(id),
                FOREIGN KEY (driver_id) REFERENCES users(id)
            )
        ''')

        # Table 6: Alerts
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                alert_id TEXT UNIQUE NOT NULL, -- AL-XXXX
                ride_id TEXT,
                type TEXT NOT NULL, -- Deviation, Stop, Signal
                severity TEXT NOT NULL, -- critical, warning
                message TEXT,
                lat REAL,
                lon REAL,
                status TEXT DEFAULT 'pending', -- pending, resolved
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (ride_id) REFERENCES rides(ride_id)
            )
        ''')

        
        self.conn.commit()
        print("Tables created!\n")
    
    def insert_gps_data(self, data_list):
        # Insert GPS data into database
        
        print(f"Inserting {len(data_list)} GPS data points...")
        
        for i, data in enumerate(data_list):
            self.cursor.execute('''
                INSERT INTO gps_data 
                (latitude, longitude, speed, timestamp, stopped_seconds, scenario)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                data['lat'],
                data['lon'],
                data['speed'],
                data['timestamp'],
                data['stopped'],
                data['scenario']
            ))
            
            if (i + 1) % 5000 == 0:
                print(f"  Inserted {i + 1}/{len(data_list)} points")
        
        self.conn.commit()
        print(f"Inserted all {len(data_list)} points!\n")
    
    def insert_risk_result(self, gps_data_id, result, zone_info):
        # Insert risk result into database
        
        reasons = ' | '.join(result.reasons)
        
        self.cursor.execute('''
            INSERT INTO risk_results
            (gps_data_id, risk_score, risk_level, zone_name, zone_type, crime_weight, reasons)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            gps_data_id,
            result.score,
            result.level,
            result.zone_name,
            zone_info['zone_type'],
            zone_info['crime_weight'],
            reasons
        ))
        
        self.conn.commit()
    
    def insert_risk_results_batch(self, data_list, results, zone_infos):
        # Insert all risk results at once (faster)
        
        print(f"Inserting {len(results)} risk results...")
        
        for i, (data, result, zone_info) in enumerate(zip(data_list, results, zone_infos)):
            reasons = ' | '.join(result.reasons)
            
            self.cursor.execute('''
                INSERT INTO risk_results
                (gps_data_id, risk_score, risk_level, zone_name, zone_type, crime_weight, reasons)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                i + 1,
                result.score,
                result.level,
                result.zone_name,
                zone_info['zone_type'],
                zone_info['crime_weight'],
                reasons
            ))
            
            if (i + 1) % 5000 == 0:
                print(f"  Inserted {i + 1}/{len(results)} results")
        
        self.conn.commit()
        print(f"Inserted all {len(results)} results!\n")
    
    def insert_statistics(self, total, safe, low, medium, high, critical, avg_risk):
        # Insert statistics
        
        self.cursor.execute('''
            INSERT INTO statistics
            (total_points, safe_count, low_count, medium_count, high_count, critical_count, average_risk)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            total,
            safe,
            low,
            medium,
            high,
            critical,
            avg_risk
        ))
        
        self.conn.commit()
        print("Statistics saved!\n")
    
    def get_all_results(self):
        # Get all risk results
        
        self.cursor.execute('''
            SELECT * FROM risk_results
        ''')
        
        return self.cursor.fetchall()
    
    def get_results_by_level(self, level):
        # Get results by risk level
        
        self.cursor.execute('''
            SELECT * FROM risk_results WHERE risk_level = ?
        ''', (level,))
        
        return self.cursor.fetchall()
    
    def get_results_by_zone(self, zone_name):
        # Get results by zone name
        
        self.cursor.execute('''
            SELECT * FROM risk_results WHERE zone_name = ?
        ''', (zone_name,))
        
        return self.cursor.fetchall()
    
    def get_statistics(self):
        # Get latest statistics
        
        self.cursor.execute('''
            SELECT * FROM statistics ORDER BY generated_at DESC LIMIT 1
        ''')
        
        return self.cursor.fetchone()
    
    def get_high_risk_zones(self):
        # Get zones with most high-risk incidents
        
        self.cursor.execute('''
            SELECT zone_name, COUNT(*) as count, AVG(risk_score) as avg_risk
            FROM risk_results
            WHERE risk_level IN ('HIGH', 'CRITICAL')
            GROUP BY zone_name
            ORDER BY count DESC
        ''')
        
        return self.cursor.fetchall()
    
    def export_to_csv(self, filename, query=None):
        # Export results to CSV
        
        import csv
        
        if query is None:
            self.cursor.execute('SELECT * FROM risk_results')
        else:
            self.cursor.execute(query)
        
        rows = self.cursor.fetchall()
        cols = [description[0] for description in self.cursor.description]
        
        with open(filename, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(cols)
            writer.writerows(rows)
        
        print(f"Exported {len(rows)} rows to {filename}\n")
    
    def delete_all_data(self):
        # Delete all data (for fresh start)
        
        self.cursor.execute('DELETE FROM risk_results')
        self.cursor.execute('DELETE FROM gps_data')
        self.cursor.execute('DELETE FROM statistics')
        self.conn.commit()
        print("All data deleted!\n")
    
    def close(self):
        # Close database connection
        
        if self.conn:
            self.conn.close()
            print("Database closed!\n")
    
    def show_summary(self):
        # Show database summary
        
        self.cursor.execute('SELECT COUNT(*) FROM gps_data')
        gps_count = self.cursor.fetchone()[0]
        
        self.cursor.execute('SELECT COUNT(*) FROM risk_results')
        risk_count = self.cursor.fetchone()[0]
        
        self.cursor.execute('''
            SELECT risk_level, COUNT(*) FROM risk_results
            GROUP BY risk_level
        ''')
        level_counts = self.cursor.fetchall()
        
        print("\n" + "="*50)
        print("DATABASE SUMMARY")
        print("="*50)
        print(f"GPS Data Points: {gps_count}")
        print(f"Risk Results: {risk_count}")
        print("\nRisk Level Distribution:")
        for level, count in level_counts:
            print(f"  {level}: {count}")
        print("="*50 + "\n")

    # ========================================================
    # NEW METHODS FOR APP INTEGRATION
    # ========================================================

    def create_user(self, username, email, password_hash, role, phone):
        try:
            self.cursor.execute('''
                INSERT INTO users (username, email, password_hash, role, phone)
                VALUES (?, ?, ?, ?, ?)
            ''', (username, email, password_hash, role, phone))
            self.conn.commit()
            return self.cursor.lastrowid
        except sqlite3.IntegrityError:
            return None

    def get_user_by_username(self, username):
        self.cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
        return self.cursor.fetchone()

    def get_user_by_id(self, user_id):
        self.cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
        return self.cursor.fetchone()

    def create_ride(self, ride_id, passenger_id, driver_id, start_lat, start_lon, end_lat, end_lon):
        self.cursor.execute('''
            INSERT INTO rides (ride_id, passenger_id, driver_id, start_lat, start_lon, end_lat, end_lon, current_lat, current_lon)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (ride_id, passenger_id, driver_id, start_lat, start_lon, end_lat, end_lon, start_lat, start_lon))
        self.conn.commit()
        return self.cursor.lastrowid

    def update_ride_location(self, ride_id, lat, lon, risk_score, risk_level):
        self.cursor.execute('''
            UPDATE rides 
            SET current_lat = ?, current_lon = ?, risk_score = ?, risk_level = ?
            WHERE ride_id = ?
        ''', (lat, lon, risk_score, risk_level, ride_id))
        self.conn.commit()

    def get_active_rides(self):
        # Join with users to get names if needed, for now simple select
        self.cursor.execute('''
            SELECT r.*, p.username as passenger_name, d.username as driver_name 
            FROM rides r
            LEFT JOIN users p ON r.passenger_id = p.id
            LEFT JOIN users d ON r.driver_id = d.id
            WHERE r.status = 'active'
        ''')
        columns = [description[0] for description in self.cursor.description]
        return [dict(zip(columns, row)) for row in self.cursor.fetchall()]

    def get_ride_by_id(self, ride_id):
        self.cursor.execute('''
            SELECT r.*, p.username as passenger_name, d.username as driver_name, 
                   d.phone as driver_phone
            FROM rides r
            LEFT JOIN users p ON r.passenger_id = p.id
            LEFT JOIN users d ON r.driver_id = d.id
            WHERE r.ride_id = ?
        ''', (ride_id,))
        row = self.cursor.fetchone()
        if row:
            columns = [description[0] for description in self.cursor.description]
            return dict(zip(columns, row))
        return None

    def create_alert(self, alert_id, ride_id, type, severity, message, lat, lon):
        self.cursor.execute('''
            INSERT INTO alerts (alert_id, ride_id, type, severity, message, lat, lon)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (alert_id, ride_id, type, severity, message, lat, lon))
        self.conn.commit()

    def get_active_alerts(self):
        self.cursor.execute('''
            SELECT a.*, r.passenger_id, u.username as passenger_name 
            FROM alerts a
            JOIN rides r ON a.ride_id = r.ride_id
            JOIN users u ON r.passenger_id = u.id
            WHERE a.status = 'pending'
            ORDER BY a.timestamp DESC
        ''')
        columns = [description[0] for description in self.cursor.description]
        return [dict(zip(columns, row)) for row in self.cursor.fetchall()]
