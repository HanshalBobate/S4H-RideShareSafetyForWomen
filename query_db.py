# query_db.py
# Query the database

from database import Database

def main():
    db = Database('risk_module.db')
    db.connect()
    
    print("\n" + "="*60)
    print("DATABASE QUERIES")
    print("="*60)
    
    # Query 1: Show summary
    print("\n[Query 1] Database Summary:")
    db.show_summary()
    
    # Query 2: Get CRITICAL risk points
    print("\n[Query 2] CRITICAL Risk Points (first 5):")
    critical = db.get_results_by_level('CRITICAL')
    for i, row in enumerate(critical[:5]):
        print(f"\n  {i+1}. Zone: {row[3]}, Score: {row[2]:.3f}")
        print(f"     Reasons: {row[6]}")
    
    # Query 3: Get HIGH risk zones
    print("\n[Query 3] High Risk Zones:")
    high_zones = db.get_high_risk_zones()
    for zone, count, avg_risk in high_zones[:5]:
        print(f"  {zone}: {count} incidents (avg: {avg_risk:.3f})")
    
    # Query 4: Get statistics
    print("\n[Query 4] Statistics:")
    stats = db.get_statistics()
    if stats:
        print(f"  Total: {stats[1]}")
        print(f"  SAFE: {stats[2]}")
        print(f"  LOW: {stats[3]}")
        print(f"  MEDIUM: {stats[4]}")
        print(f"  HIGH: {stats[5]}")
        print(f"  CRITICAL: {stats[6]}")
        print(f"  Average Risk: {stats[7]:.3f}")
    
    # Query 5: Export results by zone
    print("\n[Query 5] Exporting MIDC results...")
    db.export_to_csv(
        'midc_results.csv',
        "SELECT * FROM risk_results WHERE zone_name = 'MIDC Industrial'"
    )
    
    db.close()
    
    print("\n" + "="*60)
    print("Done!")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()