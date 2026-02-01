
import requests
import time
import json

BASE_URL = "http://localhost:5000"
RIDE_ID = "TR-8821"

def test_flow():
    print(f"Testing End-to-End Flow for Ride {RIDE_ID}")
    
    # 1. Send Telemetry Update (Safe)
    print("\n1. Sending Telemetry (Safe)...")
    payload_safe = {
        "ride_id": RIDE_ID,
        "latitude": 21.1500,
        "longitude": 79.0900,
        "speed": 45,
        "deviation_count": 0
    }
    try:
        resp = requests.post(f"{BASE_URL}/api/update_ride_status", json=payload_safe)
        print(f"Status: {resp.status_code}")
        print(f"Response: {resp.json()}")
    except Exception as e:
        print(f"Failed to connect: {e}")
        return

    # 2. Verify Update via Tracking API
    print("\n2. Verifying via Tracking API...")
    time.sleep(1)
    resp = requests.get(f"{BASE_URL}/api/tracking/{RIDE_ID}")
    data = resp.json()
    print(f"Current Location: {data['current_location']['latitude']}, {data['current_location']['longitude']}")
    print(f"Risk Level: {data['risk_level']}")
    
    if data['current_location']['latitude'] == 21.1500:
        print("✅ SUCCESS: Location Verification Passed")
    else:
        print("❌ FAILED: Location Verification Failed")

    # 3. Send Telemetry Update (Critical Risk)
    print("\n3. Sending Telemetry (Critical Risk)...")
    payload_risk = {
        "ride_id": RIDE_ID,
        "latitude": 21.1500,
        "longitude": 79.0900,
        "speed": 0,
        "deviation_count": 10 # High deviation triggers risk
    }
    resp = requests.post(f"{BASE_URL}/api/update_ride_status", json=payload_risk)
    print(f"Response: {resp.json()}")
    
    # 4. Verify Alert Generation
    print("\n4. Verifying Alerts...")
    time.sleep(1)
    resp = requests.get(f"{BASE_URL}/api/alerts")
    alerts = resp.json()['alerts']
    
    # Check if there is an alert for this ride
    found = False
    for a in alerts:
        if a['ride_id'] == RIDE_ID:
            print(f"✅ Found Alert: {a['type']} - {a['severity']}")
            found = True
            break
            
    if not found:
        print("❌ FAILED: No Alert Generated")

if __name__ == "__main__":
    test_flow()
