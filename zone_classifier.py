# zone_classifier.py
# This classifies where a location is

import math
from data_models import Zone

# Nagpur zones
ZONES = [
    # GREEN - Safe zones
    Zone("Sitabuldi", 21.1458, 79.0882, "GREEN", 0.20),
    Zone("Dharampeth", 21.1356, 79.0603, "GREEN", 0.20),
    Zone("Civil Lines", 21.1541, 79.0735, "GREEN", 0.22),
    
    # YELLOW - Medium risk
    Zone("Manewada", 21.0950, 79.1200, "YELLOW", 0.42),
    Zone("Hingna Road", 21.0985, 79.0030, "YELLOW", 0.48),
    Zone("Railway Station", 21.1450, 79.0800, "YELLOW", 0.52),
    
    # RED - High risk
    Zone("MIDC Industrial", 21.0976, 78.9772, "RED", 0.78),
    Zone("Outer Ring Road", 21.1850, 79.2300, "RED", 0.85),
    Zone("Butibori", 21.0530, 79.1800, "RED", 0.75),
]


def distance_between(lat1, lon1, lat2, lon2):
    # Calculate distance in km between two locations
    earth_radius = 6371  # km
    
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)
    
    a = math.sin(delta_lat / 2) ** 2
    a += math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon / 2) ** 2
    
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = earth_radius * c
    
    return distance


def find_nearest_zone(lat, lon):
    # Find which zone a location is in
    nearest_zone = None
    min_distance = 999999
    
    for zone in ZONES:
        dist = distance_between(lat, lon, zone.lat, zone.lon)
        
        if dist < min_distance:
            min_distance = dist
            nearest_zone = zone
    
    return nearest_zone, min_distance


def classify_location(lat, lon):
    # Classify a location into a zone
    zone, distance = find_nearest_zone(lat, lon)
    
    return {
        'zone_name': zone.name,
        'zone_type': zone.zone_type,
        'crime_weight': zone.crime_weight,
        'distance_km': round(distance, 2)
    }