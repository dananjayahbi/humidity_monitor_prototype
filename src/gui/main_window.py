"""
Main Application Window
The primary GUI container and application controller
"""

import tkinter as tk
from tkinter import ttk
import ttkbootstrap as ttk_boot
from ttkbootstrap.constants import *

from ..core.data_manager import DataManager
from ..core.config_manager import ConfigManager
from ..core.sensor_manager import SensorManager
from ..core.alert_manager import AlertManager
from ..utils.constants import WINDOW_SIZE, WINDOW_TITLE

from .overview_tab import OverviewTab
from .history_tab import HistoryTab
from .alerts_tab import AlertsTab
from .settings_tab import SettingsTab

class HumidityMonitorApp:
    """Main application window and controller"""
    
    def __init__(self):
        # Initialize core components
        self.config_manager = ConfigManager()
        self.data_manager = DataManager()
        
        # Initialize sensor manager with data callback
        self.sensor_manager = SensorManager(
            data_callback=self._on_new_data
        )
        
        # Initialize alert manager with notification callback
        self.alert_manager = AlertManager(
            self.config_manager,
            notification_callback=self._on_alert_notification
        )
        
        # Initialize GUI
        self._setup_gui()
        self._setup_tabs()
        self._setup_menu()
        
        # Connection status
        self.connection_status = "Disconnected"
        self.monitoring_active = False
        
        # Auto-connect if enabled
        if self.config_manager.get("device.auto_connect", True):
            self._auto_connect()
    
    def _setup_gui(self) -> None:
        """Setup main GUI window"""
        theme = self.config_manager.get_display_settings()["theme"]
        
        self.root = ttk_boot.Window(
            title=WINDOW_TITLE,
            themename=theme,
            size=WINDOW_SIZE.split('x')
        )
        
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
        
        # Status bar
        self.status_frame = ttk_boot.Frame(self.root)
        self.status_frame.pack(side=BOTTOM, fill=X, padx=5, pady=2)
        
        self.status_label = ttk_boot.Label(
            self.status_frame,
            text="Ready",
            bootstyle="info"
        )
        self.status_label.pack(side=LEFT)
        
        # Connection indicator
        self.connection_label = ttk_boot.Label(
            self.status_frame,
            text="●",
            bootstyle="danger",
            font=("Arial", 16)
        )
        self.connection_label.pack(side=RIGHT, padx=5)
        
        self.connection_text = ttk_boot.Label(
            self.status_frame,
            text="Disconnected",
            bootstyle="secondary"
        )
        self.connection_text.pack(side=RIGHT)
    
    def _setup_tabs(self) -> None:
        """Setup tab notebook"""
        self.notebook = ttk_boot.Notebook(self.root)
        self.notebook.pack(fill=BOTH, expand=True, padx=5, pady=5)
        
        # Create tabs
        self.overview_tab = OverviewTab(
            self.notebook, self.data_manager, self.sensor_manager,
            self.alert_manager, self.config_manager
        )
        
        self.history_tab = HistoryTab(
            self.notebook, self.data_manager, self.config_manager
        )
        
        self.alerts_tab = AlertsTab(
            self.notebook, self.alert_manager, self.config_manager
        )
        
        self.settings_tab = SettingsTab(
            self.notebook, self.config_manager, self._on_settings_changed
        )
        
        # Add tabs to notebook
        self.notebook.add(self.overview_tab.frame, text="Overview")
        self.notebook.add(self.history_tab.frame, text="History")
        self.notebook.add(self.alerts_tab.frame, text="Alerts")
        self.notebook.add(self.settings_tab.frame, text="Settings")
    
    def _setup_menu(self) -> None:
        """Setup application menu"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Export Data...", command=self._export_data)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self._on_closing)
        
        # Device menu
        device_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Device", menu=device_menu)
        device_menu.add_command(label="Connect", command=self._connect_device)
        device_menu.add_command(label="Disconnect", command=self._disconnect_device)
        device_menu.add_separator()
        device_menu.add_command(label="Test Connection", command=self._test_connection)
        
        # Tools menu
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Clear Data", command=self._clear_data)
        tools_menu.add_command(label="Test Alerts", command=self._test_alerts)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self._show_about)
    
    def _on_new_data(self, humidity: float) -> None:
        """Handle new sensor data"""
        # Store data
        self.data_manager.add_reading(humidity)
        
        # Check alerts
        self.alert_manager.check_thresholds(humidity)
        
        # Update GUI (in main thread)
        self.root.after(0, self._update_gui_data, humidity)
    
    def _update_gui_data(self, humidity: float) -> None:
        """Update GUI with new data (main thread)"""
        # Update overview tab
        self.overview_tab.update_current_humidity(humidity)
        
        # Update status
        self.status_label.config(text=f"Latest reading: {humidity:.1f}%")
    
    def _on_alert_notification(self, alert_data: dict) -> None:
        """Handle alert notifications"""
        # Update GUI in main thread
        self.root.after(0, self._show_alert_notification, alert_data)
    
    def _show_alert_notification(self, alert_data: dict) -> None:
        """Show alert notification in GUI"""
        # Update alerts tab
        self.alerts_tab.add_alert_to_recent(alert_data)
        
        # Show status message
        self.status_label.config(
            text=alert_data["message"],
            bootstyle="warning" if "cleared" in alert_data["type"] else "danger"
        )
    
    def _auto_connect(self) -> None:
        """Auto-connect to device"""
        success, message = self.sensor_manager.auto_connect()
        self._update_connection_status(success, message)
    
    def _connect_device(self) -> None:
        """Manual device connection"""
        success, message = self.sensor_manager.auto_connect()
        self._update_connection_status(success, message)
        
        if success:
            self.sensor_manager.start_monitoring()
            self.monitoring_active = True
    
    def _disconnect_device(self) -> None:
        """Disconnect device"""
        self.sensor_manager.disconnect()
        self.monitoring_active = False
        self._update_connection_status(False, "Disconnected")
    
    def _update_connection_status(self, connected: bool, message: str) -> None:
        """Update connection status display"""
        self.connection_status = message
        
        if connected:
            self.connection_label.config(bootstyle="success")
            self.connection_text.config(text="Connected")
        else:
            self.connection_label.config(bootstyle="danger")
            self.connection_text.config(text="Disconnected")
        
        # Update overview tab
        self.overview_tab.update_connection_status(connected, message)
    
    def _test_connection(self) -> None:
        """Test device connection"""
        if self.sensor_manager.is_connected():
            self.status_label.config(text="Connection test: OK", bootstyle="success")
        else:
            self.status_label.config(text="Connection test: Failed", bootstyle="danger")
    
    def _export_data(self) -> None:
        """Export data dialog"""
        from tkinter import filedialog, messagebox
        
        filename = filedialog.asksaveasfilename(
            title="Export Data",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("JSON files", "*.json")]
        )
        
        if filename:
            try:
                format_type = "csv" if filename.endswith(".csv") else "json"
                data = self.data_manager.export_data(format_type)
                
                with open(filename, 'w') as f:
                    f.write(data)
                
                messagebox.showinfo("Export Complete", f"Data exported to {filename}")
            except Exception as e:
                messagebox.showerror("Export Error", f"Failed to export data: {e}")
    
    def _clear_data(self) -> None:
        """Clear all data"""
        from tkinter import messagebox
        
        if messagebox.askyesno("Clear Data", "Are you sure you want to clear all data?"):
            self.data_manager.clear_all_data()
            self.status_label.config(text="Data cleared", bootstyle="warning")
    
    def _test_alerts(self) -> None:
        """Test alert system"""
        if self.alert_manager.test_alert_system():
            self.status_label.config(text="Alert test successful", bootstyle="success")
        else:
            self.status_label.config(text="Alert test failed", bootstyle="danger")
    
    def _show_about(self) -> None:
        """Show about dialog"""
        from tkinter import messagebox
        
        about_text = """HumidStat - Humidity Monitor v1.0
        
ESP32-based humidity monitoring system with real-time data visualization, 
alerting, and historical analysis.

Features:
• Real-time monitoring
• Threshold-based alerts
• Historical data analysis
• Data export capabilities
• Professional UI

Built with Python, tkinter, and ttkbootstrap."""
        
        messagebox.showinfo("About HumidStat", about_text)
    
    def _on_settings_changed(self) -> None:
        """Handle settings changes"""
        # Refresh theme if changed
        new_theme = self.config_manager.get_display_settings()["theme"]
        if new_theme != self.root.style.theme.name:
            self.root.style.theme_use(new_theme)
        
        # Update other components as needed
        self.overview_tab.refresh_settings()
        self.history_tab.refresh_settings()
    
    def _on_closing(self) -> None:
        """Handle application closing"""
        # Stop monitoring
        if self.monitoring_active:
            self.sensor_manager.disconnect()
        
        # Close application
        self.root.destroy()
    
    def run(self) -> None:
        """Start the application"""
        self.root.mainloop()
