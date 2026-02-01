# risk_processor.py
# This puts everything together

from data_models import GPSPoint, RiskResult
from zone_classifier import classify_location
from risk_calculator import (
    calculate_total_risk,
    get_risk_level,
    get_risk_reasons
)


class RiskProcessor:
    def __init__(self):
        self.results = []
    
    def process_point(self, lat, lon, speed_kmh, timestamp, stopped_seconds=0):
        # Process one GPS point
        
        # Step 1: Find the zone
        zone_info = classify_location(lat, lon)
        zone_type = zone_info['zone_type']
        zone_name = zone_info['zone_name']
        
        # Step 2: Calculate risk score
        score = calculate_total_risk(
            zone_type,
            timestamp,
            speed_kmh,
            stopped_seconds
        )
        
        # Step 3: Determine risk level
        level = get_risk_level(score)
        
        # Step 4: Get reasons
        reasons = get_risk_reasons(
            zone_type,
            timestamp,
            speed_kmh,
            stopped_seconds,
            score
        )
        
        # Step 5: Create result
        result = RiskResult(score, level, zone_name, reasons)
        self.results.append(result)
        
        return result
    
    def process_multiple(self, data_list):
        # Process multiple GPS points
        
        print(f"\nProcessing {len(data_list)} points...\n")
        
        for i, data in enumerate(data_list):
            result = self.process_point(
                lat=data['lat'],
                lon=data['lon'],
                speed_kmh=data['speed'],
                timestamp=data['timestamp'],
                stopped_seconds=data.get('stopped', 0)
            )
            
            if (i + 1) % 5000 == 0:
                print(f"Processed {i + 1}/{len(data_list)} points")
        
        return self.results
    
    def show_stats(self):
        # Show statistics
        if not self.results:
            print("No results to show")
            return
        
        print("\n" + "="*50)
        print("RISK STATISTICS")
        print("="*50)
        
        total = len(self.results)
        safe_count = sum(1 for r in self.results if r.level == "SAFE")
        low_count = sum(1 for r in self.results if r.level == "LOW")
        medium_count = sum(1 for r in self.results if r.level == "MEDIUM")
        high_count = sum(1 for r in self.results if r.level == "HIGH")
        critical_count = sum(1 for r in self.results if r.level == "CRITICAL")
        
        print(f"\nTotal points: {total}")
        print(f"SAFE: {safe_count} ({safe_count*100/total:.1f}%)")
        print(f"LOW: {low_count} ({low_count*100/total:.1f}%)")
        print(f"MEDIUM: {medium_count} ({medium_count*100/total:.1f}%)")
        print(f"HIGH: {high_count} ({high_count*100/total:.1f}%)")
        print(f"CRITICAL: {critical_count} ({critical_count*100/total:.1f}%)")
        
        avg_score = sum(r.score for r in self.results) / total
        print(f"\nAverage risk score: {avg_score:.3f}")
        print("="*50)