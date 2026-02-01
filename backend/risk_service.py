"""
Risk Service - Integration with existing risk calculation modules
Provides high-level API for risk calculations
"""

import sys
import os
from datetime import datetime
from typing import Dict, List, Optional, Tuple

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from threat_score_calculator import ThreatScoreCalculator, calculate_threat
from database import Database
from zone_classifier import classify_zone

class RiskService:
    """Service for risk calculation and monitoring"""
    
    def __init__(self, db_path='risk_module.db'):
        self.calculator = ThreatScoreCalculator()
        self.db = Database(db_path)
        self.db.connect()
        
        # Initialize Nagpur high-risk zones
        self._initialize_nagpur_zones()
    
    def _initialize_nagpur_zones(self):
        """Initialize high-risk zones for Nagpur"""
        # MIDC Hingna Industrial Area
        self.calculator.add_high_risk_zone(21.0850, 79.1100, 1.5)
        
        # Sitabuldi area (high traffic)
        self.calculator.add_high_risk_zone(21.1458, 79.0882, 2.0)
        
        # Add more zones as needed
    
    def calculate_ride_risk(
        self,
        latitude: float,
        longitude: float,
        deviation_count: int = 0,
        timestamp: Optional[datetime] = None
    ) -> Dict:
        """
        Calculate risk score for a ride at given location
        
        Args:
            latitude: Current latitude
            longitude: Current longitude
            deviation_count: Number of route deviations
            timestamp: Current timestamp (optional)
        
        Returns:
            Dictionary with risk score and details
        """
        result = calculate_threat(
            latitude=latitude,
            longitude=longitude,
            timestamp=timestamp,
            number_of_deviations=deviation_count
        )
        
        # Add zone classification
        zone_info = classify_zone(latitude, longitude)
        result['zone_info'] = zone_info
        
        return result
    
    def get_risk_level(self, risk_score: float) -> str:
        """
        Get risk level from risk score
        
        Args:
            risk_score: Risk score (0-100)
        
        Returns:
            Risk level: 'safe', 'low', 'medium', 'high', 'critical'
        """
        if risk_score < 20:
            return 'safe'
        elif risk_score < 40:
            return 'low'
        elif risk_score < 60:
            return 'medium'
        elif risk_score < 80:
            return 'high'
        else:
            return 'critical'
    
    def should_trigger_alert(self, risk_score: float, risk_level: str) -> bool:
        """
        Determine if an alert should be triggered
        
        Args:
            risk_score: Current risk score
            risk_level: Current risk level
        
        Returns:
            True if alert should be triggered
        """
        # Trigger alert for medium risk and above
        return risk_level in ['medium', 'high', 'critical']
    
    def analyze_route_deviation(
        self,
        planned_route: List[Tuple[float, float]],
        current_location: Tuple[float, float]
    ) -> Dict:
        """
        Analyze if current location deviates from planned route
        
        Args:
            planned_route: List of (lat, lon) tuples for planned route
            current_location: Current (lat, lon) tuple
        
        Returns:
            Dictionary with deviation analysis
        """
        # Calculate minimum distance to route
        min_distance = float('inf')
        closest_point = None
        
        for point in planned_route:
            distance = self.calculator._calculate_distance(
                current_location[0], current_location[1],
                point[0], point[1]
            )
            if distance < min_distance:
                min_distance = distance
                closest_point = point
        
        # Consider deviation if more than 300m from route
        is_deviation = min_distance > 0.3  # km
        
        return {
            'is_deviation': is_deviation,
            'distance_from_route_km': min_distance,
            'distance_from_route_m': min_distance * 1000,
            'closest_point': closest_point,
            'severity': 'critical' if min_distance > 1.0 else 'warning' if is_deviation else 'safe'
        }
    
    def get_zone_recommendations(self, latitude: float, longitude: float) -> Dict:
        """
        Get safety recommendations for current zone
        
        Args:
            latitude: Current latitude
            longitude: Current longitude
        
        Returns:
            Dictionary with zone info and recommendations
        """
        zone_info = classify_zone(latitude, longitude)
        
        recommendations = []
        if zone_info['zone_type'] == 'RED':
            recommendations = [
                'High-risk area detected',
                'Automatic monitoring enabled',
                'Emergency services on standby',
                'Avoid stopping in this area'
            ]
        elif zone_info['zone_type'] == 'YELLOW':
            recommendations = [
                'Medium-risk area',
                'Stay alert',
                'Keep doors locked',
                'Share live location with contacts'
            ]
        else:
            recommendations = [
                'Safe area',
                'Normal monitoring active',
                'Continue journey safely'
            ]
        
        return {
            'zone_info': zone_info,
            'recommendations': recommendations
        }
    
    def calculate_eta_risk(
        self,
        expected_eta_minutes: int,
        actual_elapsed_minutes: int
    ) -> Dict:
        """
        Calculate risk based on ETA deviation
        
        Args:
            expected_eta_minutes: Expected journey time
            actual_elapsed_minutes: Actual time elapsed
        
        Returns:
            Dictionary with ETA risk analysis
        """
        deviation_minutes = actual_elapsed_minutes - expected_eta_minutes
        deviation_percentage = (deviation_minutes / expected_eta_minutes) * 100 if expected_eta_minutes > 0 else 0
        
        # Determine risk level
        if deviation_percentage > 50:
            risk_level = 'critical'
            message = 'Journey taking significantly longer than expected'
        elif deviation_percentage > 25:
            risk_level = 'high'
            message = 'Journey delayed beyond normal traffic'
        elif deviation_percentage > 10:
            risk_level = 'medium'
            message = 'Minor delay detected'
        else:
            risk_level = 'safe'
            message = 'Journey on schedule'
        
        return {
            'expected_eta_minutes': expected_eta_minutes,
            'actual_elapsed_minutes': actual_elapsed_minutes,
            'deviation_minutes': deviation_minutes,
            'deviation_percentage': deviation_percentage,
            'risk_level': risk_level,
            'message': message
        }
    
    def get_historical_risk_data(
        self,
        latitude: float,
        longitude: float,
        radius_km: float = 1.0
    ) -> Dict:
        """
        Get historical risk data for an area
        
        Args:
            latitude: Center latitude
            longitude: Center longitude
            radius_km: Search radius in kilometers
        
        Returns:
            Dictionary with historical risk statistics
        """
        # Query database for historical data in this area
        # This is a placeholder - implement actual database query
        
        return {
            'area_center': {'latitude': latitude, 'longitude': longitude},
            'radius_km': radius_km,
            'total_incidents': 0,
            'avg_risk_score': 0.0,
            'incident_types': {},
            'time_distribution': {},
            'message': 'Historical data not yet available'
        }
