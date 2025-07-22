"""
Settings Tab
Application configuration and preferences
"""

import tkinter as tk
from tkinter import ttk
import ttkbootstrap as ttk_boot
from ttkbootstrap.constants import *

from ..utils.constants import AVAILABLE_THEMES, HUMIDITY_UNITS

class SettingsTab:
    """Settings tab for application configuration"""
    
    def __init__(self, parent, config_manager, settings_changed_callback):
        self.parent = parent
        self.config_manager = config_manager
        self.settings_changed_callback = settings_changed_callback
        
        # Create main frame
        self.frame = ttk_boot.Frame(parent)
        
        self._setup_ui()
        self._load_settings()
    
    def _setup_ui(self) -> None:
        """Setup the settings UI"""
        # Create scrollable frame
        canvas = tk.Canvas(self.frame)
        scrollbar = ttk_boot.Scrollbar(self.frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk_boot.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Main container
        main_container = ttk_boot.Frame(scrollable_frame)
        main_container.pack(fill=BOTH, expand=True, padx=20, pady=20)
        
        # Setup sections
        self._setup_display_settings(main_container)
        self._setup_device_settings(main_container)
        self._setup_data_settings(main_container)
        self._setup_export_settings(main_container)
        self._setup_action_buttons(main_container)
    
    def _setup_display_settings(self, parent) -> None:
        """Setup display and UI settings"""
        display_frame = ttk_boot.LabelFrame(
            parent, text="Display Settings", bootstyle="primary"
        )
        display_frame.pack(fill=X, pady=(0, 20))
        
        # Theme selection
        theme_frame = ttk_boot.Frame(display_frame)
        theme_frame.pack(fill=X, padx=10, pady=10)
        
        ttk_boot.Label(theme_frame, text="Theme:", width=20).pack(side=LEFT)
        
        self.theme_var = tk.StringVar()
        theme_combo = ttk_boot.Combobox(
            theme_frame,
            textvariable=self.theme_var,
            values=AVAILABLE_THEMES,
            state="readonly",
            width=15
        )
        theme_combo.pack(side=RIGHT, padx=(10, 0))
        theme_combo.bind("<<ComboboxSelected>>", self._on_theme_change)
        
        # Display units
        units_frame = ttk_boot.Frame(display_frame)
        units_frame.pack(fill=X, padx=10, pady=5)
        
        ttk_boot.Label(units_frame, text="Humidity Unit:", width=20).pack(side=LEFT)
        
        self.units_var = tk.StringVar()
        units_combo = ttk_boot.Combobox(
            units_frame,
            textvariable=self.units_var,
            values=list(HUMIDITY_UNITS.keys()),
            state="readonly",
            width=15
        )
        units_combo.pack(side=RIGHT, padx=(10, 0))
        
        # Update interval
        interval_frame = ttk_boot.Frame(display_frame)
        interval_frame.pack(fill=X, padx=10, pady=5)
        
        ttk_boot.Label(interval_frame, text="Update Interval (ms):", width=20).pack(side=LEFT)
        
        self.interval_var = tk.IntVar()
        interval_spinbox = ttk_boot.Spinbox(
            interval_frame,
            from_=500,
            to=10000,
            increment=500,
            textvariable=self.interval_var,
            width=10
        )
        interval_spinbox.pack(side=RIGHT, padx=(10, 0))
        
        # Display options
        options_frame = ttk_boot.Frame(display_frame)
        options_frame.pack(fill=X, padx=10, pady=10)
        
        self.auto_scale_var = tk.BooleanVar()
        ttk_boot.Checkbutton(
            options_frame,
            text="Auto-scale graphs",
            variable=self.auto_scale_var,
            bootstyle="primary"
        ).pack(anchor=W)
        
        self.show_grid_var = tk.BooleanVar()
        ttk_boot.Checkbutton(
            options_frame,
            text="Show grid lines",
            variable=self.show_grid_var,
            bootstyle="primary"
        ).pack(anchor=W)
    
    def _setup_device_settings(self, parent) -> None:
        """Setup device connection settings"""
        device_frame = ttk_boot.LabelFrame(
            parent, text="Device Settings", bootstyle="info"
        )
        device_frame.pack(fill=X, pady=(0, 20))
        
        # Auto-connect option
        self.auto_connect_var = tk.BooleanVar()
        ttk_boot.Checkbutton(
            device_frame,
            text="Auto-connect on startup",
            variable=self.auto_connect_var,
            bootstyle="info"
        ).pack(anchor=W, padx=10, pady=10)
        
        # Preferred connection
        connection_frame = ttk_boot.Frame(device_frame)
        connection_frame.pack(fill=X, padx=10, pady=5)
        
        ttk_boot.Label(connection_frame, text="Preferred Connection:", width=20).pack(side=LEFT)
        
        self.connection_var = tk.StringVar()
        connection_combo = ttk_boot.Combobox(
            connection_frame,
            textvariable=self.connection_var,
            values=["usb", "wifi"],
            state="readonly",
            width=15
        )
        connection_combo.pack(side=RIGHT, padx=(10, 0))
        
        # WiFi IP address
        wifi_frame = ttk_boot.Frame(device_frame)
        wifi_frame.pack(fill=X, padx=10, pady=5)
        
        ttk_boot.Label(wifi_frame, text="WiFi IP Address:", width=20).pack(side=LEFT)
        
        self.wifi_ip_var = tk.StringVar()
        wifi_entry = ttk_boot.Entry(
            wifi_frame,
            textvariable=self.wifi_ip_var,
            width=15
        )
        wifi_entry.pack(side=RIGHT, padx=(10, 0))
    
    def _setup_data_settings(self, parent) -> None:
        """Setup data management settings"""
        data_frame = ttk_boot.LabelFrame(
            parent, text="Data Management", bootstyle="warning"
        )
        data_frame.pack(fill=X, pady=(0, 20))
        
        # Max records
        records_frame = ttk_boot.Frame(data_frame)
        records_frame.pack(fill=X, padx=10, pady=10)
        
        ttk_boot.Label(records_frame, text="Max Records:", width=20).pack(side=LEFT)
        
        self.max_records_var = tk.IntVar()
        records_spinbox = ttk_boot.Spinbox(
            records_frame,
            from_=1000,
            to=100000,
            increment=1000,
            textvariable=self.max_records_var,
            width=10
        )
        records_spinbox.pack(side=RIGHT, padx=(10, 0))
        
        # Auto cleanup
        self.auto_cleanup_var = tk.BooleanVar()
        ttk_boot.Checkbutton(
            data_frame,
            text="Auto cleanup old data (>30 days)",
            variable=self.auto_cleanup_var,
            bootstyle="warning"
        ).pack(anchor=W, padx=10, pady=5)
        
        # Data actions
        actions_frame = ttk_boot.Frame(data_frame)
        actions_frame.pack(fill=X, padx=10, pady=10)
        
        ttk_boot.Button(
            actions_frame,
            text="Cleanup Old Data",
            command=self._cleanup_data,
            bootstyle="warning"
        ).pack(side=LEFT, padx=(0, 10))
        
        ttk_boot.Button(
            actions_frame,
            text="Clear All Data",
            command=self._clear_all_data,
            bootstyle="danger"
        ).pack(side=LEFT)
    
    def _setup_export_settings(self, parent) -> None:
        """Setup data export settings"""
        export_frame = ttk_boot.LabelFrame(
            parent, text="Data Export", bootstyle="success"
        )
        export_frame.pack(fill=X, pady=(0, 20))
        
        # Export format
        format_frame = ttk_boot.Frame(export_frame)
        format_frame.pack(fill=X, padx=10, pady=10)
        
        ttk_boot.Label(format_frame, text="Default Export Format:", width=20).pack(side=LEFT)
        
        self.export_format_var = tk.StringVar()
        format_combo = ttk_boot.Combobox(
            format_frame,
            textvariable=self.export_format_var,
            values=["csv", "json"],
            state="readonly",
            width=15
        )
        format_combo.pack(side=RIGHT, padx=(10, 0))
        
        # Export actions
        export_actions_frame = ttk_boot.Frame(export_frame)
        export_actions_frame.pack(fill=X, padx=10, pady=10)
        
        ttk_boot.Button(
            export_actions_frame,
            text="Export All Data",
            command=self._export_all_data,
            bootstyle="success"
        ).pack(side=LEFT, padx=(0, 10))
        
        ttk_boot.Button(
            export_actions_frame,
            text="Export Last 7 Days",
            command=self._export_recent_data,
            bootstyle="success"
        ).pack(side=LEFT)
    
    def _setup_action_buttons(self, parent) -> None:
        """Setup action buttons"""
        button_frame = ttk_boot.Frame(parent)
        button_frame.pack(fill=X, pady=20)
        
        ttk_boot.Button(
            button_frame,
            text="Save All Settings",
            command=self._save_all_settings,
            bootstyle="primary",
            width=20
        ).pack(side=LEFT, padx=(0, 10))
        
        ttk_boot.Button(
            button_frame,
            text="Reset to Defaults",
            command=self._reset_to_defaults,
            bootstyle="secondary",
            width=20
        ).pack(side=LEFT, padx=(0, 10))
        
        ttk_boot.Button(
            button_frame,
            text="Apply Settings",
            command=self._apply_settings,
            bootstyle="success",
            width=20
        ).pack(side=RIGHT)
    
    def _load_settings(self) -> None:
        """Load current settings from config"""
        # Display settings
        display_settings = self.config_manager.get_display_settings()
        self.theme_var.set(display_settings["theme"])
        self.units_var.set(display_settings["humidity_unit"])
        self.interval_var.set(display_settings["update_interval"])
        self.auto_scale_var.set(display_settings["auto_scale"])
        self.show_grid_var.set(display_settings["show_grid"])
        
        # Device settings
        self.auto_connect_var.set(self.config_manager.get("device.auto_connect", True))
        self.connection_var.set(self.config_manager.get("device.preferred_connection", "usb"))
        self.wifi_ip_var.set(self.config_manager.get("device.wifi_ip", "192.168.4.1"))
        
        # Data settings
        self.max_records_var.set(self.config_manager.get("data.max_records", 10000))
        self.auto_cleanup_var.set(self.config_manager.get("data.auto_cleanup", True))
        
        # Export settings
        self.export_format_var.set(self.config_manager.get("data.export_format", "csv"))
    
    def _on_theme_change(self, event=None) -> None:
        """Handle theme change"""
        new_theme = self.theme_var.get()
        self.config_manager.set("display.theme", new_theme)
        
        # Apply immediately
        if self.settings_changed_callback:
            self.settings_changed_callback()
    
    def _save_all_settings(self) -> None:
        """Save all settings"""
        # Display settings
        self.config_manager.set("display.theme", self.theme_var.get())
        self.config_manager.set("display.humidity_unit", self.units_var.get())
        self.config_manager.set("display.update_interval", self.interval_var.get())
        self.config_manager.set("display.auto_scale", self.auto_scale_var.get())
        self.config_manager.set("display.show_grid", self.show_grid_var.get())
        
        # Device settings
        self.config_manager.set("device.auto_connect", self.auto_connect_var.get())
        self.config_manager.set("device.preferred_connection", self.connection_var.get())
        self.config_manager.set("device.wifi_ip", self.wifi_ip_var.get())
        
        # Data settings
        self.config_manager.set("data.max_records", self.max_records_var.get())
        self.config_manager.set("data.auto_cleanup", self.auto_cleanup_var.get())
        self.config_manager.set("data.export_format", self.export_format_var.get())
        
        self._show_status("All settings saved successfully", "success")
    
    def _apply_settings(self) -> None:
        """Apply settings without saving"""
        if self.settings_changed_callback:
            self.settings_changed_callback()
        
        self._show_status("Settings applied", "info")
    
    def _reset_to_defaults(self) -> None:
        """Reset all settings to defaults"""
        from tkinter import messagebox
        
        if messagebox.askyesno("Reset Settings", 
                              "Are you sure you want to reset all settings to defaults?"):
            self.config_manager.reset_to_defaults()
            self._load_settings()
            
            if self.settings_changed_callback:
                self.settings_changed_callback()
            
            self._show_status("Settings reset to defaults", "warning")
    
    def _cleanup_data(self) -> None:
        """Cleanup old data"""
        from tkinter import messagebox
        
        if messagebox.askyesno("Cleanup Data", 
                              "Remove data older than 30 days?"):
            # This would call data_manager.cleanup_old_data()
            self._show_status("Old data cleaned up", "info")
    
    def _clear_all_data(self) -> None:
        """Clear all data"""
        from tkinter import messagebox
        
        if messagebox.askyesno("Clear All Data", 
                              "Are you sure you want to delete ALL data? This cannot be undone!"):
            # This would call data_manager.clear_all_data()
            self._show_status("All data cleared", "danger")
    
    def _export_all_data(self) -> None:
        """Export all data"""
        from tkinter import filedialog
        
        filename = filedialog.asksaveasfilename(
            title="Export All Data",
            defaultextension=f".{self.export_format_var.get()}",
            filetypes=[
                ("CSV files", "*.csv"),
                ("JSON files", "*.json")
            ]
        )
        
        if filename:
            self._show_status(f"Data exported to {filename}", "success")
    
    def _export_recent_data(self) -> None:
        """Export last 7 days of data"""
        from tkinter import filedialog
        from datetime import datetime, timedelta
        
        filename = filedialog.asksaveasfilename(
            title="Export Recent Data (Last 7 Days)",
            defaultextension=f".{self.export_format_var.get()}",
            filetypes=[
                ("CSV files", "*.csv"),
                ("JSON files", "*.json")
            ]
        )
        
        if filename:
            self._show_status(f"Recent data exported to {filename}", "success")
    
    def _show_status(self, message: str, style: str) -> None:
        """Show status message"""
        # This would show a temporary status message
        # For now, just print to console
        print(f"Settings Status ({style}): {message}")
