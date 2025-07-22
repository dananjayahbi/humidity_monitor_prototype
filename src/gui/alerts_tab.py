"""
Alerts Tab
Alert management and configuration
"""

import tkinter as tk
from tkinter import ttk
import ttkbootstrap as ttk_boot
from ttkbootstrap.constants import *
from datetime import datetime

from ..utils.helpers import validate_threshold_values

class AlertsTab:
    """Alerts tab for threshold and notification management"""
    
    def __init__(self, parent, alert_manager, config_manager):
        self.parent = parent
        self.alert_manager = alert_manager
        self.config_manager = config_manager
        
        # Create main frame
        self.frame = ttk_boot.Frame(parent)
        
        # Recent alerts list
        self.recent_alerts = []
        
        self._setup_ui()
        self._load_settings()
    
    def _setup_ui(self) -> None:
        """Setup the alerts UI"""
        # Create main container with scrollable content
        main_container = ttk_boot.Frame(self.frame)
        main_container.pack(fill=BOTH, expand=True, padx=20, pady=20)
        
        # Left panel - Alert Settings
        left_panel = ttk_boot.Frame(main_container)
        left_panel.pack(side=LEFT, fill=Y, padx=(0, 20))
        
        self._setup_alert_settings(left_panel)
        self._setup_notification_settings(left_panel)
        
        # Right panel - Recent Alerts
        right_panel = ttk_boot.Frame(main_container)
        right_panel.pack(side=RIGHT, fill=BOTH, expand=True)
        
        self._setup_recent_alerts(right_panel)
    
    def _setup_alert_settings(self, parent) -> None:
        """Setup alert threshold settings"""
        settings_frame = ttk_boot.LabelFrame(
            parent, text="Alert Thresholds", bootstyle="primary"
        )
        settings_frame.pack(fill=X, pady=(0, 20))
        
        # Enable/disable alerts
        self.alerts_enabled_var = tk.BooleanVar()
        alerts_check = ttk_boot.Checkbutton(
            settings_frame,
            text="Enable Alerts",
            variable=self.alerts_enabled_var,
            command=self._on_alerts_toggle,
            bootstyle="primary"
        )
        alerts_check.pack(anchor=W, padx=10, pady=10)
        
        # High threshold
        high_frame = ttk_boot.Frame(settings_frame)
        high_frame.pack(fill=X, padx=10, pady=5)
        
        ttk_boot.Label(
            high_frame, text="High Humidity Threshold (%):", width=25
        ).pack(side=LEFT)
        
        self.high_threshold_var = tk.DoubleVar()
        high_spinbox = ttk_boot.Spinbox(
            high_frame,
            from_=0.0,
            to=100.0,
            increment=0.5,
            textvariable=self.high_threshold_var,
            width=10,
            command=self._on_threshold_change
        )
        high_spinbox.pack(side=RIGHT, padx=(10, 0))
        
        # Low threshold
        low_frame = ttk_boot.Frame(settings_frame)
        low_frame.pack(fill=X, padx=10, pady=5)
        
        ttk_boot.Label(
            low_frame, text="Low Humidity Threshold (%):", width=25
        ).pack(side=LEFT)
        
        self.low_threshold_var = tk.DoubleVar()
        low_spinbox = ttk_boot.Spinbox(
            low_frame,
            from_=0.0,
            to=100.0,
            increment=0.5,
            textvariable=self.low_threshold_var,
            width=10,
            command=self._on_threshold_change
        )
        low_spinbox.pack(side=RIGHT, padx=(10, 0))
        
        # Save button
        ttk_boot.Button(
            settings_frame,
            text="Save Settings",
            command=self._save_threshold_settings,
            bootstyle="success"
        ).pack(pady=10)
    
    def _setup_notification_settings(self, parent) -> None:
        """Setup notification method settings"""
        notification_frame = ttk_boot.LabelFrame(
            parent, text="Notification Settings", bootstyle="info"
        )
        notification_frame.pack(fill=X, pady=(0, 20))
        
        # Sound notifications
        self.sound_enabled_var = tk.BooleanVar()
        sound_check = ttk_boot.Checkbutton(
            notification_frame,
            text="Sound Notifications",
            variable=self.sound_enabled_var,
            bootstyle="info"
        )
        sound_check.pack(anchor=W, padx=10, pady=5)
        
        # Email notifications
        self.email_enabled_var = tk.BooleanVar()
        email_check = ttk_boot.Checkbutton(
            notification_frame,
            text="Email Notifications",
            variable=self.email_enabled_var,
            command=self._on_email_toggle,
            bootstyle="info"
        )
        email_check.pack(anchor=W, padx=10, pady=5)
        
        # Email address
        email_frame = ttk_boot.Frame(notification_frame)
        email_frame.pack(fill=X, padx=10, pady=5)
        
        ttk_boot.Label(email_frame, text="Email Address:").pack(anchor=W)
        self.email_var = tk.StringVar()
        self.email_entry = ttk_boot.Entry(
            email_frame,
            textvariable=self.email_var,
            width=30,
            state="disabled"
        )
        self.email_entry.pack(anchor=W, pady=(5, 0))
        
        # Cooldown period
        cooldown_frame = ttk_boot.Frame(notification_frame)
        cooldown_frame.pack(fill=X, padx=10, pady=5)
        
        ttk_boot.Label(
            cooldown_frame, text="Alert Cooldown (seconds):", width=20
        ).pack(side=LEFT)
        
        self.cooldown_var = tk.IntVar()
        cooldown_spinbox = ttk_boot.Spinbox(
            cooldown_frame,
            from_=60,
            to=3600,
            increment=30,
            textvariable=self.cooldown_var,
            width=10
        )
        cooldown_spinbox.pack(side=RIGHT, padx=(10, 0))
        
        # Test and save buttons
        button_frame = ttk_boot.Frame(notification_frame)
        button_frame.pack(fill=X, padx=10, pady=10)
        
        ttk_boot.Button(
            button_frame,
            text="Test Alerts",
            command=self._test_alerts,
            bootstyle="warning"
        ).pack(side=LEFT, padx=(0, 10))
        
        ttk_boot.Button(
            button_frame,
            text="Save Settings",
            command=self._save_notification_settings,
            bootstyle="success"
        ).pack(side=RIGHT)
    
    def _setup_recent_alerts(self, parent) -> None:
        """Setup recent alerts display"""
        alerts_frame = ttk_boot.LabelFrame(
            parent, text="Recent Alerts", bootstyle="warning"
        )
        alerts_frame.pack(fill=BOTH, expand=True)
        
        # Create treeview for alerts
        columns = ("timestamp", "type", "value", "device")
        self.alerts_tree = ttk_boot.Treeview(
            alerts_frame,
            columns=columns,
            show="headings",
            height=15
        )
        
        # Configure columns
        self.alerts_tree.heading("timestamp", text="Timestamp")
        self.alerts_tree.heading("type", text="Type")
        self.alerts_tree.heading("value", text="Value (%)")
        self.alerts_tree.heading("device", text="Device")
        
        self.alerts_tree.column("timestamp", width=150)
        self.alerts_tree.column("type", width=120)
        self.alerts_tree.column("value", width=80)
        self.alerts_tree.column("device", width=150)
        
        # Scrollbar for treeview
        scrollbar = ttk_boot.Scrollbar(
            alerts_frame,
            orient=VERTICAL,
            command=self.alerts_tree.yview
        )
        self.alerts_tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack treeview and scrollbar
        self.alerts_tree.pack(side=LEFT, fill=BOTH, expand=True, padx=10, pady=10)
        scrollbar.pack(side=RIGHT, fill=Y, pady=10)
        
        # Buttons for alert management
        button_frame = ttk_boot.Frame(alerts_frame)
        button_frame.pack(fill=X, padx=10, pady=(0, 10))
        
        ttk_boot.Button(
            button_frame,
            text="Clear All",
            command=self._clear_alerts,
            bootstyle="danger"
        ).pack(side=LEFT)
        
        ttk_boot.Button(
            button_frame,
            text="Refresh",
            command=self._refresh_alerts,
            bootstyle="primary"
        ).pack(side=RIGHT)
        
        # Add some sample alerts for demonstration
        self._add_sample_alerts()
    
    def _load_settings(self) -> None:
        """Load current settings"""
        # Load thresholds
        thresholds = self.config_manager.get_thresholds()
        self.high_threshold_var.set(thresholds["high"])
        self.low_threshold_var.set(thresholds["low"])
        
        # Load alert settings
        alert_settings = self.config_manager.get_alert_settings()
        self.alerts_enabled_var.set(alert_settings["enabled"])
        self.sound_enabled_var.set(alert_settings["sound_enabled"])
        self.email_enabled_var.set(alert_settings["email_enabled"])
        self.email_var.set(alert_settings["email_address"])
        self.cooldown_var.set(alert_settings["cooldown_period"])
        
        # Update email entry state
        self._on_email_toggle()
    
    def _on_alerts_toggle(self) -> None:
        """Handle alerts enable/disable"""
        enabled = self.alerts_enabled_var.get()
        self.alert_manager.enable_alerts(enabled)
    
    def _on_email_toggle(self) -> None:
        """Handle email notifications toggle"""
        if self.email_enabled_var.get():
            self.email_entry.config(state="normal")
        else:
            self.email_entry.config(state="disabled")
    
    def _on_threshold_change(self) -> None:
        """Handle threshold value changes"""
        # Validate thresholds
        high = self.high_threshold_var.get()
        low = self.low_threshold_var.get()
        
        validated_low, validated_high = validate_threshold_values(low, high)
        
        if validated_low != low:
            self.low_threshold_var.set(validated_low)
        if validated_high != high:
            self.high_threshold_var.set(validated_high)
    
    def _save_threshold_settings(self) -> None:
        """Save threshold settings"""
        high = self.high_threshold_var.get()
        low = self.low_threshold_var.get()
        
        self.alert_manager.update_thresholds(high, low)
        
        # Show confirmation
        self._show_status("Threshold settings saved successfully", "success")
    
    def _save_notification_settings(self) -> None:
        """Save notification settings"""
        self.alert_manager.set_notification_settings(
            sound=self.sound_enabled_var.get(),
            email=self.email_enabled_var.get(),
            email_address=self.email_var.get(),
            cooldown=self.cooldown_var.get()
        )
        
        # Show confirmation
        self._show_status("Notification settings saved successfully", "success")
    
    def _test_alerts(self) -> None:
        """Test alert system"""
        if self.alert_manager.test_alert_system():
            self._show_status("Alert test successful", "success")
        else:
            self._show_status("Alert test failed", "danger")
    
    def _show_status(self, message: str, style: str) -> None:
        """Show status message"""
        # This would show a temporary status message
        # For now, just print to console
        print(f"Status ({style}): {message}")
    
    def add_alert_to_recent(self, alert_data: dict) -> None:
        """Add alert to recent alerts list"""
        # Add to internal list
        self.recent_alerts.append(alert_data)
        
        # Add to treeview
        timestamp_str = alert_data["timestamp"].strftime("%Y-%m-%d %H:%M:%S")
        alert_type = alert_data["type"].replace("_", " ").title()
        humidity_value = f"{alert_data['humidity']:.1f}"
        device = "ESP32 Sensor"  # This could be dynamic
        
        # Determine row style based on alert type
        tags = ()
        if "high" in alert_data["type"]:
            tags = ("high_alert",)
        elif "low" in alert_data["type"]:
            tags = ("low_alert",)
        elif "cleared" in alert_data["type"]:
            tags = ("cleared_alert",)
        
        # Insert at top of tree
        self.alerts_tree.insert(
            "", 0,
            values=(timestamp_str, alert_type, humidity_value, device),
            tags=tags
        )
        
        # Configure tag colors
        self.alerts_tree.tag_configure("high_alert", background="#ffcccc")
        self.alerts_tree.tag_configure("low_alert", background="#ffffcc")
        self.alerts_tree.tag_configure("cleared_alert", background="#ccffcc")
        
        # Limit number of displayed alerts
        children = self.alerts_tree.get_children()
        if len(children) > 100:  # Keep only last 100 alerts
            self.alerts_tree.delete(children[-1])
    
    def _add_sample_alerts(self) -> None:
        """Add sample alerts for demonstration"""
        sample_alerts = [
            {
                "timestamp": datetime.now(),
                "type": "high",
                "humidity": 75.2,
                "threshold": 70.0,
                "message": "High humidity alert"
            },
            {
                "timestamp": datetime.now(),
                "type": "low",
                "humidity": 25.8,
                "threshold": 30.0,
                "message": "Low humidity alert"
            }
        ]
        
        for alert in sample_alerts:
            self.add_alert_to_recent(alert)
    
    def _clear_alerts(self) -> None:
        """Clear all alerts"""
        self.recent_alerts.clear()
        
        # Clear treeview
        for item in self.alerts_tree.get_children():
            self.alerts_tree.delete(item)
        
        self._show_status("All alerts cleared", "info")
    
    def _refresh_alerts(self) -> None:
        """Refresh alerts display"""
        # This would reload alerts from persistent storage
        # For now, just show status
        self._show_status("Alerts refreshed", "info")
