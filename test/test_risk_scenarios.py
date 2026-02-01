# test_risk_scenarios.py
# Test risk with real-world scenarios

from risk_processor import RiskProcessor
from zone_classifier import classify_location
import time
from datetime import datetime, timedelta

class RiskScenarioTester:
    def __init__(self):
        self.processor = RiskProcessor()
        self.scenarios = []
    
    def add_scenario(self, name, description, points):
        # Add a scenario to test
        self.scenarios.append({
            'name': name,
            'description': description,
            'points': points
        })
    
    def run_scenario(self, scenario):
        # Run one scenario
        
        print(f"\n{'='*60}")
        print(f"SCENARIO: {scenario['name']}")
        print(f"{'='*60}")
        print(f"Description: {scenario['description']}\n")
        
        results = []
        
        for i, point in enumerate(scenario['points']):
            result = self.processor.process_point(
                lat=point['lat'],
                lon=point['lon'],
                speed_kmh=point['speed'],
                timestamp=point['timestamp'],
                stopped_seconds=point.get('stopped', 0)
            )
            results.append(result)
            
            # Show each point
            if i < 5 or i % 10 == 0:  # Show first 5 and every 10th
                dt = datetime.fromtimestamp(point['timestamp'])
                print(f"Point {i+1} ({dt.strftime('%H:%M')}):")
                print(f"  Speed: {point['speed']} km/h, Stopped: {point.get('stopped', 0)}s")
                print(f"  Zone: {result.zone_name} ({classify_location(point['lat'], point['lon'])['zone_type']})")
                print(f"  Risk: {result.score:.3f} ({result.level})")
                print(f"  Reasons: {', '.join(result.reasons)}\n")
        
        # Summary
        safe_count = sum(1 for r in results if r.level == "SAFE")
        low_count = sum(1 for r in results if r.level == "LOW")
        medium_count = sum(1 for r in results if r.level == "MEDIUM")
        high_count = sum(1 for r in results if r.level == "HIGH")
        critical_count = sum(1 for r in results if r.level == "CRITICAL")
        avg_score = sum(r.score for r in results) / len(results)
        
        print(f"Summary:")
        print(f"  Total Points: {len(results)}")
        print(f"  SAFE: {safe_count}")
        print(f"  LOW: {low_count}")
        print(f"  MEDIUM: {medium_count}")
        print(f"  HIGH: {high_count}")
        print(f"  CRITICAL: {critical_count}")
        print(f"  Average Risk: {avg_score:.3f}")
        
        return results
    
    def setup_scenarios(self):
        # Setup all test scenarios
        
        base_time = int(time.time())
        daytime = base_time - 43200  # Noon
        nighttime = base_time - 14400  # Around midnight
        
        # ===== SCENARIO 1: SAFE COMMUTE =====
        safe_commute = []
        lat, lon = 21.1458, 79.0882  # Sitabuldi (GREEN)
        
        for i in range(20):
            safe_commute.append({
                'lat': lat + (i * 0.0001),
                'lon': lon + (i * 0.0001),
                'speed': 40 + (i % 5),
                'timestamp': daytime + i * 60,
                'stopped': 0
            })
        
        self.add_scenario(
            name="Safe Commute",
            description="Normal driving through safe zone (Sitabuldi) during daytime",
            points=safe_commute
        )
        
        # ===== SCENARIO 2: RISKY NIGHT DRIVE =====
        risky_night = []
        lat, lon = 21.0976, 78.9772  # MIDC (RED)
        
        for i in range(20):
            risky_night.append({
                'lat': lat + (i * 0.0001),
                'lon': lon + (i * 0.0001),
                'speed': 50 + (i % 10),  # Fast speed
                'timestamp': nighttime + i * 60,
                'stopped': 0
            })
        
        self.add_scenario(
            name="Risky Night Drive",
            description="Fast driving through high-risk zone (MIDC) during night",
            points=risky_night
        )
        
        # ===== SCENARIO 3: SUSPICIOUS STOP =====
        suspicious_stop = []
        lat, lon = 21.0976, 78.9772  # MIDC (RED)
        
        for i in range(20):
            if i < 5:
                # Moving
                speed = 40
                stopped = 0
            elif i < 15:
                # Stopped
                speed = 0
                stopped = (i - 5) * 60  # Increasing stop time
            else:
                # Moving again
                speed = 40
                stopped = 0
            
            suspicious_stop.append({
                'lat': lat,
                'lon': lon,
                'speed': speed,
                'timestamp': nighttime + i * 60,
                'stopped': stopped
            })
        
        self.add_scenario(
            name="Suspicious Stop",
            description="Vehicle stops in high-risk zone (MIDC) at night",
            points=suspicious_stop
        )
        
        # ===== SCENARIO 4: DEVIATION FROM ROUTE =====
        deviation = []
        
        for i in range(20):
            if i < 10:
                # Normal route - safe zone
                lat, lon = 21.1458, 79.0882
                speed = 40
            else:
                # Deviates to risky zone
                lat, lon = 21.0976, 78.9772
                speed = 60  # Faster
            
            deviation.append({
                'lat': lat + (i * 0.0001),
                'lon': lon + (i * 0.0001),
                'speed': speed,
                'timestamp': daytime + i * 60,
                'stopped': 0
            })
        
        self.add_scenario(
            name="Route Deviation",
            description="Vehicle deviates from safe zone to risky zone",
            points=deviation
        )
        
        # ===== SCENARIO 5: SLOW SPEED WARNING =====
        slow_speed = []
        lat, lon = 21.1356, 79.0603  # Dharampeth (GREEN)
        
        for i in range(20):
            slow_speed.append({
                'lat': lat + (i * 0.0001),
                'lon': lon + (i * 0.0001),
                'speed': 5 + (i % 3),  # Very slow
                'timestamp': daytime + i * 60,
                'stopped': 0
            })
        
        self.add_scenario(
            name="Slow Speed Warning",
            description="Vehicle moving very slowly through safe zone",
            points=slow_speed
        )
        
        # ===== SCENARIO 6: MEDIUM ZONE EVENING =====
        medium_evening = []
        lat, lon = 21.0985, 79.0030  # Hingna Road (YELLOW)
        evening_time = base_time - 10800  # 6 PM
        
        for i in range(20):
            medium_evening.append({
                'lat': lat + (i * 0.0001),
                'lon': lon + (i * 0.0001),
                'speed': 35 + (i % 5),
                'timestamp': evening_time + i * 60,
                'stopped': 0
            })
        
        self.add_scenario(
            name="Medium Zone Evening",
            description="Driving through medium-risk zone during evening",
            points=medium_evening
        )
        
        # ===== SCENARIO 7: PANIC STOP =====
        panic_stop = []
        lat, lon = 21.0976, 78.9772  # MIDC (RED)
        
        for i in range(20):
            panic_stop.append({
                'lat': lat,
                'lon': lon,
                'speed': 0 if i >= 5 else 60,  # Sudden stop
                'timestamp': nighttime + i * 60,
                'stopped': max(0, (i - 5) * 60)  # Stopped after point 5
            })
        
        self.add_scenario(
            name="Panic Stop",
            description="Sudden stop in high-risk zone at night",
            points=panic_stop
        )
        
        # ===== SCENARIO 8: EARLY MORNING DRIVE =====
        early_morning = []
        lat, lon = 21.1458, 79.0882  # Sitabuldi (GREEN)
        early_time = base_time - 86400 + 18000  # 5 AM
        
        for i in range(20):
            early_morning.append({
                'lat': lat + (i * 0.0001),
                'lon': lon + (i * 0.0001),
                'speed': 35 + (i % 5),
                'timestamp': early_time + i * 60,
                'stopped': 0
            })
        
        self.add_scenario(
            name="Early Morning Drive",
            description="Driving through safe zone during early morning",
            points=early_morning
        )
    
    def run_all_scenarios(self):
        # Run all scenarios
        
        print("\n\n")
        print("█"*60)
        print("█" + " "*58 + "█")
        print("█" + " "*15 + "RISK MODULE - SCENARIO TESTING" + " "*13 + "█")
        print("█" + " "*58 + "█")
        print("█"*60)
        
        self.setup_scenarios()
        
        all_results = []
        
        for scenario in self.scenarios:
            results = self.run_scenario(scenario)
            all_results.append({
                'scenario': scenario['name'],
                'results': results
            })
        
        # Print final summary
        print("\n\n")
        print("█"*60)
        print("█" + " "*58 + "█")
        print("█" + " "*22 + "OVERALL SUMMARY" + " "*21 + "█")
        print("█" + " "*58 + "█")
        print("█"*60)
        
        print("\nScenario Results:")
        
        for scenario_result in all_results:
            results = scenario_result['results']
            critical_count = sum(1 for r in results if r.level == "CRITICAL")
            high_count = sum(1 for r in results if r.level == "HIGH")
            avg_score = sum(r.score for r in results) / len(results)
            
            print(f"\n  {scenario_result['scenario']}:")
            print(f"    Average Risk: {avg_score:.3f}")
            print(f"    HIGH/CRITICAL: {high_count + critical_count}")
            
            if avg_score > 0.60:
                print(f"    Status: 🚨 CRITICAL")
            elif avg_score > 0.40:
                print(f"    Status: 🔴 HIGH")
            elif avg_score > 0.25:
                print(f"    Status: 🟡 MEDIUM")
            else:
                print(f"    Status: ✅ SAFE")
        
        print("\n" + "█"*60 + "\n")


if __name__ == "__main__":
    tester = RiskScenarioTester()
    tester.run_all_scenarios()