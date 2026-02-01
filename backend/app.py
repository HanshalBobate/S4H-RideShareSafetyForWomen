"""
Flask Backend for S4H-1 Ride Safety Monitoring System
Main application file with all routes and API endpoints
"""

from flask import Flask, render_template, jsonify, request, session, redirect, url_for
from flask_cors import CORS
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from datetime import datetime, timedelta
import os
import sys
import random

# Add parent directory to path to import risk modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from threat_score_calculator import ThreatScoreCalculator, calculate_threat
from database import Database
from data_models import GPSPoint, Zone, RiskResult
from auth import User, UserDatabase, create_default_users, generate_token

app = Flask(__name__, 
            template_folder='../frontend',
            static_folder='../frontend')
app.secret_key = 'your-secret-key-change-this-in-production'
CORS(app)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login_page'

# Initialize user database
user_db = UserDatabase()

# Create default users if they don't exist
print("\nCreating default users...")
try:
    users = create_default_users(user_db)
    if users:
        print(f"Created {len(users)} users: {', '.join([u.username for u in users])}")
    else:
        print("Default users already exist")
except Exception as e:
    print(f"Note: Some users may already exist ({e})")

@login_manager.user_loader
def load_user(user_id):
    """Load user for Flask-Login"""
    return user_db.get_user_by_id(int(user_id))

# Initialize threat calculator
threat_calculator = ThreatScoreCalculator()

# Add Nagpur high-risk zones
threat_calculator.add_high_risk_zone(21.1458, 79.0882, 2.0)  # Sitabuldi
threat_calculator.add_high_risk_zone(21.0850, 79.1100, 1.5)  # MIDC Hingna

# Initialize database
db = Database('../risk_module.db')
db.connect()
db.create_tables()

# ==================== ROUTES ====================

@app.route('/')
def index():
    """Landing page"""
    return render_template('index.html')

@app.route('/passenger_dashboard')
@login_required
def passenger_dashboard():
    """Passenger dashboard page"""
    if current_user.role not in ['passenger', 'admin']:
        return redirect(url_for('login_page'))
    return render_template('passenger_dashboard.html')

@app.route('/operator_dashboard')
@login_required
def operator_dashboard():
    """Operator dashboard page"""
    if current_user.role not in ['operator', 'driver', 'admin']:
        return redirect(url_for('login_page'))
    return render_template('operator_dashboard.html')

@app.route('/admin_console')
@login_required
def admin_console():
    """Admin console page"""
    if current_user.role != 'admin':
        return redirect(url_for('login_page'))
    return render_template('admin_console.html')

@app.route('/alert')
def alert():
    """Alert monitoring page"""
    return render_template('alert.html')

# ==================== AUTHENTICATION ROUTES ====================

@app.route('/login')
def login_page():
    """Login page"""
    return render_template('login.html')

@app.route('/register')
def register_page():
    """Register page"""
    return render_template('register.html')

@app.route('/api/login', methods=['POST'])
def login():
    """Login API endpoint"""
    try:
        data = request.json
        username = data.get('username')
        password = data.get('password')
        remember = data.get('remember', False)
        
        # Authenticate user
        user = user_db.authenticate_user(username, password)
        
        if user:
            # Log in user with Flask-Login
            login_user(user, remember=remember)
            
            # Generate JWT token
            token = generate_token(user.id, user.role)
            
            return jsonify({
                'success': True,
                'message': 'Login successful',
                'user': user.to_dict(),
                'token': token
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Invalid username or password'
            }), 401
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 400

@app.route('/api/logout', methods=['POST'])
@login_required
def logout():
    """Logout API endpoint"""
    logout_user()
    return jsonify({
        'success': True,
        'message': 'Logged out successfully'
    })

@app.route('/api/register', methods=['POST'])
def register():
    """Register new user"""
    try:
        data = request.json
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        role = data.get('role', 'passenger')
        phone = data.get('phone')
        
        # Create user
        user = user_db.create_user(username, email, password, role, phone)
        
        if user:
            return jsonify({
                'success': True,
                'message': 'User registered successfully',
                'user': user.to_dict()
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Username or email already exists'
            }), 400
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 400

@app.route('/api/current_user')
@login_required
def get_current_user():
    """Get current logged-in user"""
    return jsonify({
        'success': True,
        'user': current_user.to_dict()
    })

# ==================== API ENDPOINTS ====================

@app.route('/api/calculate_risk', methods=['POST'])
def calculate_risk():
    """
    Calculate risk score for given GPS coordinates
    
    Request JSON:
    {
        "latitude": 21.1458,
        "longitude": 79.0882,
        "deviation_count": 2,
        "timestamp": "2026-02-01T00:53:31" (optional)
    }
    """
    try:
        data = request.json
        lat = float(data.get('latitude'))
        lon = float(data.get('longitude'))
        deviation_count = int(data.get('deviation_count', 0))
        
        # Parse timestamp if provided
        timestamp = None
        if 'timestamp' in data:
            timestamp = datetime.fromisoformat(data['timestamp'])
        
        # Calculate threat score
        result = calculate_threat(lat, lon, timestamp, deviation_count)
        
        return jsonify({
            'success': True,
            'data': result
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

@app.route('/api/active_rides', methods=['GET'])
def get_active_rides():
    """Get all active rides with their current status"""
    # Mock data - replace with actual database queries
    rides = [
        {
            'id': 'TR-8821',
            'passenger_name': 'Ananya Kulkarni',
            'driver_name': 'Suresh Patil',
            'vehicle': 'Maruti Suzuki Dzire',
            'plate': 'MH-31-AB-1234',
            'status': 'active',
            'current_location': 'Residency Road Junction',
            'destination': 'Empress Mall',
            'eta_minutes': 8,
            'latitude': 21.1458,
            'longitude': 79.0882,
            'risk_score': 15.5,
            'risk_level': 'safe'
        },
        {
            'id': 'TR-8822',
            'passenger_name': 'Priya Sharma',
            'driver_name': 'Rajesh K.',
            'vehicle': 'Honda City',
            'plate': 'MH-31-CD-5678',
            'status': 'active',
            'current_location': 'Sitabuldi Square',
            'destination': 'VNIT Campus',
            'eta_minutes': 15,
            'latitude': 21.1500,
            'longitude': 79.0850,
            'risk_score': 42.3,
            'risk_level': 'warning'
        }
    ]
    
    return jsonify({
        'success': True,
        'count': len(rides),
        'rides': rides
    })

@app.route('/api/alerts', methods=['GET'])
def get_alerts():
    """Get all active alerts"""
    alerts = [
        {
            'id': 'AL-8291',
            'passenger_name': 'Priya Sharma',
            'driver_name': 'Rajesh K.',
            'ride_id': 'RD-440',
            'type': 'Route Deviation',
            'severity': 'warning',
            'time_ago': '2 mins ago',
            'status': 'pending',
            'latitude': 21.1458,
            'longitude': 79.0882,
            'message': 'Vehicle has diverted 300m from planned route.',
            'current_speed': 42,
            'deviation_distance': 312
        },
        {
            'id': 'AL-8292',
            'passenger_name': 'Amit Deshmukh',
            'driver_name': 'Sneha P.',
            'ride_id': 'RD-442',
            'type': 'Sudden Stop',
            'severity': 'critical',
            'time_ago': 'Just now',
            'status': 'pending',
            'latitude': 21.1702,
            'longitude': 79.0950,
            'message': 'Excessive G-Force detected at intersection.',
            'current_speed': 0,
            'deviation_distance': 0
        }
    ]
    
    severity_filter = request.args.get('severity')
    if severity_filter:
        alerts = [a for a in alerts if a['severity'] == severity_filter]
    
    return jsonify({
        'success': True,
        'count': len(alerts),
        'alerts': alerts
    })

@app.route('/api/incidents', methods=['GET'])
def get_incidents():
    """Get all incidents for operator dashboard"""
    incidents = [
        {
            'id': 'AL-9021',
            'passenger_name': 'Kavita R.',
            'type': 'Deviation',
            'severity': 'critical',
            'district': 'Sitabuldi',
            'time_ago': '2m ago',
            'assigned_volunteer': None,
            'latitude': 21.1458,
            'longitude': 79.0882
        },
        {
            'id': 'AL-9025',
            'passenger_name': 'Aditya D.',
            'type': 'Unusual Stop',
            'severity': 'warning',
            'district': 'Dharampeth',
            'time_ago': '5m ago',
            'assigned_volunteer': 'Vol. Pooja',
            'latitude': 21.1500,
            'longitude': 79.0900
        },
        {
            'id': 'AL-9028',
            'passenger_name': 'Rohan S.',
            'type': 'Low Signal',
            'severity': 'safe',
            'district': 'Sadar',
            'time_ago': '12m ago',
            'assigned_volunteer': None,
            'latitude': 21.1400,
            'longitude': 79.0800
        }
    ]
    
    return jsonify({
        'success': True,
        'count': len(incidents),
        'incidents': incidents
    })

@app.route('/api/zones', methods=['GET'])
def get_zones():
    """Get all safety zones"""
    zones = [
        {
            'id': 'ZONE-001',
            'type': 'safe_corridor',
            'name': 'Sitabuldi-Dharampeth Route',
            'description': 'High-visibility patrolling enabled. 24/7 monitoring.',
            'alert_sensitivity': 'Low',
            'created_date': '2026-01-15',
            'last_updated': '2026-01-30'
        },
        {
            'id': 'ZONE-002',
            'type': 'high_risk',
            'name': 'MIDC Hingna Industrial Area',
            'description': 'Poor lighting detected. Automatic operator assignment for all trips.',
            'alert_sensitivity': 'Ultra-High',
            'created_date': '2026-01-10',
            'last_updated': '2026-01-28'
        }
    ]
    
    return jsonify({
        'success': True,
        'count': len(zones),
        'zones': zones
    })

@app.route('/api/statistics', methods=['GET'])
def get_statistics():
    """Get system statistics"""
    stats = {
        'total_trips_24h': 14284,
        'trips_change_percentage': 12,
        'trips_trend': 'up',
        'resolved_incidents': 182,
        'resolution_percentage': 94,
        'active_staff': 42,
        'connected_ngos': 12,
        'system_load_status': 'Normal',
        'system_status_message': 'All nodes online',
        'active_rides': 1284,
        'pending_alerts': 3,
        'avg_response_time': '42s',
        'safety_score': '99.4%'
    }
    
    return jsonify({
        'success': True,
        'statistics': stats
    })

@app.route('/api/trip_history/<user_id>', methods=['GET'])
def get_trip_history(user_id):
    """Get trip history for a user"""
    trips = [
        {
            'id': 'TR-8810',
            'date': '2026-01-31',
            'time': '16:30',
            'destination': 'Empress Mall',
            'status': 'Safe',
            'status_color': 'success',
            'driver_name': 'Suresh Patil',
            'distance': '8.5 km',
            'duration': '22 mins',
            'fare': '₹125'
        },
        {
            'id': 'TR-8795',
            'date': '2026-01-28',
            'time': '14:15',
            'destination': 'Nagpur Railway Station',
            'status': 'Safe',
            'status_color': 'success',
            'driver_name': 'Rajesh K.',
            'distance': '12.3 km',
            'duration': '28 mins',
            'fare': '₹180'
        },
        {
            'id': 'TR-8702',
            'date': '2026-01-25',
            'time': '09:45',
            'destination': 'VNIT Campus',
            'status': 'Warning',
            'status_color': 'warning',
            'driver_name': 'Vikram M.',
            'distance': '15.2 km',
            'duration': '35 mins',
            'fare': '₹210'
        }
    ]
    
    return jsonify({
        'success': True,
        'user_id': user_id,
        'count': len(trips),
        'trips': trips
    })

@app.route('/api/volunteers', methods=['GET'])
def get_volunteers():
    """Get available volunteers"""
    volunteers = [
        {
            'id': 'VOL-001',
            'name': 'Pooja',
            'status': 'Active',
            'district': 'Sitabuldi',
            'organization': 'Mahila Suraksha Sangh'
        },
        {
            'id': 'VOL-002',
            'name': 'Arjun',
            'status': 'Standby',
            'district': 'Dharampeth',
            'organization': 'Mahila Suraksha Sangh'
        },
        {
            'id': 'VOL-003',
            'name': 'Rahul',
            'status': 'Active',
            'district': 'Sadar',
            'organization': 'Safety First NGO'
        }
    ]
    
    return jsonify({
        'success': True,
        'count': len(volunteers),
        'volunteers': volunteers
    })

@app.route('/api/assign_volunteer', methods=['POST'])
def assign_volunteer():
    """Assign a volunteer to an incident"""
    try:
        data = request.json
        incident_id = data.get('incident_id')
        volunteer_id = data.get('volunteer_id')
        
        # Mock assignment - replace with actual database update
        return jsonify({
            'success': True,
            'message': f'Volunteer {volunteer_id} assigned to incident {incident_id}'
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

@app.route('/api/update_ride_status', methods=['POST'])
def update_ride_status():
    """Update ride status and calculate risk"""
    try:
        data = request.json
        ride_id = data.get('ride_id')
        latitude = float(data.get('latitude'))
        longitude = float(data.get('longitude'))
        speed = float(data.get('speed', 0))
        deviation_count = int(data.get('deviation_count', 0))
        
        # Calculate risk score
        result = calculate_threat(latitude, longitude, None, deviation_count)
        
        # Mock update - replace with actual database update
        return jsonify({
            'success': True,
            'ride_id': ride_id,
            'risk_score': result['threat_score'],
            'risk_level': result['risk_level'],
            'message': 'Ride status updated successfully'
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

# ==================== ERROR HANDLERS ====================

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'error': 'Resource not found'
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'success': False,
        'error': 'Internal server error'
    }), 500

# ==================== MAIN ====================

if __name__ == '__main__':
    print("=" * 60)
    print("S4H-1 Ride Safety Monitoring System - Backend Server")
    print("=" * 60)
    print(f"Server starting on http://localhost:5000")
    print(f"Template folder: {app.template_folder}")
    print(f"Static folder: {app.static_folder}")
    print("=" * 60)
    
    app.run(debug=True, host='0.0.0.0', port=5000)
