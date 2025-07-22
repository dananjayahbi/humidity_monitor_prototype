#!/usr/bin/env python3
"""
Humidity Monitor Application
Main entry point for the ESP32 Humidity Monitoring System
"""

import sys
import os

# Ensure the 'src' directory is correctly added to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

# Import the main application class
from src.gui.main_window import HumidityMonitorApp

def main():
    """Main application entry point"""
    try:
        app = HumidityMonitorApp()
        app.run()
    except Exception as e:
        print(f"Application error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
