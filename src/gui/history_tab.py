"""
History Tab
Historical data visualization and analysis
"""

import tkinter as tk
from tkinter import ttk
import ttkbootstrap as ttk_boot
from ttkbootstrap.constants import *
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime, timedelta
from ..utils.helpers import parse_datetime

class HistoryTab:
    """Historical data tab with filtering and analysis"""
    
    def __init__(self, parent, data_manager, config_manager):
        self.parent = parent
        self.data_manager = data_manager
        self.config_manager = config_manager
        
        # Create main frame
        self.frame = ttk_boot.Frame(parent)
        
        # Current period and filter settings
        self.current_period = "daily"
        self.start_date = None
        self.end_date = None
        
        # Add functionality to adjust the number of records displayed
        self.max_records = config_manager.get_config()['data']['max_records']
        
        self._setup_ui()
        self._setup_graph()
        self._load_data()
    
    def _setup_ui(self) -> None:
        """Setup the history UI"""
        # Control panel
        control_frame = ttk_boot.Frame(self.frame)
        control_frame.pack(fill=X, padx=20, pady=10)
        
        # Period selection
        period_frame = ttk_boot.LabelFrame(control_frame, text="Time Period")
        period_frame.pack(side=LEFT, fill=Y, padx=(0, 10))
        
        self.period_var = tk.StringVar(value="daily")
        
        periods = [("Daily", "daily"), ("Weekly", "weekly"), ("Monthly", "monthly")]
        for text, value in periods:
            btn = ttk_boot.Radiobutton(
                period_frame,
                text=text,
                variable=self.period_var,
                value=value,
                command=self._on_period_change
            )
            btn.pack(anchor=W, padx=10, pady=2)
        
        # Date filter
        filter_frame = ttk_boot.LabelFrame(control_frame, text="Date Filter")
        filter_frame.pack(side=LEFT, fill=Y, padx=(0, 10))
        
        ttk_boot.Label(filter_frame, text="Start Date:").pack(anchor=W, padx=10, pady=2)
        self.start_date_entry = ttk_boot.DateEntry(
            filter_frame,
            firstweekday=0,
            startdate=datetime.now() - timedelta(days=7),
            dateformat='%Y-%m-%d'
        )
        self.start_date_entry.pack(padx=10, pady=2)
        
        ttk_boot.Label(filter_frame, text="End Date:").pack(anchor=W, padx=10, pady=2)
        self.end_date_entry = ttk_boot.DateEntry(
            filter_frame,
            firstweekday=0,
            startdate=datetime.now(),
            dateformat='%Y-%m-%d'
        )
        self.end_date_entry.pack(padx=10, pady=2)
        
        ttk_boot.Button(
            filter_frame,
            text="Apply Filter",
            command=self._apply_date_filter,
            bootstyle="primary"
        ).pack(pady=10)
        
        ttk_boot.Button(
            filter_frame,
            text="Clear Filter",
            command=self._clear_date_filter,
            bootstyle="secondary"
        ).pack()
        
        # Statistics panel
        stats_frame = ttk_boot.LabelFrame(control_frame, text="Statistics")
        stats_frame.pack(side=RIGHT, fill=Y)
        
        self.stats_labels = {}
        stats_items = [
            ("readings", "Total Readings:"),
            ("average", "Average:"),
            ("min", "Minimum:"),
            ("max", "Maximum:"),
            ("trend", "Trend:")
        ]
        
        for key, label in stats_items:
            self.stats_labels[key] = ttk_boot.Label(
                stats_frame,
                text=f"{label} --"
            )
            self.stats_labels[key].pack(anchor=W, padx=10, pady=2)
        
        # Records display adjustment
        records_frame = ttk_boot.LabelFrame(control_frame, text="Records Display")
        records_frame.pack(side=RIGHT, fill=Y, padx=(10, 0))
        
        ttk_boot.Label(records_frame, text="Max Records:").pack(anchor=W, padx=10, pady=2)
        self.records_slider = ttk.Scale(
            records_frame, from_=10, to=self.max_records, orient='horizontal',
            command=self.update_records
        )
        self.records_slider.set(self.max_records)
        self.records_slider.pack(fill=X, padx=10, pady=2)
    
    def _setup_graph(self) -> None:
        """Setup the historical data graph"""
        # Graph frame
        graph_frame = ttk_boot.LabelFrame(
            self.frame, text="Humidity History", bootstyle="info"
        )
        graph_frame.pack(fill=BOTH, expand=True, padx=20, pady=(0, 20))
        
        # Create matplotlib figure
        self.fig, self.ax = plt.subplots(figsize=(14, 8))
        self.fig.patch.set_facecolor('#f8f9fa')
        
        # Style the plot
        self.ax.set_title("Humidity History", fontsize=16, fontweight='bold')
        self.ax.set_ylabel("Humidity (%)", fontsize=12)
        self.ax.set_xlabel("Time", fontsize=12)
        self.ax.grid(True, alpha=0.3)
        self.ax.set_ylim(0, 100)
        
        # Create canvas
        self.canvas = FigureCanvasTkAgg(self.fig, graph_frame)
        self.canvas.get_tk_widget().pack(fill=BOTH, expand=True, padx=10, pady=10)
        
        # Toolbar for zoom/pan
        toolbar_frame = ttk_boot.Frame(graph_frame)
        toolbar_frame.pack(fill=X, padx=10, pady=(0, 10))
        
        from matplotlib.backends.backend_tkagg import NavigationToolbar2Tk
        toolbar = NavigationToolbar2Tk(self.canvas, toolbar_frame)
        toolbar.update()
    
    def _load_data(self) -> None:
        """Load and display data"""
        if self.start_date and self.end_date:
            # Use date filter
            start_str = self.start_date.strftime("%Y-%m-%d")
            end_str = self.end_date.strftime("%Y-%m-%d")
            data = self.data_manager.get_readings_by_date_range(start_str, end_str)
        else:
            # Use period filter
            data = self.data_manager.get_readings_by_period(self.current_period)
        
        self._update_graph(data)
        self._update_statistics(data)
    
    def _update_graph(self, data) -> None:
        """Update the graph with new data"""
        self.ax.clear()
        
        if not data:
            self.ax.text(0.5, 0.5, 'No data available for selected period',
                        horizontalalignment='center', verticalalignment='center',
                        transform=self.ax.transAxes, fontsize=14)
            self.canvas.draw()
            return
        
        # Prepare data
        timestamps = [parse_datetime(reading["timestamp"]) for reading in data]
        humidity_values = [reading["humidity"] for reading in data]
        
        # Limit the number of records displayed
        if len(timestamps) > self.max_records:
            timestamps = timestamps[-self.max_records:]
            humidity_values = humidity_values[-self.max_records:]
        
        # Plot line with markers
        self.ax.plot(timestamps, humidity_values, 'b-', linewidth=2, alpha=0.8, 
                    marker='o', markersize=3, label="Humidity")
        
        # Add threshold lines
        thresholds = self.config_manager.get_thresholds()
        self.ax.axhline(y=thresholds["high"], color='red', linestyle='--', 
                       alpha=0.7, label=f'High Threshold ({thresholds["high"]:.1f}%)')
        self.ax.axhline(y=thresholds["low"], color='orange', linestyle='--', 
                       alpha=0.7, label=f'Low Threshold ({thresholds["low"]:.1f}%)')
        
        # Styling
        self.ax.set_title(f"Humidity History - {self.current_period.title()}", 
                         fontsize=16, fontweight='bold')
        self.ax.set_ylabel("Humidity (%)", fontsize=12)
        self.ax.set_xlabel("Time", fontsize=12)
        self.ax.grid(True, alpha=0.3)
        self.ax.legend()
        self.ax.set_ylim(0, 100)
        
        # Format x-axis based on data range
        if len(timestamps) > 0:
            time_span = timestamps[-1] - timestamps[0]
            
            if time_span.days > 7:
                # Show dates for longer periods
                import matplotlib.dates as mdates
                self.ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
                self.ax.xaxis.set_major_locator(mdates.DayLocator(interval=max(1, time_span.days // 10)))
            else:
                # Show times for shorter periods
                import matplotlib.dates as mdates
                self.ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
                if time_span.seconds > 3600:  # More than 1 hour
                    self.ax.xaxis.set_major_locator(mdates.HourLocator(interval=max(1, time_span.seconds // 3600 // 6)))
        
        # Rotate x-axis labels for better readability
        plt.setp(self.ax.xaxis.get_majorticklabels(), rotation=45)
        
        # Tight layout
        self.fig.tight_layout()
        self.canvas.draw()
    
    def _update_statistics(self, data) -> None:
        """Update statistics display"""
        if not data:
            for key in self.stats_labels:
                self.stats_labels[key].config(text=f"{self.stats_labels[key].cget('text').split(':')[0]}: --")
            return
        
        humidity_values = [reading["humidity"] for reading in data]
        
        # Calculate statistics
        avg_humidity = sum(humidity_values) / len(humidity_values)
        min_humidity = min(humidity_values)
        max_humidity = max(humidity_values)
        
        # Calculate trend
        trend = 0.0
        if len(humidity_values) >= 10:
            mid_point = len(humidity_values) // 2
            first_half_avg = sum(humidity_values[:mid_point]) / mid_point
            second_half_avg = sum(humidity_values[mid_point:]) / (len(humidity_values) - mid_point)
            trend = ((second_half_avg - first_half_avg) / first_half_avg) * 100 if first_half_avg != 0 else 0
        
        # Update labels
        self.stats_labels["readings"].config(text=f"Total Readings: {len(data)}")
        self.stats_labels["average"].config(text=f"Average: {avg_humidity:.1f}%")
        self.stats_labels["min"].config(text=f"Minimum: {min_humidity:.1f}%")
        self.stats_labels["max"].config(text=f"Maximum: {max_humidity:.1f}%")
        
        trend_text = f"Trend: {trend:+.1f}%"
        trend_style = "success" if trend >= 0 else "danger"
        self.stats_labels["trend"].config(text=trend_text, bootstyle=trend_style)
    
    def _on_period_change(self) -> None:
        """Handle period selection change"""
        self.current_period = self.period_var.get()
        
        # Clear date filter when period changes
        self.start_date = None
        self.end_date = None
        
        self._load_data()
    
    def _apply_date_filter(self) -> None:
        """Apply custom date filter"""
        try:
            self.start_date = self.start_date_entry.entry.get_date()
            self.end_date = self.end_date_entry.entry.get_date()
            
            if self.start_date > self.end_date:
                self.start_date, self.end_date = self.end_date, self.start_date
            
            self._load_data()
            
        except Exception as e:
            tk.messagebox.showerror("Date Error", f"Invalid date selection: {e}")
    
    def _clear_date_filter(self) -> None:
        """Clear custom date filter"""
        self.start_date = None
        self.end_date = None
        
        # Reset date entries
        self.start_date_entry.entry.set_date(datetime.now() - timedelta(days=7))
        self.end_date_entry.entry.set_date(datetime.now())
        
        self._load_data()
    
    def refresh_settings(self) -> None:
        """Refresh display based on settings changes"""
        self._load_data()
    
    def update_records(self, value) -> None:
        """Update the maximum number of records displayed"""
        self.max_records = int(float(value))
        # Only refresh if the graph has been initialized
        if hasattr(self, 'ax') and self.ax is not None:
            self._load_data()
    def refresh_chart(self) -> None:
        """Refresh the chart with the current settings"""
        # Simply call _load_data which already handles the data loading and graph updating
        self._load_data()
