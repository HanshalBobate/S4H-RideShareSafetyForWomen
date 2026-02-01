# run_all_tests.py
# Run all tests at once

from test.test_accuracy import AccuracyTester
from test.test_database import DatabaseTester
from test.test_zone_classification import ZoneClassificationTester

def main():
    print("\n\n")
    print("█"*60)
    print("█" + " "*58 + "█")
    print("█" + " "*15 + "COMPLETE RISK MODULE TEST SUITE" + " "*12 + "█")
    print("█" + " "*58 + "█")
    print("█"*60)
    
    # Test 1: Zone Classification
    print("\n\n[TEST 1] ZONE CLASSIFICATION")
    zone_tester = ZoneClassificationTester()
    zone_tester.run_all_tests()
    
    # Test 2: Accuracy
    print("\n\n[TEST 2] RISK CALCULATION ACCURACY")
    accuracy_tester = AccuracyTester()
    accuracy_tester.run_all_tests()
    
    # Test 3: Database
    print("\n\n[TEST 3] DATABASE FUNCTIONALITY")
    db_tester = DatabaseTester()
    db_tester.run_all_tests()
    
    # Overall summary
    print("\n\n")
    print("█"*60)
    print("█" + " "*58 + "█")
    print("█" + " "*20 + "OVERALL TEST SUMMARY" + " "*18 + "█")
    print("█" + " "*58 + "█")
    print("█"*60)
    
    total_tests = (zone_tester.tests_passed + zone_tester.tests_failed +
                   accuracy_tester.tests_passed + accuracy_tester.tests_failed +
                   db_tester.tests_passed + db_tester.tests_failed)
    
    total_passed = (zone_tester.tests_passed + 
                    accuracy_tester.tests_passed + 
                    db_tester.tests_passed)
    
    passed_pct = (total_passed / total_tests * 100) if total_tests > 0 else 0
    
    print(f"\nTotal Tests: {total_tests}")
    print(f"Passed: {total_passed} ({passed_pct:.1f}%)")
    print(f"Failed: {total_tests - total_passed}")
    
    if passed_pct == 100:
        print("\n✅ ALL TESTS PASSED - SYSTEM READY FOR PRODUCTION!")
    elif passed_pct >= 90:
        print("\n✅ EXCELLENT - System is working well")
    elif passed_pct >= 80:
        print("\n⚠️ GOOD - Most tests passed, minor issues")
    else:
        print("\n❌ CRITICAL - Several tests failed, needs fixing")
    
    print("\n" + "█"*60 + "\n")


if __name__ == "__main__":
    main()