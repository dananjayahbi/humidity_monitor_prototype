"""
Application Constants
Centralized configuration and constants
"""

import os

# ESP32 Configuration
ESP32_USB_IDS = [("10C4", "EA60"), ("1A86", "7523"), ("0403", "6001")]
ESP32_WIFI_IP = "192.168.4.1"
ESP32_BAUD_RATE = 115200

# Data Configuration
MAX_DATA_POINTS = 1000
GRAPH_DISPLAY_POINTS = 50
UPDATE_INTERVAL = 1000  # milliseconds

# File Paths - Use absolute paths relative to project root
DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'data'))
DATA_FILE = "humidity_data.json"
CONFIG_FILE = "config.json"

# UI Configuration
WINDOW_SIZE = "1000x700"
WINDOW_TITLE = "HumidStat - Humidity Monitor"

# Theme Configuration
DEFAULT_THEME = "cosmo"
AVAILABLE_THEMES = [
    "cosmo", "flatly", "journal", "litera", "lumen", "minty",
    "pulse", "sandstone", "united", "yeti", "morph", "simplex",
    "cerculean", "solar", "superhero", "darkly", "cyborg", "vapor"
]

# Alert Configuration
DEFAULT_HIGH_THRESHOLD = 70.0
DEFAULT_LOW_THRESHOLD = 30.0
ALERT_COOLDOWN = 300  # seconds

# Display Units
HUMIDITY_UNITS = {
    "percentage": "%",
    "absolute": "g/m³"
}

# Time Formats
TIME_FORMAT = "%H:%M:%S"
DATE_FORMAT = "%Y-%m-%d"
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"

# Graph Configuration
GRAPH_COLORS = {
    "primary": "#3498db",
    "success": "#2ecc71",
    "warning": "#f39c12",
    "danger": "#e74c3c",
    "info": "#17a2b8"
}
