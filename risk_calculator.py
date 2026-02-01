# risk_calculator.py
# This calculates the risk score

from datetime import datetime

# Risk scores for each zone type
ZONE_SCORES = {
    'GREEN': 0.20,
    'YELLOW': 0.50,
    'RED': 0.80
}


def get_time_risk(timestamp):
    # Calculate risk based on time of day
    dt = datetime.fromtimestamp(timestamp)
    hour = dt.hour
    
    if hour >= 6 and hour <= 21:
        # Daytime (6 AM to 9 PM) - low risk
        return 0.10
    elif hour > 21 and hour <= 24:
        # Evening (9 PM to Midnight) - medium risk
        return 0.30
    else:
        # Night (Midnight to 6 AM) - high risk
        return 0.60


def get_speed_risk(speed_kmh):
    # Calculate risk based on speed
    if speed_kmh > 30:
        # Normal speed - low risk
        return 0.10
    elif speed_kmh > 10:
        # Slow speed - medium risk
        return 0.30
    else:
        # Very slow/stopped - high risk
        return 0.60


def get_stop_risk(stopped_seconds):
    # Calculate risk based on how long stopped
    if stopped_seconds < 30:
        # Brief stop - low risk
        return 0.10
    elif stopped_seconds < 120:
        # Medium stop - medium risk
        return 0.40
    else:
        # Long stop - high risk
        return 0.70


def calculate_total_risk(zone_type, timestamp, speed_kmh, stopped_seconds):
    # Calculate overall risk score
    
    zone_risk = ZONE_SCORES[zone_type]
    time_risk = get_time_risk(timestamp)
    speed_risk = get_speed_risk(speed_kmh)
    stop_risk = get_stop_risk(stopped_seconds)
    
    # Weighted formula
    total_risk = (
        zone_risk * 0.40 +      # Zone is 40%
        time_risk * 0.20 +      # Time is 20%
        speed_risk * 0.15 +     # Speed is 15%
        stop_risk * 0.25        # Stop is 25%
    )
    
    return round(total_risk, 3)


def get_risk_level(score):
    # Convert score to text level
    if score >= 0.70:
        return "CRITICAL"
    elif score >= 0.50:
        return "HIGH"
    elif score >= 0.30:
        return "MEDIUM"
    elif score >= 0.15:
        return "LOW"
    else:
        return "SAFE"


def get_risk_reasons(zone_type, timestamp, speed_kmh, stopped_seconds, score):
    # Explain why risk is high
    reasons = []
    
    # Zone reason
    if zone_type == "RED":
        reasons.append("In high-risk zone (RED)")
    elif zone_type == "YELLOW":
        reasons.append("In medium-risk zone (YELLOW)")
    
    # Time reason
    dt = datetime.fromtimestamp(timestamp)
    hour = dt.hour
    if hour >= 22 or hour < 5:
        reasons.append("Traveling at night (10 PM - 5 AM)")
    
    # Speed reason
    if speed_kmh < 10:
        reasons.append("Vehicle moving very slowly or stopped")
    
    # Stop reason
    if stopped_seconds > 300:
        reasons.append(f"Stopped for {stopped_seconds} seconds")
    
    return reasons