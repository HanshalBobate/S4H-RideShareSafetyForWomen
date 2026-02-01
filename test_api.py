"""
Test script for Rakshak Backend API
Tests all major endpoints and risk calculation integration
"""

import requests
import json
from datetime import datetime

BASE_URL = 'http://localhost:5000'

def print_section(title):
    """Print section header"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)

def test_endpoint(method, endpoint, data=None, params=None):
    """Test an API endpoint"""
    url = f"{BASE_URL}{endpoint}"
    
    try:
        if method == 'GET':
            response = requests.get(url, params=params)
        elif method == 'POST':
            response = requests.post(url, json=data)
        
        print(f"\n{method} {endpoint}")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Response: {json.dumps(result, indent=2)}")
            return True
        else:
            print(f"Error: {response.text}")
            return False
    
    except requests.exceptions.ConnectionError:
        print(f"ERROR: Could not connect to {BASE_URL}")
        print("Make sure the Flask server is running (python app.py)")
        return False
    except Exception as e:
        print(f"ERROR: {str(e)}")
        return False

def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("  Rakshak Backend API Test Suite")
    print("=" * 60)
    print(f"  Testing server at: {BASE_URL}")
    print("=" * 60)
    
    # Test 1: Risk Calculation
    print_section("Test 1: Risk Calculation API")
    test_endpoint('POST', '/api/calculate_risk', data={
        'latitude': 21.1458,
        'longitude': 79.0882,
        'deviation_count': 2,
        'timestamp': datetime.now().isoformat()
    })
    
    # Test 2: Active Rides
    print_section("Test 2: Active Rides API")
    test_endpoint('GET', '/api/active_rides')
    
    # Test 3: Alerts
    print_section("Test 3: Alerts API")
    test_endpoint('GET', '/api/alerts')
    
    # Test 4: Alerts with Filter
    print_section("Test 4: Alerts API (Critical Only)")
    test_endpoint('GET', '/api/alerts', params={'severity': 'critical'})
    
    # Test 5: Incidents
    print_section("Test 5: Incidents API")
    test_endpoint('GET', '/api/incidents')
    
    # Test 6: Safety Zones
    print_section("Test 6: Safety Zones API")
    test_endpoint('GET', '/api/zones')
    
    # Test 7: Statistics
    print_section("Test 7: Statistics API")
    test_endpoint('GET', '/api/statistics')
    
    # Test 8: Trip History
    print_section("Test 8: Trip History API")
    test_endpoint('GET', '/api/trip_history/PASS-1234')
    
    # Test 9: Volunteers
    print_section("Test 9: Volunteers API")
    test_endpoint('GET', '/api/volunteers')
    
    # Test 10: Assign Volunteer
    print_section("Test 10: Assign Volunteer API")
    test_endpoint('POST', '/api/assign_volunteer', data={
        'incident_id': 'AL-9021',
        'volunteer_id': 'VOL-001'
    })
    
    # Test 11: Update Ride Status
    print_section("Test 11: Update Ride Status API")
    test_endpoint('POST', '/api/update_ride_status', data={
        'ride_id': 'TR-8821',
        'latitude': 21.1458,
        'longitude': 79.0882,
        'speed': 45.5,
        'deviation_count': 1
    })
    
    # Test 12: High Risk Location
    print_section("Test 12: High Risk Location (MIDC Hingna)")
    test_endpoint('POST', '/api/calculate_risk', data={
        'latitude': 21.0850,
        'longitude': 79.1100,
        'deviation_count': 3
    })
    
    print("\n" + "=" * 60)
    print("  All Tests Completed!")
    print("=" * 60)
    print("\nNote: These are basic connectivity tests.")
    print("For production, implement proper unit tests with assertions.")
    print("=" * 60 + "\n")

if __name__ == '__main__':
    main()
