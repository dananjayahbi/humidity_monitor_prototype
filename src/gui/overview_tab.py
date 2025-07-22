"""
Overview Tab
Main dashboard showing current humidity and real-time graph
"""

import tkinter as tk
from tkinter import ttk
import ttkbootstrap as ttk_boot
from ttkbootstrap.constants import *
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.animation import FuncAnimation
from datetime import datetime
import numpy as np

from ..utils.constants import GRAPH_DISPLAY_POINTS, UPDATE_INTERVAL

class OverviewTab:
    """Overview tab with current readings and real-time graph"""
    
    def __init__(self, parent, data_manager, sensor_manager, alert_manager, config_manager):
        self.parent = parent
        self.data_manager = data_manager
        self.sensor_manager = sensor_manager
        self.alert_manager = alert_manager
        self.config_manager = config_manager
        
        # Create main frame
        self.frame = ttk_boot.Frame(parent)
        
        # Current humidity value
        self.current_humidity = 0.0
        self.connection_status = "Disconnected"
        
        self._setup_ui()
        self._setup_graph()
        self._start_updates()
    
    def _setup_ui(self) -> None:
        """Setup the overview UI"""
        # Top section - Current reading and controls
        top_frame = ttk_boot.Frame(self.frame)
        top_frame.pack(fill=X, padx=20, pady=10)
        
        # Current humidity display
        humidity_frame = ttk_boot.LabelFrame(
            top_frame, text="Current Humidity", bootstyle="info"
        )
        humidity_frame.pack(side=LEFT, fill=BOTH, expand=True, padx=(0, 10))
        
        self.humidity_value = ttk_boot.Label(
            humidity_frame,
            text="--.--%",
            font=("Arial", 36, "bold"),
            bootstyle="info"
        )
        self.humidity_value.pack(pady=20)
        
        self.last_update = ttk_boot.Label(
            humidity_frame,
            text="No readings yet",
            bootstyle="secondary"
        )
        self.last_update.pack()
        
        # Control panel
        control_frame = ttk_boot.LabelFrame(
            top_frame, text="Control Panel", bootstyle="primary"
        )
        control_frame.pack(side=RIGHT, fill=Y, padx=(10, 0))
        
        self.start_button = ttk_boot.Button(
            control_frame,
            text="Start Monitoring",
            bootstyle="success",
            command=self._toggle_monitoring,
            width=15
        )
        self.start_button.pack(pady=5)
        
        self.connect_button = ttk_boot.Button(
            control_frame,
            text="Connect Device",
            bootstyle="primary",
            command=self._connect_device,
            width=15
        )
        self.connect_button.pack(pady=5)
        
        # Status display
        self.status_text = ttk_boot.Label(
            control_frame,
            text="Click 'Connect Device' to start",
            bootstyle="secondary",
            wraplength=150
        )
        self.status_text.pack(pady=10)
        
        # Statistics section
        stats_frame = ttk_boot.LabelFrame(
            top_frame, text="Today's Statistics", bootstyle="info"
        )
        stats_frame.pack(side=RIGHT, fill=Y, padx=(10, 0))
        
        self.avg_label = ttk_boot.Label(stats_frame, text="Average: --.--%")
        self.avg_label.pack(anchor=W, padx=10, pady=2)
        
        self.min_label = ttk_boot.Label(stats_frame, text="Minimum: --.--%")
        self.min_label.pack(anchor=W, padx=10, pady=2)
        
        self.max_label = ttk_boot.Label(stats_frame, text="Maximum: --.--%")
        self.max_label.pack(anchor=W, padx=10, pady=2)
        
        self.trend_label = ttk_boot.Label(stats_frame, text="Trend: --.--%")
        self.trend_label.pack(anchor=W, padx=10, pady=2)
    
    def _setup_graph(self) -> None:
        """Setup the real-time graph"""
        # Graph frame
        graph_frame = ttk_boot.LabelFrame(
            self.frame, text="Real-Time Humidity Chart", bootstyle="secondary"
        )
        graph_frame.pack(fill=BOTH, expand=True, padx=20, pady=10)
        
        # Create matplotlib figure
        self.fig, self.ax = plt.subplots(figsize=(12, 6))
        self.fig.patch.set_facecolor('#f8f9fa')
        
        # Style the plot
        self.ax.set_title("Humidity Levels (Last 50 Readings)", fontsize=14, fontweight='bold')
        self.ax.set_ylabel("Humidity (%)", fontsize=12)
        self.ax.set_xlabel("Time", fontsize=12)
        self.ax.grid(True, alpha=0.3)
        self.ax.set_ylim(0, 100)
        
        # Initialize empty line
        self.line, = self.ax.plot([], [], 'b-', linewidth=2, alpha=0.8, label="Humidity")
        self.ax.legend()
        
        # Add threshold lines (will be updated when thresholds change)
        self.high_line = self.ax.axhline(y=70, color='red', linestyle='--', alpha=0.7, label='High Threshold')
        self.low_line = self.ax.axhline(y=30, color='orange', linestyle='--', alpha=0.7, label='Low Threshold')
        
        # Create canvas
        self.canvas = FigureCanvasTkAgg(self.fig, graph_frame)
        self.canvas.get_tk_widget().pack(fill=BOTH, expand=True, padx=10, pady=10)
        
        # Tight layout
        self.fig.tight_layout()
    
    def _start_updates(self) -> None:
        """Start periodic updates"""
        self._update_display()
        self.frame.after(UPDATE_INTERVAL, self._start_updates)
    
    def _update_display(self) -> None:
        """Update the display with latest data"""
        # Get recent data
        recent_data = self.data_manager.get_recent_readings(GRAPH_DISPLAY_POINTS)
        
        if recent_data:
            # Update graph
            timestamps = []
            humidity_values = []
            
            for i, reading in enumerate(recent_data):
                timestamps.append(i)  # Use index for x-axis
                humidity_values.append(reading["humidity"])
            
            # Update line data
            self.line.set_data(timestamps, humidity_values)
            
            # Update x-axis
            if len(timestamps) > 1:
                self.ax.set_xlim(0, len(timestamps) - 1)
                
                # Set x-tick labels to show time
                if len(recent_data) >= 5:
                    tick_indices = np.linspace(0, len(recent_data) - 1, 5, dtype=int)
                    tick_labels = []
                    for idx in tick_indices:
                        time_str = recent_data[idx]["timestamp"].split(" ")[1][:5]  # HH:MM
                        tick_labels.append(time_str)
                    
                    self.ax.set_xticks(tick_indices)
                    self.ax.set_xticklabels(tick_labels)
            
            # Update threshold lines
            thresholds = self.config_manager.get_thresholds()
            self.high_line.set_ydata([thresholds["high"], thresholds["high"]])
            self.low_line.set_ydata([thresholds["low"], thresholds["low"]])
            
            # Redraw canvas
            self.canvas.draw()
            
            # Update current humidity display
            latest = recent_data[-1]
            self.current_humidity = latest["humidity"]
            
        # Update statistics
        self._update_statistics()
    
    def _update_statistics(self) -> None:
        """Update daily statistics"""
        stats = self.data_manager.get_statistics("daily")
        
        self.avg_label.config(text=f"Average: {stats['average']:.1f}%")
        self.min_label.config(text=f"Minimum: {stats['min']:.1f}%")
        self.max_label.config(text=f"Maximum: {stats['max']:.1f}%")
        
        trend_text = f"Trend: {stats['trend']:+.1f}%"
        trend_style = "success" if stats['trend'] >= 0 else "danger"
        self.trend_label.config(text=trend_text, bootstyle=trend_style)
    
    def update_current_humidity(self, humidity: float) -> None:
        """Update current humidity display"""
        self.current_humidity = humidity
        self.humidity_value.config(text=f"{humidity:.1f}%")
        self.last_update.config(text=f"Updated: {datetime.now().strftime('%H:%M:%S')}")
        
        # Update color based on thresholds
        thresholds = self.config_manager.get_thresholds()
        if humidity > thresholds["high"]:
            self.humidity_value.config(bootstyle="danger")
        elif humidity < thresholds["low"]:
            self.humidity_value.config(bootstyle="warning")
        else:
            self.humidity_value.config(bootstyle="success")
    
    def update_connection_status(self, connected: bool, message: str) -> None:
        """Update connection status"""
        self.connection_status = message
        self.status_text.config(text=message)
        
        if connected:
            self.connect_button.config(text="Disconnect", bootstyle="secondary")
            self.start_button.config(state="normal")
        else:
            self.connect_button.config(text="Connect Device", bootstyle="primary")
            self.start_button.config(state="disabled")
    
    def _connect_device(self) -> None:
        """Handle device connection"""
        if self.sensor_manager.is_connected():
            self.sensor_manager.disconnect()
            self.update_connection_status(False, "Disconnected")
        else:
            success, message = self.sensor_manager.auto_connect()
            self.update_connection_status(success, message)
    
    def _toggle_monitoring(self) -> None:
        """Toggle monitoring on/off"""
        if self.sensor_manager.is_connected():
            if hasattr(self.sensor_manager, 'is_running') and self.sensor_manager.is_running:
                self.sensor_manager.stop_monitoring()
                self.start_button.config(text="Start Monitoring", bootstyle="success")
            else:
                if self.sensor_manager.start_monitoring():
                    self.start_button.config(text="Stop Monitoring", bootstyle="danger")
    
    def refresh_settings(self) -> None:
        """Refresh display based on settings changes"""
        # Update threshold lines
        thresholds = self.config_manager.get_thresholds()
        self.high_line.set_ydata([thresholds["high"], thresholds["high"]])
        self.low_line.set_ydata([thresholds["low"], thresholds["low"]])
        
        # Redraw canvas
        self.canvas.draw()
        
        # Update statistics
        self._update_statistics()
