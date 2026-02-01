import sys
import os
import unittest

# Add path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from app import app, safe_route_engine
except ImportError as e:
    print(f"Import Error: {e}")
    sys.exit(1)

class TestIntegration(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_engine_init(self):
        print("\nTesting Engine Initialization...")
        self.assertIsNotNone(safe_route_engine)
        print("Engine initialized successfully.")
    
    def test_endpoint(self):
        print("\nTesting Endpoint /api/safe_routes_map...")
        # Mock coordinates near Nagpur (Sitabuldi to Dharampeth)
        start_lat, start_lon = 21.1458, 79.0882
        end_lat, end_lon = 21.1400, 79.0600
        
        url = f'/api/safe_routes_map?start_lat={start_lat}&start_lon={start_lon}&end_lat={end_lat}&end_lon={end_lon}'
        response = self.app.get(url)
        
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            print("Response successfully received.")
            content = response.data.decode('utf-8')
            if "folium" in content or "leaflet" in content.lower():
                print("Map HTML content verified.")
            else:
                print("Warning: Map content seems suspicious (no folium/leaflet keywords).")
        else:
            print(f"Error Response: {response.data.decode('utf-8')}")
            
            
        self.assertEqual(response.status_code, 200)

    def test_json_endpoint(self):
        print("\nTesting JSON Endpoint /api/safe_routes...")
        # Use defaults
        url = '/api/safe_routes'
        response = self.app.get(url)
        
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            data = response.json
            if data.get('success'):
                print(f"Success! Routes found: {len(data.get('routes', []))}")
                start_lat = data['start']['lat']
                print(f"Start Lat Verify: {start_lat}")
                # Verify we used the default coordinates provided by user
                # 21.17665960080987
                if abs(start_lat - 21.176659) < 0.0001:
                    print("Default coordinates confirmed.")
            else:
                print(f"API Error: {data.get('error')}")
        else:
            print(f"Error Response: {response.data.decode('utf-8')}")
        
        self.assertEqual(response.status_code, 200)

if __name__ == '__main__':
    unittest.main()
