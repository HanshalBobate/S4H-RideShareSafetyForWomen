# data_generator.py
# This generates fake GPS data for testing

import random
import time
from datetime import datetime, timedelta

class DataGenerator:
    def __init__(self):
        self.base_lat = 21.12
        self.base_lon = 79.08
        self.data_points = []
    
    def generate_safe_route(self, count):
        # Generate normal driving - safe
        points = []
        
        for i in range(count):
            # Start at a random time during day
            hours_offset = random.randint(6, 21)
            base_time = int(time.time()) - 86400 + (hours_offset * 3600)
            
            lat = self.base_lat + random.uniform(-0.02, 0.02)
            lon = self.base_lon + random.uniform(-0.02, 0.02)
            speed = random.uniform(30, 60)
            
            points.append({
                'lat': lat,
                'lon': lon,
                'speed': speed,
                'timestamp': base_time + i * 5,
                'stopped': 0,
                'scenario': 'SAFE_ROUTE'
            })
        
        return points
    
    def generate_risky_deviation(self, count):
        # Generate risky behavior - deviation from route
        points = []
        
        for i in range(count):
            # Night time
            hours_offset = random.randint(22, 24) if random.random() > 0.5 else random.randint(0, 5)
            base_time = int(time.time()) - 86400 + (hours_offset * 3600)
            
            # Move away from normal route
            lat = self.base_lat + random.uniform(-0.05, 0.05)
            lon = self.base_lon + random.uniform(-0.05, 0.05)
            
            # Fast speed (evasive?)
            speed = random.uniform(50, 80)
            
            points.append({
                'lat': lat,
                'lon': lon,
                'speed': speed,
                'timestamp': base_time + i * 5,
                'stopped': 0,
                'scenario': 'RISKY_DEVIATION'
            })
        
        return points
    
    def generate_suspicious_stop(self, count):
        # Generate suspicious stops
        points = []
        
        for i in range(count):
            # Night time
            hours_offset = random.randint(22, 24) if random.random() > 0.5 else random.randint(0, 5)
            base_time = int(time.time()) - 86400 + (hours_offset * 3600)
            
            # Red zone area (MIDC or similar)
            lat = 21.0976
            lon = 78.9772
            
            # Add some variation
            lat += random.uniform(-0.02, 0.02)
            lon += random.uniform(-0.02, 0.02)
            
            # Stopped
            speed = 0
            stopped_time = random.randint(180, 600)  # 3-10 minutes
            
            points.append({
                'lat': lat,
                'lon': lon,
                'speed': speed,
                'timestamp': base_time + i * 5,
                'stopped': stopped_time,
                'scenario': 'SUSPICIOUS_STOP'
            })
        
        return points
    
    def generate_normal_commute(self, count):
        # Generate normal commute pattern
        points = []
        
        for i in range(count):
            # Random time
            random_hour = random.randint(0, 23)
            base_time = int(time.time()) - 86400 + (random_hour * 3600)
            
            lat = self.base_lat + random.uniform(-0.03, 0.03)
            lon = self.base_lon + random.uniform(-0.03, 0.03)
            
            # Variable speed based on time
            if 6 <= random_hour <= 9:
                speed = random.uniform(20, 40)  # Morning traffic
            elif 9 <= random_hour <= 17:
                speed = random.uniform(35, 55)  # Normal driving
            elif 17 <= random_hour <= 20:
                speed = random.uniform(25, 45)  # Evening traffic
            else:
                speed = random.uniform(40, 70)  # Night driving
            
            stopped = random.randint(0, 120) if random.random() > 0.8 else 0
            
            points.append({
                'lat': lat,
                'lon': lon,
                'speed': speed,
                'timestamp': base_time + i * 5,
                'stopped': stopped,
                'scenario': 'NORMAL_COMMUTE'
            })
        
        return points
    
    def generate_random_mixed(self, count):
        # Generate random mixed behavior
        points = []
        
        for i in range(count):
            random_hour = random.randint(0, 23)
            base_time = int(time.time()) - 86400 + (random_hour * 3600)
            
            lat = self.base_lat + random.uniform(-0.04, 0.04)
            lon = self.base_lon + random.uniform(-0.04, 0.04)
            speed = random.uniform(0, 80)
            stopped = random.randint(0, 300) if speed < 5 else 0
            
            points.append({
                'lat': lat,
                'lon': lon,
                'speed': speed,
                'timestamp': base_time + i * 5,
                'stopped': stopped,
                'scenario': 'RANDOM_MIXED'
            })
        
        return points
    
    def generate_20000_points(self):
        # Generate 20,000 points split into scenarios
        
        print("Generating 20,000 data points...\n")
        
        # Distribution
        safe_count = 5000          # 25%
        risky_count = 3000         # 15%
        suspicious_count = 2000    # 10%
        commute_count = 5000       # 25%
        random_count = 5000        # 25%
        
        print("Generating SAFE_ROUTE points (5,000)...")
        self.data_points.extend(self.generate_safe_route(safe_count))
        
        print("Generating RISKY_DEVIATION points (3,000)...")
        self.data_points.extend(self.generate_risky_deviation(risky_count))
        
        print("Generating SUSPICIOUS_STOP points (2,000)...")
        self.data_points.extend(self.generate_suspicious_stop(suspicious_count))
        
        print("Generating NORMAL_COMMUTE points (5,000)...")
        self.data_points.extend(self.generate_normal_commute(commute_count))
        
        print("Generating RANDOM_MIXED points (5,000)...")
        self.data_points.extend(self.generate_random_mixed(random_count))
        
        print(f"\nTotal generated: {len(self.data_points)} points\n")
        
        return self.data_points
    
    def save_to_file(self, filename):
        # Save to CSV file
        import csv
        
        print(f"Saving to {filename}...")
        
        with open(filename, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['lat', 'lon', 'speed', 'timestamp', 'stopped', 'scenario'])
            writer.writeheader()
            writer.writerows(self.data_points)
        
        print(f"Saved {len(self.data_points)} points to {filename}\n")
    
    def load_from_file(self, filename):
        # Load from CSV file
        import csv
        
        print(f"Loading from {filename}...")
        
        self.data_points = []
        
        with open(filename, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                self.data_points.append({
                    'lat': float(row['lat']),
                    'lon': float(row['lon']),
                    'speed': float(row['speed']),
                    'timestamp': int(row['timestamp']),
                    'stopped': int(row['stopped']),
                    'scenario': row['scenario']
                })
        
        print(f"Loaded {len(self.data_points)} points\n")
        
        return self.data_points