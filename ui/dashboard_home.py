"""Dashboard home screen."""
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QFrame, QGridLayout, QPushButton)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from services.dashboard_service import DashboardService


class DashboardHome(QWidget):
    """Dashboard home screen with statistics and charts."""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        """Initialize UI."""
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Welcome message
        welcome_label = QLabel("Dashboard")
        welcome_font = QFont()
        welcome_font.setPointSize(20)
        welcome_font.setBold(True)
        welcome_label.setFont(welcome_font)
        layout.addWidget(welcome_label)
        
        # Refresh button
        refresh_layout = QHBoxLayout()
        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self.refresh_data)
        refresh_btn.setMaximumWidth(100)
        refresh_layout.addWidget(refresh_btn)
        refresh_layout.addStretch()
        layout.addLayout(refresh_layout)
        
        # Stats cards grid (Today / This Month)
        stats_grid = QGridLayout()
        stats_grid.setSpacing(15)
        stats_grid.setColumnStretch(0, 1)
        stats_grid.setColumnStretch(1, 1)
        
        # Headers
        today_label = QLabel("Today")
        today_label.setStyleSheet("font-weight: bold; font-size: 14px; color: #666;")
        stats_grid.addWidget(today_label, 0, 0)
        month_label = QLabel("This Month")
        month_label.setStyleSheet("font-weight: bold; font-size: 14px; color: #666;")
        stats_grid.addWidget(month_label, 0, 1)

        # Cards
        self.today_purchase_card = self.create_stat_card("Purchased", "#4CAF50")
        stats_grid.addWidget(self.today_purchase_card, 1, 0)
        self.today_sale_card = self.create_stat_card("Sold", "#FF9800")
        stats_grid.addWidget(self.today_sale_card, 2, 0)

        self.month_purchase_card = self.create_stat_card("Purchased", "#4CAF50")
        stats_grid.addWidget(self.month_purchase_card, 1, 1)
        self.month_sale_card = self.create_stat_card("Sold", "#FF9800")
        stats_grid.addWidget(self.month_sale_card, 2, 1)

        layout.addLayout(stats_grid)
        
        # Chart section
        chart_label = QLabel("Monthly Transactions")
        chart_label.setStyleSheet("font-weight: bold; font-size: 16px; margin-top: 20px;")
        layout.addWidget(chart_label)
        
        # Create matplotlib figure
        self.figure = Figure(figsize=(10, 5))
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)
        
        layout.addStretch()
        
        # Load initial data
        self.refresh_data()
    
    def create_stat_card(self, title, color):
        """Create a statistics card with always-visible text."""
        card = QFrame()
        card.setObjectName("statCard")
        card.setStyleSheet(
            f"""
            QFrame#statCard {{
                background-color: {color};
                border-radius: 10px;
                padding: 14px;
            }}
            QFrame#statCard QLabel {{
                color: #FFFFFF;
            }}
            """
        )
        card.setFixedHeight(120)

        layout = QVBoxLayout(card)
        layout.setSpacing(6)
        layout.setContentsMargins(10, 10, 10, 10)

        title_label = QLabel(title)
        title_label.setStyleSheet("font-size: 12px; letter-spacing: 0.5px; text-transform: uppercase;")
        layout.addWidget(title_label, alignment=Qt.AlignLeft)

        qty_label = QLabel("0 qty")
        qty_label.setStyleSheet("font-size: 26px; font-weight: 800;")
        layout.addWidget(qty_label, alignment=Qt.AlignLeft)

        amt_label = QLabel("₹ 0.00")
        amt_label.setStyleSheet("font-size: 13px; font-weight: 600;")
        layout.addWidget(amt_label, alignment=Qt.AlignLeft)

        layout.addStretch()
        card.qty_label = qty_label
        card.amt_label = amt_label
        return card
    
    def update_stat_card(self, card, qty_value, amount_value):
        """Update statistics card values, tolerating None/invalid numbers."""
        try:
            qty_val = float(qty_value or 0)
        except Exception:
            qty_val = 0.0

        try:
            amt_val = float(amount_value or 0)
        except Exception:
            amt_val = 0.0

        card.qty_label.setText(f"{qty_val:,.0f} qty")
        card.amt_label.setText(f"₹ {amt_val:,.2f}")
    
    def refresh_data(self):
        """Refresh dashboard data."""
        # Get today's stats
        today_stats = DashboardService.get_today_stats()
        self.update_stat_card(self.today_purchase_card, today_stats['purchase_qty'], today_stats['purchase_amount'])
        self.update_stat_card(self.today_sale_card, today_stats['sale_qty'], today_stats['sale_amount'])
        
        # Get month's stats
        month_stats = DashboardService.get_month_stats()
        self.update_stat_card(self.month_purchase_card, month_stats['purchase_qty'], month_stats['purchase_amount'])
        self.update_stat_card(self.month_sale_card, month_stats['sale_qty'], month_stats['sale_amount'])
        
        # Update chart
        self.update_chart()
    
    def update_chart(self):
        """Update the monthly chart."""
        chart_data = DashboardService.get_monthly_chart_data()
        
        self.figure.clear()
        
        # Create subplots
        ax1 = self.figure.add_subplot(111)
        ax2 = ax1.twinx()
        
        # Plot quantity lines
        line1 = ax1.plot(chart_data['dates'], chart_data['purchase_qty'], 
                         color='#4CAF50', marker='o', linewidth=2, label='Purchased Qty')
        line2 = ax1.plot(chart_data['dates'], chart_data['sale_qty'], 
                         color='#FF9800', marker='s', linewidth=2, label='Sold Qty')
        
        # Plot amount lines
        line3 = ax2.plot(chart_data['dates'], chart_data['purchase_amt'], 
                         color='#2E7D32', marker='o', linewidth=2, linestyle='--', label='Purchased Amt', alpha=0.7)
        line4 = ax2.plot(chart_data['dates'], chart_data['sale_amt'], 
                         color='#E65100', marker='s', linewidth=2, linestyle='--', label='Sold Amt', alpha=0.7)
        
        # Labels and title
        ax1.set_xlabel('Date', fontsize=10)
        ax1.set_ylabel('Quantity', fontsize=10, color='black')
        ax2.set_ylabel('Amount (₹)', fontsize=10, color='black')
        ax1.set_title('Daily Purchase & Sale Trends', fontsize=12, fontweight='bold')
        
        # Rotate x-axis labels
        ax1.tick_params(axis='x', rotation=45)
        
        # Grid
        ax1.grid(True, alpha=0.3)
        
        # Combined legend
        lines = line1 + line2 + line3 + line4
        labels = [l.get_label() for l in lines]
        ax1.legend(lines, labels, loc='upper left', fontsize=8)
        
        self.figure.tight_layout()
        self.canvas.draw()
