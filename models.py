"""
Database Models for Rakshak System
Extends the existing data models with Flask-specific functionality
"""

from datetime import datetime
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data_models import GPSPoint, Zone, RiskResult

class Ride:
    """Model for ride data"""
    def __init__(self, ride_id, passenger_id, driver_id, status='pending'):
        self.ride_id = ride_id
        self.passenger_id = passenger_id
        self.driver_id = driver_id
        self.status = status  # pending, active, completed, cancelled
        self.start_time = None
        self.end_time = None
        self.start_location = None
        self.end_location = None
        self.current_location = None
        self.risk_score = 0.0
        self.risk_level = 'safe'
        self.deviation_count = 0
        self.alerts = []
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'ride_id': self.ride_id,
            'passenger_id': self.passenger_id,
            'driver_id': self.driver_id,
            'status': self.status,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'start_location': self.start_location,
            'end_location': self.end_location,
            'current_location': self.current_location,
            'risk_score': self.risk_score,
            'risk_level': self.risk_level,
            'deviation_count': self.deviation_count,
            'alerts': self.alerts
        }

class User:
    """Model for user data"""
    def __init__(self, user_id, name, email, role, phone=None):
        self.user_id = user_id
        self.name = name
        self.email = email
        self.role = role  # passenger, driver, operator, admin
        self.phone = phone
        self.created_at = datetime.now()
        self.is_active = True
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'user_id': self.user_id,
            'name': self.name,
            'email': self.email,
            'role': self.role,
            'phone': self.phone,
            'created_at': self.created_at.isoformat(),
            'is_active': self.is_active
        }

class Alert:
    """Model for alert/incident data"""
    def __init__(self, alert_id, ride_id, alert_type, severity='warning'):
        self.alert_id = alert_id
        self.ride_id = ride_id
        self.alert_type = alert_type  # route_deviation, sudden_stop, speeding, etc.
        self.severity = severity  # safe, warning, critical
        self.status = 'pending'  # pending, acknowledged, resolved
        self.created_at = datetime.now()
        self.acknowledged_at = None
        self.resolved_at = None
        self.assigned_volunteer = None
        self.latitude = None
        self.longitude = None
        self.message = ''
        self.metadata = {}
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'alert_id': self.alert_id,
            'ride_id': self.ride_id,
            'alert_type': self.alert_type,
            'severity': self.severity,
            'status': self.status,
            'created_at': self.created_at.isoformat(),
            'acknowledged_at': self.acknowledged_at.isoformat() if self.acknowledged_at else None,
            'resolved_at': self.resolved_at.isoformat() if self.resolved_at else None,
            'assigned_volunteer': self.assigned_volunteer,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'message': self.message,
            'metadata': self.metadata
        }

class Volunteer:
    """Model for volunteer/NGO staff data"""
    def __init__(self, volunteer_id, name, organization, district):
        self.volunteer_id = volunteer_id
        self.name = name
        self.organization = organization
        self.district = district
        self.status = 'standby'  # active, standby, offline
        self.phone = None
        self.assigned_incidents = []
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'volunteer_id': self.volunteer_id,
            'name': self.name,
            'organization': self.organization,
            'district': self.district,
            'status': self.status,
            'phone': self.phone,
            'assigned_incidents': self.assigned_incidents
        }

class SafetyZone:
    """Model for safety zone data (extends Zone)"""
    def __init__(self, zone_id, name, zone_type, latitude, longitude, radius_km):
        self.zone_id = zone_id
        self.name = name
        self.zone_type = zone_type  # safe_corridor, high_risk, medium_risk
        self.latitude = latitude
        self.longitude = longitude
        self.radius_km = radius_km
        self.alert_sensitivity = 'medium'  # low, medium, high, ultra-high
        self.description = ''
        self.created_at = datetime.now()
        self.last_updated = datetime.now()
        self.is_active = True
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'zone_id': self.zone_id,
            'name': self.name,
            'zone_type': self.zone_type,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'radius_km': self.radius_km,
            'alert_sensitivity': self.alert_sensitivity,
            'description': self.description,
            'created_at': self.created_at.isoformat(),
            'last_updated': self.last_updated.isoformat(),
            'is_active': self.is_active
        }
