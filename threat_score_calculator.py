"""
Threat Score Calculator Module

This module calculates a threat/risk score based on vehicle behavior parameters:
- Latitude and Longitude (location-based risk)
- Time (temporal patterns)
- Number of deviations (behavior anomalies)
"""

import math
import random
import sqlite3
import os
from datetime import datetime
from typing import Tuple, Dict, Optional, List


class ThreatScoreCalculator:
    """
    Calculate threat scores based on driving behavior and location data.
    """
    
    # Risk thresholds
    DEVIATION_THRESHOLD = 5
    
    # Weight factors for different components
    WEIGHTS = {
        'deviation_count': 0.60,
        'location_risk': 0.20,
        'time_risk': 0.20
    }
    
    def __init__(self):
        """Initialize the threat score calculator."""
        self.high_risk_zones = []  # Can be populated with known risky areas
        
    def calculate_deviation_risk(self, deviation_count: int) -> float:
        """
        Calculate risk score from number of deviations.
        
        Args:
            deviation_count: Number of deviations detected
            
        Returns:
            Risk score (0-100)
        """
        if deviation_count == 0:
            return 0
        
        # Logarithmic scaling for deviation count
        risk_score = min(100, 20 * math.log(deviation_count + 1) * 10)
        
        return risk_score
    
    def calculate_location_risk(
        self, 
        latitude: float, 
        longitude: float
    ) -> float:
        """
        Calculate risk score based on location.
        
        Args:
            latitude: Latitude coordinate
            longitude: Longitude coordinate
            
        Returns:
            Risk score (0-100)
        """
        # Base risk is low
        risk_score = 10.0
        
        # Check against high-risk zones
        for zone in self.high_risk_zones:
            zone_lat, zone_lon, zone_radius = zone
            distance = self._calculate_distance(
                latitude, longitude, zone_lat, zone_lon
            )
            
            if distance < zone_radius:
                # Closer to zone center = higher risk
                proximity_factor = 1 - (distance / zone_radius)
                risk_score = max(risk_score, 50 + proximity_factor * 50)
        
        return min(100, risk_score)
    
    def calculate_time_risk(self, timestamp: Optional[datetime] = None) -> float:
        """
        Calculate risk score based on time of day.
        
        Args:
            timestamp: Datetime object (defaults to current time)
            
        Returns:
            Risk score (0-100)
        """
        if timestamp is None:
            timestamp = datetime.now()
        
        hour = timestamp.hour
        
        # Higher risk during late night/early morning (12 AM - 5 AM)
        if 0 <= hour < 5:
            return 60 + (5 - hour) * 8
        # Moderate risk during rush hours (7-9 AM, 5-7 PM)
        elif hour in [7, 8, 17, 18]:
            return 40
        # Lower risk during normal hours
        else:
            return 20
    
    def _calculate_distance(
        self, 
        lat1: float, 
        lon1: float, 
        lat2: float, 
        lon2: float
    ) -> float:
        """
        Calculate distance between two coordinates using Haversine formula.
        
        Args:
            lat1, lon1: First coordinate
            lat2, lon2: Second coordinate
            
        Returns:
            Distance in kilometers
        """
        R = 6371  # Earth's radius in kilometers
        
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lon = math.radians(lon2 - lon1)
        
        a = (math.sin(delta_lat / 2) ** 2 + 
             math.cos(lat1_rad) * math.cos(lat2_rad) * 
             math.sin(delta_lon / 2) ** 2)
        c = 2 * math.asin(math.sqrt(a))
        
        return R * c
    
    def calculate_threat_score(
        self,
        latitude: float,
        longitude: float,
        timestamp: Optional[datetime] = None,
        deviation_count: int = 0
    ) -> Dict[str, float]:
        """
        Calculate overall threat score based on all parameters.
        
        Args:
            latitude: Latitude coordinate
            longitude: Longitude coordinate
            timestamp: Datetime object (optional)
            deviation_count: Number of deviations (required)
            
        Returns:
            Dictionary containing:
                - threat_score: Overall threat score (0-100)
                - risk_level: Risk level category
                - component_scores: Individual component scores
        """
        # Calculate individual component scores
        deviation_risk = self.calculate_deviation_risk(deviation_count)
        location_risk = self.calculate_location_risk(latitude, longitude)
        time_risk = self.calculate_time_risk(timestamp)
        
        # Calculate weighted threat score
        threat_score = (
            deviation_risk * self.WEIGHTS['deviation_count'] +
            location_risk * self.WEIGHTS['location_risk'] +
            time_risk * self.WEIGHTS['time_risk']
        )
        
        # Determine risk level
        if threat_score >= 75:
            risk_level = "CRITICAL"
        elif threat_score >= 60:
            risk_level = "HIGH"
        elif threat_score >= 40:
            risk_level = "MEDIUM"
        elif threat_score >= 20:
            risk_level = "LOW"
        else:
            risk_level = "MINIMAL"
        
        return {
            'threat_score': round(threat_score, 2),
            'risk_level': risk_level,
            'component_scores': {
                'deviation_risk': round(deviation_risk, 2),
                'location_risk': round(location_risk, 2),
                'time_risk': round(time_risk, 2)
            },
            'deviation_count': deviation_count,
            'coordinates': {
                'latitude': latitude,
                'longitude': longitude
            }
        }
    
    def add_high_risk_zone(
        self, 
        latitude: float, 
        longitude: float, 
        radius_km: float
    ):
        """
        Add a high-risk geographic zone.
        
        Args:
            latitude: Zone center latitude
            longitude: Zone center longitude
            radius_km: Zone radius in kilometers
        """
        self.high_risk_zones.append((latitude, longitude, radius_km))



# Database helper functions
def fetch_random_gps_data(db_path: str = None, count: int = 1) -> List[Dict]:
    """
    Fetch random GPS data points from the risk_module database.
    
    Args:
        db_path: Path to the database file (defaults to ../risk_module.db)
        count: Number of random records to fetch
        
    Returns:
        List of dictionaries containing GPS data with keys:
        - latitude, longitude, speed, timestamp, stopped_seconds, scenario
    """
    if db_path is None:
        # Default to parent directory
        current_dir = os.path.dirname(os.path.abspath(__file__))
        db_path = os.path.join(os.path.dirname(current_dir), 'risk_module.db')
    
    if not os.path.exists(db_path):
        raise FileNotFoundError(f"Database not found at: {db_path}")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Fetch random GPS data points
    cursor.execute(f'''
        SELECT latitude, longitude, speed, timestamp, stopped_seconds, scenario
        FROM gps_data
        ORDER BY RANDOM()
        LIMIT {count}
    ''')
    
    rows = cursor.fetchall()
    conn.close()
    
    # Convert to list of dictionaries
    data_points = []
    for row in rows:
        data_points.append({
            'latitude': row[0],
            'longitude': row[1],
            'speed': row[2],
            'timestamp': row[3],
            'stopped_seconds': row[4],
            'scenario': row[5]
        })
    
    return data_points


# Convenience function for quick calculations

def calculate_threat(
    latitude: float,
    longitude: float,
    timestamp: Optional[datetime] = None,
    number_of_deviations: int = 0
) -> Dict[str, float]:
    """
    Quick function to calculate threat score.
    
    Args:
        latitude: Latitude coordinate
        longitude: Longitude coordinate
        timestamp: Datetime object (optional)
        number_of_deviations: Number of deviations
        
    Returns:
        Dictionary with threat score and details
    """
    calculator = ThreatScoreCalculator()
    return calculator.calculate_threat_score(
        latitude=latitude,
        longitude=longitude,
        timestamp=timestamp,
        deviation_count=number_of_deviations
    )


# Example usage
if __name__ == "__main__":
    print("=" * 70)
    print("THREAT ASSESSMENT SYSTEM - Database Testing")
    print("Fetching random GPS data from risk_module.db")
    print("=" * 70)
    print()
    
    try:
        # Fetch random GPS data points from database
        print("Fetching 10 random GPS data points from database...")
        gps_data_points = fetch_random_gps_data(count=10)
        print(f"[OK] Successfully fetched {len(gps_data_points)} data points\n")
        
        # Process first 3 data points for detailed analysis
        for i, data_point in enumerate(gps_data_points[:3], 1):
            print(f"EXAMPLE {i}: {data_point['scenario']} Scenario")
            print("-" * 70)
            
            # Extract data from database
            latitude = data_point['latitude']
            longitude = data_point['longitude']
            speed = data_point['speed']
            timestamp_unix = data_point['timestamp']
            stopped_seconds = data_point['stopped_seconds']
            scenario = data_point['scenario']
            
            # Convert timestamp to datetime
            timestamp_dt = datetime.fromtimestamp(timestamp_unix)
            
            # Calculate deviation count based on scenario
            if 'RISKY' in scenario or 'SUSPICIOUS' in scenario:
                # High deviations for risky scenarios
                deviation_count = random.randint(8, 15)
            elif 'NORMAL' in scenario or 'RANDOM' in scenario:
                # Moderate deviations
                deviation_count = random.randint(3, 8)
            else:  # SAFE scenarios
                # Low deviations
                deviation_count = random.randint(0, 3)
            
            # Calculate threat score
            result = calculate_threat(
                latitude=latitude,
                longitude=longitude,
                timestamp=timestamp_dt,
                number_of_deviations=deviation_count
            )
            
            # Display results
            print(f"Database Record:")
            print(f"  Scenario: {scenario}")
            print(f"  Location: ({latitude:.6f}, {longitude:.6f})")
            print(f"  Speed: {speed:.2f} km/h")
            print(f"  Time: {timestamp_dt.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"  Stopped: {stopped_seconds} seconds")
            print()
            print(f"Threat Assessment:")
            print(f"  Deviation Count: {deviation_count}")
            print(f"  Threat Score: {result['threat_score']}/100")
            print(f"  Risk Level: {result['risk_level']}")
            print()
            print(f"Component Scores:")
            for component, score in result['component_scores'].items():
                print(f"  {component.replace('_', ' ').title()}: {score}/100")
            print("=" * 70)
            print()
        
        # Summary statistics for all 10 points
        print("OVERALL SUMMARY (All 10 Data Points)")
        print("-" * 70)
        
        all_scores = []
        scenario_counts = {}
        
        for data_point in gps_data_points:
            # Calculate deviation count based on scenario
            scenario = data_point['scenario']
            if 'RISKY' in scenario or 'SUSPICIOUS' in scenario:
                deviation_count = random.randint(8, 15)
            elif 'NORMAL' in scenario or 'RANDOM' in scenario:
                deviation_count = random.randint(3, 8)
            else:  # SAFE scenarios
                deviation_count = random.randint(0, 3)
            
            result = calculate_threat(
                latitude=data_point['latitude'],
                longitude=data_point['longitude'],
                timestamp=datetime.fromtimestamp(data_point['timestamp']),
                number_of_deviations=deviation_count
            )
            
            all_scores.append(result['threat_score'])
            scenario_counts[scenario] = scenario_counts.get(scenario, 0) + 1
        
        print(f"Total Data Points Analyzed: {len(gps_data_points)}")
        print(f"Average Threat Score: {sum(all_scores) / len(all_scores):.2f}/100")
        print(f"Highest Threat Score: {max(all_scores):.2f}/100")
        print(f"Lowest Threat Score: {min(all_scores):.2f}/100")
        print()
        print("Scenarios Distribution:")
        for scenario, count in sorted(scenario_counts.items()):
            print(f"  {scenario}: {count} points")
        print("=" * 70)
        
    except FileNotFoundError as e:
        print(f"[ERROR] {e}")
        print("\nPlease ensure risk_module.db exists in the parent directory.")
        print("Expected location: D:\\VNAVC2\\SEM4\\risk_module.db")
    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()


