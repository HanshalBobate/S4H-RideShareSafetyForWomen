# test_live_risk.py
# Test risk with manual input

from risk_processor import RiskProcessor
from zone_classifier import classify_location
import time

class LiveRiskTester:
    def __init__(self):
        self.processor = RiskProcessor()
    
    def test_single_point(self, lat, lon, speed, stopped=0):
        # Test a single GPS point
        
        current_time = int(time.time())
        
        result = self.processor.process_point(lat, lon, speed, current_time, stopped)
        zone_info = classify_location(lat, lon)
        
        print(f"\n{'='*60}")
        print("LIVE RISK TEST")
        print(f"{'='*60}")
        
        print(f"\nInput:")
        print(f"  Location: ({lat}, {lon})")
        print(f"  Speed: {speed} km/h")
        print(f"  Stopped: {stopped} seconds")
        
        print(f"\nOutput:")
        print(f"  Zone: {result.zone_name}")
        print(f"  Zone Type: {zone_info['zone_type']}")
        print(f"  Crime Weight: {zone_info['crime_weight']}")
        print(f"  Risk Score: {result.score:.3f}")
        print(f"  Risk Level: {result.level}")
        
        print(f"\nReasons:")
        for reason in result.reasons:
            print(f"  - {reason}")
        
        print(f"\n{'='*60}")
        
        return result
    
    def interactive_mode(self):
        # Interactive mode - user inputs coordinates
        
        print("\n" + "="*60)
        print("LIVE RISK TESTER - INTERACTIVE MODE")
        print("="*60)
        print("\nEnter GPS coordinates to test risk calculation")
        print("Type 'quit' to exit\n")
        
        while True:
            try:
                user_input = input("Enter: latitude,longitude,speed[,stopped] (or 'quit'): ")
                
                if user_input.lower() == 'quit':
                    break
                
                parts = user_input.split(',')
                
                if len(parts) < 3:
                    print("Invalid format. Use: latitude,longitude,speed[,stopped]")
                    continue
                
                lat = float(parts[0])
                lon = float(parts[1])
                speed = float(parts[2])
                stopped = float(parts[3]) if len(parts) > 3 else 0
                
                self.test_single_point(lat, lon, speed, stopped)
                
            except ValueError:
                print("Invalid input. Please enter numbers.")
            except Exception as e:
                print(f"Error: {e}")
        
        print("\nGoodbye!")
    
    def run_preset_tests(self):
        # Run preset test cases
        
        print("\n\n")
        print("█"*60)
        print("█" + " "*58 + "█")
        print("█" + " "*17 + "LIVE RISK TESTING - PRESET CASES" + " "*10 + "█")
        print("█" + " "*58 + "█")
        print("█"*60)
        
        test_cases = [
            {
                'name': 'Test 1: Safe Zone - Daytime - Normal',
                'lat': 21.1458,  # Sitabuldi
                'lon': 79.0882,
                'speed': 40,
                'stopped': 0
            },
            {
                'name': 'Test 2: Red Zone - Daytime - Fast',
                'lat': 21.0976,  # MIDC
                'lon': 78.9772,
                'speed': 70,
                'stopped': 0
            },
            {
                'name': 'Test 3: Yellow Zone - Evening - Slow',
                'lat': 21.0985,  # Hingna Road
                'lon': 79.0030,
                'speed': 15,
                'stopped': 0
            },
            {
                'name': 'Test 4: Red Zone - Stopped 5 minutes',
                'lat': 21.0976,  # MIDC
                'lon': 78.9772,
                'speed': 0,
                'stopped': 300
            },
            {
                'name': 'Test 5: Safe Zone - Very Slow',
                'lat': 21.1458,  # Sitabuldi
                'lon': 79.0882,
                'speed': 5,
                'stopped': 0
            },
        ]
        
        for i, test in enumerate(test_cases, 1):
            print(f"\n{test['name']}")
            result = self.test_single_point(test['lat'], test['lon'], test['speed'], test['stopped'])
            
            # Show recommendation
            if result.level == "CRITICAL":
                print("  🚨 RECOMMENDATION: EMERGENCY - CONTACT AUTHORITIES")
            elif result.level == "HIGH":
                print("  🔴 RECOMMENDATION: ALERT OPERATOR - INVESTIGATE")
            elif result.level == "MEDIUM":
                print("  🟡 RECOMMENDATION: MONITOR CLOSELY")
            elif result.level == "LOW":
                print("  ⚠️ RECOMMENDATION: WATCH FOR CHANGES")
            else:
                print("  ✅ RECOMMENDATION: NORMAL - NO ACTION")
        
        print("\n" + "█"*60 + "\n")


if __name__ == "__main__":
    tester = LiveRiskTester()
    
    print("\nChoose mode:")
    print("1. Run preset test cases")
    print("2. Interactive mode (enter your own coordinates)")
    
    choice = input("\nEnter choice (1 or 2): ").strip()
    
    if choice == "1":
        tester.run_preset_tests()
    elif choice == "2":
        tester.interactive_mode()
    else:
        print("Invalid choice")