# data_models.py
# This file defines what data we work with

class GPSPoint:
    def __init__(self, lat, lon, speed, timestamp):
        self.latitude = lat
        self.longitude = lon
        self.speed_kmh = speed
        self.timestamp = timestamp


class Zone:
    def __init__(self, name, lat, lon, zone_type, crime_weight):
        self.name = name
        self.lat = lat
        self.lon = lon
        self.zone_type = zone_type  # GREEN, YELLOW, RED
        self.crime_weight = crime_weight


class RiskResult:
    def __init__(self, score, level, zone_name, reasons):
        self.score = score
        self.level = level
        self.zone_name = zone_name
        self.reasons = reasons
    
    def show(self):
        print(f"\nRisk Score: {self.score:.2f}")
        print(f"Risk Level: {self.level}")
        print(f"Zone: {self.zone_name}")
        print(f"Reasons:")
        for reason in self.reasons:
            print(f"  - {reason}")