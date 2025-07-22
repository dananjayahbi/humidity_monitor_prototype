"""
Configuration Manager
Handles application settings and configuration persistence
"""

import json
import os
from typing import Dict, Any
from pathlib import Path

from ..utils.constants import (
    DATA_DIR, CONFIG_FILE, DEFAULT_HIGH_THRESHOLD, DEFAULT_LOW_THRESHOLD,
    DEFAULT_THEME, HUMIDITY_UNITS
)

class ConfigManager:
    """Manages application configuration"""
    
    def __init__(self):
        self.config_path = Path(DATA_DIR) / CONFIG_FILE
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file"""
        default_config = {
            "thresholds": {
                "high": DEFAULT_HIGH_THRESHOLD,
                "low": DEFAULT_LOW_THRESHOLD
            },
            "alerts": {
                "enabled": True,
                "sound_enabled": True,
                "email_enabled": False,
                "email_address": "",
                "cooldown_period": 300
            },
            "display": {
                "theme": DEFAULT_THEME,
                "humidity_unit": "percentage",
                "auto_scale": True,
                "show_grid": True,
                "update_interval": 1000
            },
            "device": {
                "auto_connect": True,
                "preferred_connection": "usb",
                "wifi_ip": "192.168.4.1"
            },
            "data": {
                "max_records": 10000,
                "auto_cleanup": True,
                "export_format": "csv"
            }
        }
        
        if not self.config_path.exists():
            # Create data directory if it doesn't exist
            self.config_path.parent.mkdir(exist_ok=True)
            # Save default config
            self._save_config(default_config)
            return default_config
        
        try:
            with open(self.config_path, 'r') as f:
                loaded_config = json.load(f)
            
            # Merge with defaults to ensure all keys exist
            return self._merge_configs(default_config, loaded_config)
        
        except (json.JSONDecodeError, FileNotFoundError):
            return default_config
    
    def _merge_configs(self, default: Dict[str, Any], loaded: Dict[str, Any]) -> Dict[str, Any]:
        """Merge loaded config with defaults"""
        result = default.copy()
        
        for key, value in loaded.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key].update(value)
            else:
                result[key] = value
        
        return result
    
    def _save_config(self, config: Dict[str, Any]) -> None:
        """Save configuration to file"""
        try:
            with open(self.config_path, 'w') as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            print(f"Error saving config: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value"""
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any) -> None:
        """Set configuration value"""
        keys = key.split('.')
        config = self.config
        
        # Navigate to the parent of the target key
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        # Set the value
        config[keys[-1]] = value
        
        # Save to file
        self._save_config(self.config)
    
    def get_thresholds(self) -> Dict[str, float]:
        """Get humidity thresholds"""
        return {
            "high": self.get("thresholds.high", DEFAULT_HIGH_THRESHOLD),
            "low": self.get("thresholds.low", DEFAULT_LOW_THRESHOLD)
        }
    
    def set_thresholds(self, high: float, low: float) -> None:
        """Set humidity thresholds"""
        self.set("thresholds.high", high)
        self.set("thresholds.low", low)
    
    def get_display_settings(self) -> Dict[str, Any]:
        """Get display settings"""
        return {
            "theme": self.get("display.theme", DEFAULT_THEME),
            "humidity_unit": self.get("display.humidity_unit", "percentage"),
            "auto_scale": self.get("display.auto_scale", True),
            "show_grid": self.get("display.show_grid", True),
            "update_interval": self.get("display.update_interval", 1000)
        }
    
    def get_alert_settings(self) -> Dict[str, Any]:
        """Get alert settings"""
        return {
            "enabled": self.get("alerts.enabled", True),
            "sound_enabled": self.get("alerts.sound_enabled", True),
            "email_enabled": self.get("alerts.email_enabled", False),
            "email_address": self.get("alerts.email_address", ""),
            "cooldown_period": self.get("alerts.cooldown_period", 300)
        }
    
    def reset_to_defaults(self) -> None:
        """Reset configuration to defaults"""
        if self.config_path.exists():
            self.config_path.unlink()
        self.config = self._load_config()
    
    def get_config(self) -> Dict[str, Any]:
        """Get the entire configuration dictionary"""
        return self.config
