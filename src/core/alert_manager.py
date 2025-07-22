"""
Alert Manager
Handles threshold monitoring and notification system
"""

import time
from datetime import datetime, timedelta
from typing import Optional, Callable, Dict, Any
import threading
import os
import json

class AlertManager:
    """Manages humidity alerts and notifications"""
    
    def __init__(self, config_manager, notification_callback: Optional[Callable] = None):
        self.config_manager = config_manager
        self.notification_callback = notification_callback
        self.last_alert_time: Dict[str, datetime] = {}
        self.alert_active: Dict[str, bool] = {"high": False, "low": False}
        self.monitoring = False
    
    def check_thresholds(self, humidity: float) -> None:
        """Check humidity against thresholds and trigger alerts"""
        if not self.config_manager.get("alerts.enabled", True):
            return
        
        thresholds = self.config_manager.get_thresholds()
        cooldown = self.config_manager.get("alerts.cooldown_period", 300)
        
        current_time = datetime.now()
        
        # Check high threshold
        if humidity > thresholds["high"]:
            self._handle_threshold_breach(
                "high", humidity, thresholds["high"], 
                current_time, cooldown
            )
        elif self.alert_active["high"]:
            self._clear_alert("high", humidity, thresholds["high"])
        
        # Check low threshold
        if humidity < thresholds["low"]:
            self._handle_threshold_breach(
                "low", humidity, thresholds["low"], 
                current_time, cooldown
            )
        elif self.alert_active["low"]:
            self._clear_alert("low", humidity, thresholds["low"])
    
    def _handle_threshold_breach(self, alert_type: str, humidity: float, 
                                threshold: float, current_time: datetime, 
                                cooldown: int) -> None:
        """Handle threshold breach"""
        # Check if we're in cooldown period
        if alert_type in self.last_alert_time:
            time_since_last = (current_time - self.last_alert_time[alert_type]).total_seconds()
            if time_since_last < cooldown:
                return
        
        # Trigger alert
        self.alert_active[alert_type] = True
        self.last_alert_time[alert_type] = current_time
        
        alert_data = {
            "type": alert_type,
            "humidity": humidity,
            "threshold": threshold,
            "timestamp": current_time,
            "message": self._generate_alert_message(alert_type, humidity, threshold)
        }
        
        self._send_notification(alert_data)
        
        # Store alert record in a separate JSON file
        self._store_alert_record(alert_data)
    
    def _clear_alert(self, alert_type: str, humidity: float, threshold: float) -> None:
        """Clear active alert"""
        if self.alert_active[alert_type]:
            self.alert_active[alert_type] = False
            
            alert_data = {
                "type": f"{alert_type}_cleared",
                "humidity": humidity,
                "threshold": threshold,
                "timestamp": datetime.now(),
                "message": self._generate_clear_message(alert_type, humidity, threshold)
            }
            
            self._send_notification(alert_data)
    
    def _generate_alert_message(self, alert_type: str, humidity: float, threshold: float) -> str:
        """Generate alert message"""
        if alert_type == "high":
            return f"High humidity alert! Current: {humidity:.1f}% (Threshold: {threshold:.1f}%)"
        else:
            return f"Low humidity alert! Current: {humidity:.1f}% (Threshold: {threshold:.1f}%)"
    
    def _generate_clear_message(self, alert_type: str, humidity: float, threshold: float) -> str:
        """Generate alert clear message"""
        if alert_type == "high":
            return f"High humidity alert cleared. Current: {humidity:.1f}% (Below {threshold:.1f}%)"
        else:
            return f"Low humidity alert cleared. Current: {humidity:.1f}% (Above {threshold:.1f}%)"
    
    def _send_notification(self, alert_data: Dict[str, Any]) -> None:
        """Send notification through available channels"""
        # Store alert record
        self._store_alert_record(alert_data)
        
        # Sound notification
        if self.config_manager.get("alerts.sound_enabled", True):
            self._play_alert_sound(alert_data["type"])
        
        # Email notification (if enabled and configured)
        if (self.config_manager.get("alerts.email_enabled", False) and 
            self.config_manager.get("alerts.email_address", "")):
            self._send_email_alert(alert_data)
        
        # GUI notification callback
        if self.notification_callback:
            self.notification_callback(alert_data)
    
    def _play_alert_sound(self, alert_type: str) -> None:
        """Play alert sound"""
        try:
            # For Windows
            import winsound
            if "cleared" in alert_type:
                # Lower frequency for cleared alerts
                winsound.Beep(800, 200)
            else:
                # Higher frequency for active alerts
                winsound.Beep(1000, 500)
        except ImportError:
            try:
                # For Unix-like systems
                import os
                os.system("echo -e '\a'")
            except:
                pass  # No sound available
    
    def _send_email_alert(self, alert_data: Dict[str, Any]) -> None:
        """Send email alert (placeholder implementation)"""
        # This would implement SMTP email sending
        # For now, just print to console
        email = self.config_manager.get("alerts.email_address", "")
        print(f"Email alert to {email}: {alert_data['message']}")
    
    def _store_alert_record(self, alert_data: Dict[str, Any]) -> None:
        """Store alert record in a JSON file"""
        try:
            from ..utils.constants import DATA_DIR
            
            # Ensure data folder exists
            alert_dir = os.path.join(DATA_DIR, "db")
            os.makedirs(alert_dir, exist_ok=True)
            
            # Load existing records
            alert_file = os.path.join(alert_dir, "alert_records.json")
            try:
                with open(alert_file, 'r') as f:
                    records = json.load(f)
            except (FileNotFoundError, json.JSONDecodeError):
                records = []
            
            # Add new record
            alert_record = {
                'timestamp': alert_data['timestamp'].strftime('%Y-%m-%d %H:%M:%S'),
                'type': alert_data['type'],
                'humidity': alert_data['humidity'],
                'threshold': alert_data['threshold'],
                'message': alert_data['message']
            }
            records.append(alert_record)
            
            # Save back to file
            with open(alert_file, 'w') as f:
                json.dump(records, f, indent=2)
                
        except Exception as e:
            print(f"Failed to store alert record: {e}")
    
    def get_active_alerts(self) -> Dict[str, bool]:
        """Get currently active alerts"""
        return self.alert_active.copy()
    
    def get_recent_alerts(self, hours: int = 24) -> list:
        """Get recent alerts (placeholder - would need persistent storage)"""
        # This would return alerts from the last N hours
        # For now, return empty list
        return []
    
    def clear_all_alerts(self) -> None:
        """Clear all active alerts"""
        self.alert_active = {"high": False, "low": False}
        self.last_alert_time.clear()
    
    def test_alert_system(self) -> bool:
        """Test the alert system"""
        try:
            test_alert = {
                "type": "test",
                "humidity": 50.0,
                "threshold": 50.0,
                "timestamp": datetime.now(),
                "message": "Alert system test"
            }
            
            self._send_notification(test_alert)
            return True
        except Exception as e:
            print(f"Alert system test failed: {e}")
            return False
    
    def update_thresholds(self, high: float, low: float) -> None:
        """Update alert thresholds"""
        self.config_manager.set_thresholds(high, low)
        # Clear any alerts that are no longer valid
        self.clear_all_alerts()
    
    def enable_alerts(self, enabled: bool) -> None:
        """Enable or disable alerts"""
        self.config_manager.set("alerts.enabled", enabled)
        if not enabled:
            self.clear_all_alerts()
    
    def set_notification_settings(self, sound: bool = True, email: bool = False, 
                                 email_address: str = "", cooldown: int = 300) -> None:
        """Update notification settings"""
        self.config_manager.set("alerts.sound_enabled", sound)
        self.config_manager.set("alerts.email_enabled", email)
        self.config_manager.set("alerts.email_address", email_address)
        self.config_manager.set("alerts.cooldown_period", cooldown)
