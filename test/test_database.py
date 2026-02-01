# test_database.py
# Test if database is working correctly

from database import Database
from data_generator import DataGenerator
from risk_processor import RiskProcessor
from zone_classifier import classify_location
import os

class DatabaseTester:
    def __init__(self):
        self.db_name = 'test_risk_module.db'
        self.tests_passed = 0
        self.tests_failed = 0
    
    def setup_test_db(self):
        # Create a test database
        
        print("Setting up test database...")
        
        # Remove old test db if exists
        if os.path.exists(self.db_name):
            os.remove(self.db_name)
        
        # Generate small dataset
        generator = DataGenerator()
        data = generator.generate_safe_route(100)
        data.extend(generator.generate_suspicious_stop(50))
        
        # Process through risk module
        processor = RiskProcessor()
        results = processor.process_multiple(data)
        
        # Store in database
        db = Database(self.db_name)
        db.connect()
        db.create_tables()
        db.insert_gps_data(data)
        
        zone_infos = [classify_location(p['lat'], p['lon']) for p in data]
        db.insert_risk_results_batch(data, results, zone_infos)
        
        # Store stats
        total = len(results)
        safe = sum(1 for r in results if r.level == "SAFE")
        low = sum(1 for r in results if r.level == "LOW")
        medium = sum(1 for r in results if r.level == "MEDIUM")
        high = sum(1 for r in results if r.level == "HIGH")
        critical = sum(1 for r in results if r.level == "CRITICAL")
        avg_risk = sum(r.score for r in results) / total if total > 0 else 0
        
        db.insert_statistics(total, safe, low, medium, high, critical, avg_risk)
        db.close()
        
        print(f"Test database created with {total} records\n")
    
    def test_connection(self):
        # Test: Can connect to database
        
        print("Test 1: Database Connection")
        try:
            db = Database(self.db_name)
            db.connect()
            db.close()
            print("  ✅ PASSED - Database connection works\n")
            self.tests_passed += 1
            return True
        except Exception as e:
            print(f"  ❌ FAILED - {e}\n")
            self.tests_failed += 1
            return False
    
    def test_gps_data_count(self):
        # Test: GPS data was inserted
        
        print("Test 2: GPS Data Insertion")
        try:
            db = Database(self.db_name)
            db.connect()
            
            db.cursor.execute('SELECT COUNT(*) FROM gps_data')
            count = db.cursor.fetchone()[0]
            
            db.close()
            
            if count > 0:
                print(f"  ✅ PASSED - {count} GPS records found\n")
                self.tests_passed += 1
                return True
            else:
                print(f"  ❌ FAILED - No GPS records found\n")
                self.tests_failed += 1
                return False
        except Exception as e:
            print(f"  ❌ FAILED - {e}\n")
            self.tests_failed += 1
            return False
    
    def test_risk_results_count(self):
        # Test: Risk results were calculated
        
        print("Test 3: Risk Results Calculation")
        try:
            db = Database(self.db_name)
            db.connect()
            
            db.cursor.execute('SELECT COUNT(*) FROM risk_results')
            count = db.cursor.fetchone()[0]
            
            db.close()
            
            if count > 0:
                print(f"  ✅ PASSED - {count} risk results found\n")
                self.tests_passed += 1
                return True
            else:
                print(f"  ❌ FAILED - No risk results found\n")
                self.tests_failed += 1
                return False
        except Exception as e:
            print(f"  ❌ FAILED - {e}\n")
            self.tests_failed += 1
            return False
    
    def test_risk_distribution(self):
        # Test: Risk levels are distributed
        
        print("Test 4: Risk Level Distribution")
        try:
            db = Database(self.db_name)
            db.connect()
            
            db.cursor.execute('''
                SELECT risk_level, COUNT(*) FROM risk_results
                GROUP BY risk_level
            ''')
            
            results = db.cursor.fetchall()
            db.close()
            
            print(f"  Distribution:")
            for level, count in results:
                print(f"    {level}: {count}")
            
            print("  ✅ PASSED - Risk levels are distributed\n")
            self.tests_passed += 1
            return True
        except Exception as e:
            print(f"  ❌ FAILED - {e}\n")
            self.tests_failed += 1
            return False
    
    def test_statistics(self):
        # Test: Statistics were stored
        
        print("Test 5: Statistics Storage")
        try:
            db = Database(self.db_name)
            db.connect()
            
            stats = db.get_statistics()
            db.close()
            
            if stats:
                print(f"  Statistics found:")
                print(f"    Total: {stats[1]}")
                print(f"    Average Risk: {stats[7]:.3f}")
                print("  ✅ PASSED - Statistics stored\n")
                self.tests_passed += 1
                return True
            else:
                print(f"  ❌ FAILED - No statistics found\n")
                self.tests_failed += 1
                return False
        except Exception as e:
            print(f"  ❌ FAILED - {e}\n")
            self.tests_failed += 1
            return False
    
    def test_query_by_level(self):
        # Test: Can query by risk level
        
        print("Test 6: Query by Risk Level")
        try:
            db = Database(self.db_name)
            db.connect()
            
            critical = db.get_results_by_level('CRITICAL')
            high = db.get_results_by_level('HIGH')
            safe = db.get_results_by_level('SAFE')
            
            db.close()
            
            print(f"  CRITICAL: {len(critical)}")
            print(f"  HIGH: {len(high)}")
            print(f"  SAFE: {len(safe)}")
            print("  ✅ PASSED - Query by level works\n")
            self.tests_passed += 1
            return True
        except Exception as e:
            print(f"  ❌ FAILED - {e}\n")
            self.tests_failed += 1
            return False
    
    def test_export_csv(self):
        # Test: Can export to CSV
        
        print("Test 7: Export to CSV")
        try:
            db = Database(self.db_name)
            db.connect()
            
            db.export_to_csv('test_export.csv')
            
            db.close()
            
            if os.path.exists('test_export.csv'):
                print("  ✅ PASSED - CSV export works\n")
                self.tests_passed += 1
                return True
            else:
                print(f"  ❌ FAILED - CSV not created\n")
                self.tests_failed += 1
                return False
        except Exception as e:
            print(f"  ❌ FAILED - {e}\n")
            self.tests_failed += 1
            return False
    
    def run_all_tests(self):
        # Run all database tests
        
        print("\n" + "="*60)
        print("DATABASE TESTS")
        print("="*60 + "\n")
        
        self.setup_test_db()
        self.test_connection()
        self.test_gps_data_count()
        self.test_risk_results_count()
        self.test_risk_distribution()
        self.test_statistics()
        self.test_query_by_level()
        self.test_export_csv()
        
        # Print summary
        total = self.tests_passed + self.tests_failed
        passed_pct = (self.tests_passed / total * 100) if total > 0 else 0
        
        print("="*60)
        print("TEST SUMMARY")
        print("="*60)
        
        print(f"\nTotal Tests: {total}")
        print(f"Passed: {self.tests_passed} ({passed_pct:.1f}%)")
        print(f"Failed: {self.tests_failed}")
        
        if passed_pct == 100:
            print("\n✅ ALL DATABASE TESTS PASSED!")
        elif passed_pct >= 80:
            print("\n✅ GOOD - Most database tests passed")
        else:
            print("\n❌ Some database tests failed")
        
        print("="*60 + "\n")


if __name__ == "__main__":
    tester = DatabaseTester()
    tester.run_all_tests()