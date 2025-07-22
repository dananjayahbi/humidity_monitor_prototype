"""
Helper Functions
Utility functions for the application
"""

import re
import time
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

# Update parsing logic to handle edge cases
def parse_humidity_from_serial(line: str) -> Optional[float]:
    match = re.search(r"Humidity:\s*([\d.]+)", line)
    if match:
        try:
            humidity = float(match.group(1))
            # Ensure humidity is within a valid range
            if 0 <= humidity <= 100:
                return humidity
        except ValueError:
            pass
    return None

def format_timestamp(timestamp: Optional[datetime] = None) -> str:
    """Format timestamp for display"""
    if timestamp is None:
        timestamp = datetime.now()
    return timestamp.strftime("%H:%M:%S")

def format_date(date: Optional[datetime] = None) -> str:
    """Format date for display"""
    if date is None:
        date = datetime.now()
    return date.strftime("%Y-%m-%d")

def format_datetime(dt: Optional[datetime] = None) -> str:
    """Format datetime for storage"""
    if dt is None:
        dt = datetime.now()
    return dt.strftime("%Y-%m-%d %H:%M:%S")

def parse_datetime(dt_string: str) -> datetime:
    """Parse datetime string"""
    return datetime.strptime(dt_string, "%Y-%m-%d %H:%M:%S")

def get_time_range(period: str) -> tuple:
    """Get start and end datetime for a given period"""
    now = datetime.now()
    
    if period == "daily":
        start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        end = start + timedelta(days=1)
    elif period == "weekly":
        days_since_monday = now.weekday()
        start = (now - timedelta(days=days_since_monday)).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        end = start + timedelta(days=7)
    elif period == "monthly":
        start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        if now.month == 12:
            end = start.replace(year=now.year + 1, month=1)
        else:
            end = start.replace(month=now.month + 1)
    else:
        # Default to daily
        start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        end = start + timedelta(days=1)
    
    return start, end

def filter_data_by_date_range(data: List[Dict], start_date: str, end_date: str) -> List[Dict]:
    """Filter data by date range"""
    try:
        start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        end_dt = datetime.strptime(end_date, "%Y-%m-%d") + timedelta(days=1)
        
        filtered_data = []
        for record in data:
            record_dt = parse_datetime(record["timestamp"])
            if start_dt <= record_dt < end_dt:
                filtered_data.append(record)
        
        return filtered_data
    except (ValueError, KeyError):
        return data

def calculate_humidity_stats(data: List[Dict]) -> Dict[str, Any]:
    """Calculate humidity statistics"""
    if not data:
        return {
            "current": 0.0,
            "average": 0.0,
            "min": 0.0,
            "max": 0.0,
            "count": 0,
            "trend": 0.0
        }
    
    values = [record["humidity"] for record in data]
    current = values[-1] if values else 0.0
    
    # Calculate trend (last 5 vs previous 5 readings)
    trend = 0.0
    if len(values) >= 10:
        recent_avg = sum(values[-5:]) / 5
        previous_avg = sum(values[-10:-5]) / 5
        trend = ((recent_avg - previous_avg) / previous_avg) * 100 if previous_avg != 0 else 0.0
    
    return {
        "current": current,
        "average": sum(values) / len(values),
        "min": min(values),
        "max": max(values),
        "count": len(values),
        "trend": trend
    }

def convert_humidity_unit(value: float, from_unit: str, to_unit: str, 
                         temperature: float = 20.0) -> float:
    """Convert humidity between percentage and absolute units"""
    if from_unit == to_unit:
        return value
    
    # Simplified conversion - in real application, would need more accurate formulas
    if from_unit == "percentage" and to_unit == "absolute":
        # Rough conversion from % to g/m³ at given temperature
        return value * 0.17  # Simplified factor
    elif from_unit == "absolute" and to_unit == "percentage":
        # Rough conversion from g/m³ to % at given temperature
        return value / 0.17  # Simplified factor
    
    return value

def validate_threshold_values(low: float, high: float) -> tuple:
    """Validate and correct threshold values"""
    # Ensure values are within valid range
    low = max(0.0, min(100.0, low))
    high = max(0.0, min(100.0, high))
    
    # Ensure low < high
    if low >= high:
        high = low + 5.0
        if high > 100.0:
            high = 100.0
            low = high - 5.0
    
    return low, high
