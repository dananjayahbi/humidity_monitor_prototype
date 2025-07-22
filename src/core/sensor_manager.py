"""
Sensor Manager
Handles ESP32 communication and data collection
"""

import serial
import serial.tools.list_ports
import threading
import time
from typing import Optional, Callable
from pythonping import ping
import os

from ..utils.constants import ESP32_USB_IDS, ESP32_WIFI_IP, ESP32_BAUD_RATE
from ..utils.helpers import parse_humidity_from_serial

# Fix the data folder path
DATA_FOLDER = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'data'))

class SensorManager:
    """Manages ESP32 sensor communication"""
    
    def __init__(self, data_callback: Optional[Callable[[float], None]] = None):
        self.data_callback = data_callback
        self.serial_connection: Optional[serial.Serial] = None
        self.connected_port: Optional[str] = None
        self.is_running = False
        self.read_thread: Optional[threading.Thread] = None
        self.connection_type: Optional[str] = None
    
    def detect_usb_device(self) -> Optional[str]:
        """Detect ESP32 device connected via USB"""
        ports = serial.tools.list_ports.comports()
        
        for port in ports:
            vid = f"{port.vid:04X}" if port.vid else ""
            pid = f"{port.pid:04X}" if port.pid else ""
            
            if (vid, pid) in ESP32_USB_IDS:
                return port.device
        
        return None
    
    def test_wifi_connection(self, ip: str = ESP32_WIFI_IP) -> bool:
        """Test Wi-Fi connection to ESP32"""
        try:
            response = ping(ip, count=1, timeout=1)
            return response.success()
        except Exception:
            return False
    
    def connect_usb(self, port: Optional[str] = None) -> bool:
        """Connect to ESP32 via USB"""
        if port is None:
            port = self.detect_usb_device()
        
        if port is None:
            return False
        
        try:
            self.serial_connection = serial.Serial(
                port, ESP32_BAUD_RATE, timeout=1
            )
            self.connected_port = port
            self.connection_type = "usb"
            return True
        
        except Exception as e:
            print(f"Error connecting to USB port {port}: {e}")
            return False
    
    def connect_wifi(self, ip: str = ESP32_WIFI_IP) -> bool:
        """Connect to ESP32 via Wi-Fi (placeholder for HTTP/TCP implementation)"""
        if self.test_wifi_connection(ip):
            self.connection_type = "wifi"
            self.connected_port = ip
            return True
        return False
    
    def auto_connect(self) -> tuple[bool, str]:
        """Automatically detect and connect to ESP32"""
        # Try USB first
        if self.connect_usb():
            return True, f"Connected via USB ({self.connected_port})"
        
        # Try Wi-Fi
        if self.connect_wifi():
            return True, f"Connected via Wi-Fi ({self.connected_port})"
        
        return False, "ESP32 not detected"
    
    def start_monitoring(self) -> bool:
        """Start data monitoring"""
        if not self.is_connected():
            return False
        
        self.is_running = True
        
        if self.connection_type == "usb":
            self.read_thread = threading.Thread(target=self._read_serial_data, daemon=True)
            self.read_thread.start()
            return True
        elif self.connection_type == "wifi":
            # For Wi-Fi, would implement HTTP polling or WebSocket connection
            self.read_thread = threading.Thread(target=self._read_wifi_data, daemon=True)
            self.read_thread.start()
            return True
        
        return False
    
    def stop_monitoring(self) -> None:
        """Stop data monitoring"""
        self.is_running = False
        
        if self.read_thread and self.read_thread.is_alive():
            self.read_thread.join(timeout=1.0)
    
    def disconnect(self) -> None:
        """Disconnect from ESP32"""
        self.stop_monitoring()
        
        if self.serial_connection and self.serial_connection.is_open:
            try:
                self.serial_connection.close()
            except Exception as e:
                print(f"Error closing serial connection: {e}")
        
        self.serial_connection = None
        self.connected_port = None
        self.connection_type = None
    
    def is_connected(self) -> bool:
        """Check if device is connected"""
        if self.connection_type == "usb":
            return (self.serial_connection is not None and 
                   self.serial_connection.is_open)
        elif self.connection_type == "wifi":
            return self.test_wifi_connection(self.connected_port)
        
        return False
    
    def get_connection_info(self) -> dict:
        """Get connection information"""
        return {
            "connected": self.is_connected(),
            "type": self.connection_type,
            "port": self.connected_port,
            "monitoring": self.is_running
        }
    
    def _read_serial_data(self) -> None:
        """Read data from serial connection"""
        while self.is_running and self.serial_connection:
            try:
                if self.serial_connection.in_waiting > 0:
                    line = self.serial_connection.readline().decode('utf-8').strip()
                    
                    if line:
                        humidity = parse_humidity_from_serial(line)
                        if humidity is not None and self.data_callback:
                            self.data_callback(humidity)
                
                time.sleep(0.1)
            
            except Exception as e:
                if self.is_running:  # Only log if we're still supposed to be running
                    print(f"Error reading serial data: {e}")
                break
    
    def _read_wifi_data(self) -> None:
        """Read data from Wi-Fi connection (placeholder)"""
        # This would implement HTTP requests or WebSocket connection to ESP32
        # For now, simulate with random data for demonstration
        import random
        
        while self.is_running:
            try:
                # Simulate humidity reading
                if self.data_callback:
                    # Generate simulated data for demonstration
                    humidity = 40 + random.uniform(-10, 20)
                    self.data_callback(humidity)
                
                time.sleep(5)  # Read every 5 seconds for Wi-Fi
            
            except Exception as e:
                if self.is_running:
                    print(f"Error reading Wi-Fi data: {e}")
                break
    
    def send_command(self, command: str) -> Optional[str]:
        """Send command to ESP32 (USB only)"""
        if self.connection_type != "usb" or not self.serial_connection:
            return None
        
        try:
            self.serial_connection.write(f"{command}\n".encode())
            time.sleep(0.1)
            
            if self.serial_connection.in_waiting > 0:
                response = self.serial_connection.readline().decode('utf-8').strip()
                return response
        
        except Exception as e:
            print(f"Error sending command: {e}")
        
        return None
