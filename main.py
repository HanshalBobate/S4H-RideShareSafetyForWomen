# main.py
# Main script with database

import time
from data_generator import DataGenerator
from risk_processor import RiskProcessor
from database import Database
from zone_classifier import classify_location

def main():
    print("="*60)
    print("RISK MODULE - DATA GENERATOR + RISK CALCULATOR + DATABASE")
    print("="*60)
    
    # Step 1: Generate data
    print("\n[STEP 1] GENERATING DATA\n")
    
    generator = DataGenerator()
    data = generator.generate_20000_points()
    
    # Step 2: Connect to database
    print("\n[STEP 2] CONNECTING TO DATABASE\n")
    
    db = Database('risk_module.db')
    db.connect()
    db.create_tables()
    
    # Step 3: Insert GPS data
    print("\n[STEP 3] STORING GPS DATA IN DATABASE\n")
    
    db.insert_gps_data(data)
    
    # Step 4: Calculate risk for all points
    print("\n[STEP 4] CALCULATING RISK\n")
    
    processor = RiskProcessor()
    results = processor.process_multiple(data)
    
    # Get zone info for each result
    zone_infos = []
    for point in data:
        zone_info = classify_location(point['lat'], point['lon'])
        zone_infos.append(zone_info)
    
    # Step 5: Store risk results in database
    print("\n[STEP 5] STORING RISK RESULTS IN DATABASE\n")
    
    db.insert_risk_results_batch(data, results, zone_infos)
    
    # Step 6: Calculate and store statistics
    print("\n[STEP 6] CALCULATING STATISTICS\n")
    
    processor.show_stats()
    
    total = len(results)
    safe = sum(1 for r in results if r.level == "SAFE")
    low = sum(1 for r in results if r.level == "LOW")
    medium = sum(1 for r in results if r.level == "MEDIUM")
    high = sum(1 for r in results if r.level == "HIGH")
    critical = sum(1 for r in results if r.level == "CRITICAL")
    avg_risk = sum(r.score for r in results) / total
    
    db.insert_statistics(total, safe, low, medium, high, critical, avg_risk)
    
    # Step 7: Show high risk zones
    print("\n[STEP 7] HIGH RISK ZONES\n")
    
    high_risk_zones = db.get_high_risk_zones()
    print("Zones with most HIGH/CRITICAL incidents:")
    for zone_name, count, avg_risk in high_risk_zones[:10]:
        print(f"  {zone_name}: {count} incidents (avg risk: {avg_risk:.3f})")
    
    # Step 8: Export to CSV
    print("\n[STEP 8] EXPORTING TO CSV\n")
    
    db.export_to_csv('risk_results_from_db.csv')
    
    # Step 9: Show summary
    print("\n[STEP 9] DATABASE SUMMARY\n")
    
    db.show_summary()
    
    # Close database
    db.close()
    
    print("="*60)
    print("DONE!")
    print("="*60)
    print("\nGenerated files:")
    print("  1. risk_module.db - SQLite database")
    print("  2. risk_results_from_db.csv - Risk results in CSV")


if __name__ == "__main__":
    main()