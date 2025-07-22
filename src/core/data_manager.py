"""
Data Manager
Handles humidity data storage and retrieval using JSON files
"""

import json
import os
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from pathlib import Path

from ..utils.constants import DATA_DIR, DATA_FILE, DATETIME_FORMAT
from ..utils.helpers import parse_datetime, format_datetime, get_time_range

class DataManager:
    """Manages humidity data storage and retrieval"""
    
    def __init__(self):
        self.data_path = Path(DATA_DIR) / DATA_FILE
        self._ensure_data_file()
    
    def _ensure_data_file(self) -> None:
        """Ensure data file and directory exist"""
        # Create data directory if it doesn't exist
        self.data_path.parent.mkdir(exist_ok=True)
        
        # Create data file if it doesn't exist
        if not self.data_path.exists():
            self._save_data([])
    
    def _load_data(self) -> List[Dict[str, Any]]:
        """Load data from JSON file"""
        try:
            with open(self.data_path, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return []
    
    def _save_data(self, data: List[Dict[str, Any]]) -> None:
        """Save data to JSON file"""
        try:
            with open(self.data_path, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving data: {e}")
    
    def add_reading(self, humidity: float, temperature: Optional[float] = None, 
                   timestamp: Optional[datetime] = None) -> None:
        """Add a new humidity reading"""
        if timestamp is None:
            timestamp = datetime.now()
        
        reading = {
            "timestamp": format_datetime(timestamp),
            "humidity": round(humidity, 2),
            "temperature": round(temperature, 2) if temperature is not None else None
        }
        
        data = self._load_data()
        data.append(reading)
        
        # Optional: Limit data size (keep last N records)
        max_records = 10000  # This could be configurable
        if len(data) > max_records:
            data = data[-max_records:]
        
        self._save_data(data)
    
    def get_all_readings(self) -> List[Dict[str, Any]]:
        """Get all humidity readings"""
        return self._load_data()
    
    def get_recent_readings(self, count: int = 50) -> List[Dict[str, Any]]:
        """Get the most recent N readings"""
        data = self._load_data()
        return data[-count:] if len(data) > count else data
    
    def get_readings_by_period(self, period: str = "daily") -> List[Dict[str, Any]]:
        """Get readings for a specific time period"""
        start_time, end_time = get_time_range(period)
        data = self._load_data()
        
        filtered_data = []
        for reading in data:
            try:
                reading_time = parse_datetime(reading["timestamp"])
                if start_time <= reading_time < end_time:
                    filtered_data.append(reading)
            except (ValueError, KeyError):
                continue
        
        return filtered_data
    
    def get_readings_by_date_range(self, start_date: str, end_date: str) -> List[Dict[str, Any]]:
        """Get readings within a date range"""
        try:
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
            end_dt = datetime.strptime(end_date, "%Y-%m-%d") + timedelta(days=1)
        except ValueError:
            return []
        
        data = self._load_data()
        filtered_data = []
        
        for reading in data:
            try:
                reading_dt = parse_datetime(reading["timestamp"])
                if start_dt <= reading_dt < end_dt:
                    filtered_data.append(reading)
            except (ValueError, KeyError):
                continue
        
        return filtered_data
    
    def get_latest_reading(self) -> Optional[Dict[str, Any]]:
        """Get the most recent reading"""
        data = self._load_data()
        return data[-1] if data else None
    
    def get_statistics(self, period: str = "daily") -> Dict[str, Any]:
        """Get statistics for a given period"""
        data = self.get_readings_by_period(period)
        
        if not data:
            return {
                "count": 0,
                "average": 0.0,
                "min": 0.0,
                "max": 0.0,
                "current": 0.0,
                "trend": 0.0
            }
        
        humidity_values = [reading["humidity"] for reading in data]
        
        # Calculate trend (compare last 25% with first 25%)
        trend = 0.0
        if len(humidity_values) >= 4:
            quarter = len(humidity_values) // 4
            recent_avg = sum(humidity_values[-quarter:]) / quarter
            early_avg = sum(humidity_values[:quarter]) / quarter
            if early_avg != 0:
                trend = ((recent_avg - early_avg) / early_avg) * 100
        
        return {
            "count": len(data),
            "average": sum(humidity_values) / len(humidity_values),
            "min": min(humidity_values),
            "max": max(humidity_values),
            "current": humidity_values[-1],
            "trend": trend
        }
    
    def cleanup_old_data(self, days_to_keep: int = 30) -> int:
        """Remove data older than specified days"""
        cutoff_date = datetime.now() - timedelta(days=days_to_keep)
        data = self._load_data()
        
        original_count = len(data)
        filtered_data = []
        
        for reading in data:
            try:
                reading_time = parse_datetime(reading["timestamp"])
                if reading_time >= cutoff_date:
                    filtered_data.append(reading)
            except (ValueError, KeyError):
                # Keep readings with invalid timestamps
                filtered_data.append(reading)
        
        self._save_data(filtered_data)
        return original_count - len(filtered_data)
    
    def export_data(self, format_type: str = "csv", start_date: Optional[str] = None,
                   end_date: Optional[str] = None) -> str:
        """Export data in specified format"""
        if start_date and end_date:
            data = self.get_readings_by_date_range(start_date, end_date)
        else:
            data = self.get_all_readings()
        
        if format_type.lower() == "csv":
            lines = ["timestamp,humidity,temperature"]
            for reading in data:
                temp = reading.get("temperature", "")
                lines.append(f"{reading['timestamp']},{reading['humidity']},{temp}")
            return "\n".join(lines)
        
        elif format_type.lower() == "json":
            return json.dumps(data, indent=2)
        
        else:
            raise ValueError(f"Unsupported export format: {format_type}")
    
    def clear_all_data(self) -> None:
        """Clear all stored data"""
        self._save_data([])
