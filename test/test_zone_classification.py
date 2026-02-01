# test_zone_classification.py
# Test if zone classification is correct

from zone_classifier import classify_location, ZONES

class ZoneClassificationTester:
    def __init__(self):
        self.tests_passed = 0
        self.tests_failed = 0
    
    def test_zone(self, name, lat, lon, expected_zone_type):
        # Test one zone classification
        
        print(f"\nTest: {name}")
        print(f"  Location: ({lat}, {lon})")
        
        result = classify_location(lat, lon)
        
        print(f"  Classified as: {result['zone_name']} ({result['zone_type']})")
        print(f"  Expected: {expected_zone_type}")
        
        if result['zone_type'] == expected_zone_type:
            print("  ✅ PASSED")
            self.tests_passed += 1
        else:
            print("  ❌ FAILED")
            self.tests_failed += 1
    
    def run_all_tests(self):
        # Run all zone tests
        
        print("\n" + "="*60)
        print("ZONE CLASSIFICATION TESTS")
        print("="*60)
        
        # Test GREEN zones
        print("\n--- GREEN ZONES ---")
        self.test_zone("Sitabuldi", 21.1458, 79.0882, "GREEN")
        self.test_zone("Dharampeth", 21.1356, 79.0603, "GREEN")
        self.test_zone("Civil Lines", 21.1541, 79.0735, "GREEN")
        
        # Test YELLOW zones
        print("\n--- YELLOW ZONES ---")
        self.test_zone("Manewada", 21.0950, 79.1200, "YELLOW")
        self.test_zone("Hingna Road", 21.0985, 79.0030, "YELLOW")
        self.test_zone("Railway Station", 21.1450, 79.0800, "YELLOW")
        
        # Test RED zones
        print("\n--- RED ZONES ---")
        self.test_zone("MIDC Industrial", 21.0976, 78.9772, "RED")
        self.test_zone("Outer Ring Road", 21.1850, 79.2300, "RED")
        self.test_zone("Butibori", 21.0530, 79.1800, "RED")
        
        # Print summary
        total = self.tests_passed + self.tests_failed
        passed_pct = (self.tests_passed / total * 100) if total > 0 else 0
        
        print("\n" + "="*60)
        print("TEST SUMMARY")
        print("="*60)
        
        print(f"\nTotal Tests: {total}")
        print(f"Passed: {self.tests_passed} ({passed_pct:.1f}%)")
        print(f"Failed: {self.tests_failed}")
        
        if passed_pct == 100:
            print("\n✅ ALL ZONE TESTS PASSED!")
        else:
            print("\n❌ Some zone tests failed")
        
        print("="*60 + "\n")


if __name__ == "__main__":
    tester = ZoneClassificationTester()
    tester.run_all_tests()