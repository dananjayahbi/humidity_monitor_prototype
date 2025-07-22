# HumidStat - Quick Start Guide

## Prerequisites

- Python 3.8 or higher
- ESP32 device with humidity sensor
- USB cable or Wi-Fi connection

## Installation

### Option 1: Automatic Installation
```bash
python install.py
```

### Option 2: Manual Installation
```bash
pip install -r requirements.txt
```

## Running the Application

```bash
python main.py
```

## First Time Setup

1. **Connect Your ESP32**
   - Connect ESP32 via USB cable
   - Or ensure ESP32 is connected to your Wi-Fi network

2. **Start Monitoring**
   - Click "Connect Device" in the Overview tab
   - Click "Start Monitoring" to begin data collection

3. **Configure Alerts**
   - Go to the Alerts tab
   - Set your preferred high and low humidity thresholds
   - Enable sound or email notifications as needed

4. **Customize Settings**
   - Visit the Settings tab to customize appearance and behavior
   - Choose your preferred theme
   - Set update intervals and data retention policies

## Features Overview

### Overview Tab
- Real-time humidity display
- Live graph with last 50 readings
- Today's statistics (average, min, max, trend)
- Device connection controls

### History Tab
- Historical data visualization
- Filter by day, week, or month
- Custom date range filtering
- Export capabilities

### Alerts Tab
- Configure humidity thresholds
- Set up notifications (sound, email)
- View recent alert history
- Test alert system

### Settings Tab
- Customize appearance (themes, units)
- Configure device connections
- Manage data retention
- Export preferences

## Troubleshooting

### ESP32 Not Detected
- Check USB cable connection
- Verify ESP32 drivers are installed
- Try different USB port
- Check if device appears in device manager

### No Data Appearing
- Verify ESP32 is sending data in correct format
- Check serial output: "Humidity: XX.X"
- Ensure correct baud rate (115200)

### Wi-Fi Connection Issues
- Verify ESP32 IP address in settings
- Check Wi-Fi network connectivity
- Ensure ESP32 web server is running

## Data Format

The application expects humidity data in this format:
```
Humidity: 65.4
```

## File Structure

```
humidity_monitor/
├── main.py              # Application entry point
├── install.py           # Installation script
├── requirements.txt     # Dependencies
├── data/               # Data storage
│   ├── humidity_data.json
│   └── config.json
└── src/               # Source code
    ├── core/          # Core functionality
    ├── gui/           # User interface
    └── utils/         # Utilities
```

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Verify all dependencies are installed
3. Ensure ESP32 is properly configured

## License

This software is provided as-is for educational and personal use.
