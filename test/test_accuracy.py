# test_accuracy.py
# Test if risk calculations are correct

from risk_processor import RiskProcessor
from zone_classifier import classify_location
from risk_calculator import calculate_total_risk, get_risk_level
import time

class AccuracyTester:
    def __init__(self):
        self.processor = RiskProcessor()
        self.tests_passed = 0
        self.tests_failed = 0
        self.test_results = []
    
    def test_case(self, name, lat, lon, speed, timestamp, stopped, expected_level, expected_min_score, expected_max_score):
        # Run one test case
        
        print(f"\nTest: {name}")
        print(f"  Location: ({lat}, {lon})")
        print(f"  Speed: {speed} km/h, Stopped: {stopped}s")
        
        # Process the point
        result = self.processor.process_point(lat, lon, speed, timestamp, stopped)
        
        # Check results
        zone_info = classify_location(lat, lon)
        print(f"  Zone: {result.zone_name} ({zone_info['zone_type']})")
        print(f"  Risk Score: {result.score:.3f} (expected: {expected_min_score:.3f} - {expected_max_score:.3f})")
        print(f"  Risk Level: {result.level} (expected: {expected_level})")
        
        # Validate
        level_ok = result.level == expected_level
        score_ok = expected_min_score <= result.score <= expected_max_score
        
        if level_ok and score_ok:
            print("  ✅ PASSED")
            self.tests_passed += 1
            self.test_results.append({
                'name': name,
                'status': 'PASSED',
                'result': result
            })
        else:
            print("  ❌ FAILED")
            self.tests_failed += 1
            self.test_results.append({
                'name': name,
                'status': 'FAILED',
                'result': result,
                'expected_level': expected_level,
                'expected_score_range': (expected_min_score, expected_max_score)
            })
    
    def run_all_tests(self):
        # Run all test cases
        
        current_time = int(time.time())
        
        print("\n" + "="*60)
        print("ACCURACY TESTS - RISK MODULE")
        print("="*60)
        
        # Test 1: Safe zone, daytime, normal speed
        self.test_case(
            name="Safe Zone - Daytime - Normal Speed",
            lat=21.1458,  # Sitabuldi (GREEN)
            lon=79.0882,
            speed=40,
            timestamp=current_time,
            stopped=0,
            expected_level="SAFE",
            expected_min_score=0.10,
            expected_max_score=0.20
        )
        
        # Test 2: Safe zone, evening, slow speed
        self.test_case(
            name="Safe Zone - Evening - Slow Speed",
            lat=21.1458,
            lon=79.0882,
            speed=15,
            timestamp=current_time,
            stopped=0,
            expected_level="LOW",
            expected_min_score=0.15,
            expected_max_score=0.30
        )
        
        # Test 3: Medium zone, daytime, stopped
        self.test_case(
            name="Medium Zone - Daytime - Stopped (60s)",
            lat=21.0985,  # Hingna Road (YELLOW)
            lon=79.0030,
            speed=0,
            timestamp=current_time,
            stopped=60,
            expected_level="MEDIUM",
            expected_min_score=0.25,
            expected_max_score=0.45
        )
        
        # Test 4: High risk zone, daytime, normal speed
        self.test_case(
            name="High Risk Zone - Daytime - Normal Speed",
            lat=21.0976,  # MIDC (RED)
            lon=78.9772,
            speed=40,
            timestamp=current_time,
            stopped=0,
            expected_level="MEDIUM",
            expected_min_score=0.30,
            expected_max_score=0.40
        )
        
        # Test 5: High risk zone, night, stopped long
        self.test_case(
            name="High Risk Zone - Night - Long Stop (300s)",
            lat=21.0976,
            lon=78.9772,
            speed=0,
            timestamp=current_time - 14400,  # 4 hours ago (around midnight)
            stopped=300,
            expected_level="HIGH",
            expected_min_score=0.50,
            expected_max_score=0.70
        )
        
        # Test 6: High risk zone, night, very slow
        self.test_case(
            name="High Risk Zone - Night - Very Slow Speed",
            lat=21.0976,
            lon=78.9772,
            speed=5,
            timestamp=current_time - 14400,  # Night time
            stopped=0,
            expected_level="CRITICAL",
            expected_min_score=0.70,
            expected_max_score=1.00
        )
        
        # Test 7: Medium zone, night, normal speed
        self.test_case(
            name="Medium Zone - Night - Normal Speed",
            lat=21.0985,
            lon=79.0030,
            speed=40,
            timestamp=current_time - 14400,  # Night
            stopped=0,
            expected_level="MEDIUM",
            expected_min_score=0.25,
            expected_max_score=0.45
        )
        
        # Test 8: Safe zone, night, stopped medium
        self.test_case(
            name="Safe Zone - Night - Medium Stop (120s)",
            lat=21.1458,
            lon=79.0882,
            speed=0,
            timestamp=current_time - 14400,  # Night
            stopped=120,
            expected_level="LOW",
            expected_min_score=0.15,
            expected_max_score=0.35
        )
        
        # Print summary
        self.print_summary()
    
    def print_summary(self):
        # Print test summary
        
        print("\n" + "="*60)
        print("TEST SUMMARY")
        print("="*60)
        
        total = self.tests_passed + self.tests_failed
        passed_pct = (self.tests_passed / total * 100) if total > 0 else 0
        
        print(f"\nTotal Tests: {total}")
        print(f"Passed: {self.tests_passed} ({passed_pct:.1f}%)")
        print(f"Failed: {self.tests_failed}")
        
        if self.tests_failed > 0:
            print("\nFailed Tests:")
            for test in self.test_results:
                if test['status'] == 'FAILED':
                    print(f"\n  ❌ {test['name']}")
                    print(f"     Got: {test['result'].level} ({test['result'].score:.3f})")
                    print(f"     Expected: {test['expected_level']} ({test['expected_score_range'][0]:.3f} - {test['expected_score_range'][1]:.3f})")
        
        if passed_pct == 100:
            print("\n✅ ALL TESTS PASSED!")
        elif passed_pct >= 80:
            print("\n✅ GOOD - Most tests passed")
        elif passed_pct >= 60:
            print("\n⚠️ WARNING - Some issues found")
        else:
            print("\n❌ CRITICAL - Many tests failed")
        
        print("="*60)


if __name__ == "__main__":
    tester = Accura