# Humidity Monitor Application

An ESP32 humidity monitoring system with real-time data visualization, alerting, and historical data analysis.

## Features

- Real-time humidity monitoring via ESP32 (USB/Wi-Fi)
- Interactive data visualization with smooth line graphs
- Configurable threshold-based alerting system
- Historical data analysis (Daily/Weekly/Monthly views)
- Data filtering and export capabilities
- Professional UI with multiple themes
- JSON-based data storage and configuration

## Project Structure

```
humidity_monitor/
├── main.py                 # Application entry point
├── requirements.txt        # Dependencies
├── data/                   # Data storage
│   ├── humidity_data.json  # Sensor readings
│   └── config.json         # Application settings
└── src/
    ├── core/               # Core functionality
    │   ├── data_manager.py # Data storage and retrieval
    │   ├── config_manager.py # Settings management
    │   ├── sensor_manager.py # ESP32 communication
    │   └── alert_manager.py # Notification system
    ├── gui/                # User interface
    │   ├── main_window.py  # Main application window
    │   ├── overview_tab.py # Dashboard/overview
    │   ├── history_tab.py  # Historical data view
    │   ├── alerts_tab.py   # Alert management
    │   └── settings_tab.py # Configuration
    └── utils/              # Utilities
        ├── constants.py    # Application constants
        └── helpers.py      # Helper functions
```

## Installation

1. Install Python 3.8+
2. Install dependencies: `pip install -r requirements.txt`
3. Run the application: `python main.py`

## Usage

1. Connect your ESP32 device via USB
2. Click "Start Monitoring" to begin data collection
3. Configure thresholds in the Alerts tab
4. View historical data in the History tab
5. Customize settings in the Settings tab
