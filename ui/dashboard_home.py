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
        self.setStyleSheet("background-color: #F5F5F5;")
        layout = QVBoxLayout(self)
        layout.setSpacing(25)
        layout.setContentsMargins(40, 35, 40, 35)
        
        # Header with title and refresh button
        header_layout = QHBoxLayout()
        header_layout.setSpacing(0)
        
        welcome_label = QLabel("Dashboard")
        welcome_font = QFont()
        welcome_font.setPointSize(22)
        welcome_font.setBold(True)
        welcome_label.setFont(welcome_font)
        welcome_label.setStyleSheet("color: #212121;")
        header_layout.addWidget(welcome_label)
        
        header_layout.addStretch()
        
        refresh_btn = QPushButton("↻ Refresh")
        refresh_btn.clicked.connect(self.refresh_data)
        refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #1976D2;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 20px;
                font-size: 13px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #1565C0;
            }
            QPushButton:pressed {
                background-color: #0D47A1;
            }
        """)
        header_layout.addWidget(refresh_btn)
        
        layout.addLayout(header_layout)
        
        # Main stats section - two columns
        main_stats_layout = QHBoxLayout()
        main_stats_layout.setSpacing(25)
        
        # Left: Overview info card
        self.overview_card = self.create_overview_card()
        main_stats_layout.addWidget(self.overview_card)
        
        # Right: Transaction stats grid
        right_container = QWidget()
        right_layout = QVBoxLayout(right_container)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(15)
        
        # Stats cards grid (Today / This Month) - compact layout
        stats_grid = QGridLayout()
        stats_grid.setHorizontalSpacing(20)
        stats_grid.setVerticalSpacing(15)
        
        # Headers
        today_label = QLabel("Today")
        today_label.setStyleSheet("font-weight: 700; font-size: 13px; color: #757575; text-transform: uppercase; letter-spacing: 0.5px;")
        stats_grid.addWidget(today_label, 0, 0, Qt.AlignLeft)
        
        month_label = QLabel("This Month")
        month_label.setStyleSheet("font-weight: 700; font-size: 13px; color: #757575; text-transform: uppercase; letter-spacing: 0.5px;")
        stats_grid.addWidget(month_label, 0, 1, Qt.AlignLeft)

        # Cards - more compact
        self.today_purchase_card = self.create_stat_card("Purchased", "#43A047")
        stats_grid.addWidget(self.today_purchase_card, 1, 0)
        self.today_sale_card = self.create_stat_card("Sold", "#FB8C00")
        stats_grid.addWidget(self.today_sale_card, 2, 0)

        self.month_purchase_card = self.create_stat_card("Purchased", "#43A047")
        stats_grid.addWidget(self.month_purchase_card, 1, 1)
        self.month_sale_card = self.create_stat_card("Sold", "#FB8C00")
        stats_grid.addWidget(self.month_sale_card, 2, 1)

        right_layout.addLayout(stats_grid)
        main_stats_layout.addWidget(right_container)
        
        layout.addLayout(main_stats_layout)
        
        # Chart section
        chart_label = QLabel("Monthly Trends")
        chart_label.setStyleSheet("font-weight: 700; font-size: 16px; color: #212121; margin-top: 15px;")
        layout.addWidget(chart_label)
        
        # Create matplotlib figure with better sizing
        self.figure = Figure(figsize=(12, 4.5), facecolor='white')
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setStyleSheet("background-color: white; border-radius: 8px;")
        self.canvas.setGraphicsEffect(self.create_shadow())
        layout.addWidget(self.canvas)
        
        layout.addStretch()
        
        # Load initial data
        self.refresh_data()
    
    def create_stat_card(self, title, color):
        """Create a compact, modern statistics card."""
        card = QFrame()
        card.setObjectName("statCard")
        card.setStyleSheet(
            f"""
            QFrame#statCard {{
                background-color: {color};
                border-radius: 8px;
                border: none;
            }}
            QFrame#statCard QLabel {{
                color: #FFFFFF;
                background: transparent;
            }}
            """
        )
        card.setFixedSize(240, 100)
        card.setGraphicsEffect(self.create_shadow())

        layout = QVBoxLayout(card)
        layout.setSpacing(4)
        layout.setContentsMargins(16, 14, 16, 14)

        title_label = QLabel(title.upper())
        title_label.setStyleSheet("font-size: 11px; letter-spacing: 0.8px; font-weight: 600; background: transparent;")
        title_label.setAutoFillBackground(False)
        layout.addWidget(title_label, alignment=Qt.AlignLeft)

        qty_label = QLabel("0 qty")
        qty_label.setStyleSheet("font-size: 24px; font-weight: 700; margin-top: 2px; background: transparent;")
        qty_label.setAutoFillBackground(False)
        layout.addWidget(qty_label, alignment=Qt.AlignLeft)

        amt_label = QLabel("₹ 0.00")
        amt_label.setStyleSheet("font-size: 12px; font-weight: 500; margin-top: 1px; background: transparent;")
        amt_label.setAutoFillBackground(False)
        layout.addWidget(amt_label, alignment=Qt.AlignLeft)

        card.qty_label = qty_label
        card.amt_label = amt_label
        return card
    
    def create_overview_card(self):
        """Create overview info card with system stats."""
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: #FFFFFF;
                border: none;
                border-radius: 8px;
            }
        """)
        card.setFixedWidth(320)
        card.setFixedHeight(230)
        card.setGraphicsEffect(self.create_shadow())
        
        layout = QVBoxLayout(card)
        layout.setSpacing(14)
        layout.setContentsMargins(22, 20, 22, 20)
        
        # Title
        title_label = QLabel("OVERVIEW")
        title_label.setStyleSheet("font-weight: 700; font-size: 13px; color: #757575; letter-spacing: 0.8px;")
        layout.addWidget(title_label)
        
        # Info rows
        self.distributor_label = self.create_info_row("Distributors", "0")
        layout.addWidget(self.distributor_label)
        
        self.ticket_label = self.create_info_row("Ticket Types", "0")
        layout.addWidget(self.ticket_label)
        
        self.party_label = self.create_info_row("Parties", "0")
        layout.addWidget(self.party_label)
        
        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setStyleSheet("background-color: #E0E0E0; max-height: 1px;")
        layout.addWidget(separator)
        
        self.stock_label = self.create_info_row("In Stock (Today)", "0 Qty | ₹ 0.00")
        layout.addWidget(self.stock_label)
        
        layout.addStretch()
        
        return card
    
    def create_info_row(self, label_text, value_text):
        """Create an info row with label and value."""
        row = QWidget()
        row_layout = QHBoxLayout(row)
        row_layout.setContentsMargins(0, 0, 0, 0)
        row_layout.setSpacing(0)
        
        label = QLabel(label_text)
        label.setStyleSheet("font-size: 13px; color: #616161; font-weight: 500;")
        row_layout.addWidget(label)
        
        row_layout.addStretch()
        
        value = QLabel(value_text)
        value.setStyleSheet("font-size: 13px; color: #212121; font-weight: 700;")
        value.setObjectName("value")
        row_layout.addWidget(value)
        
        return row
    
    def create_shadow(self):
        """Create a subtle drop shadow effect."""
        from PySide6.QtWidgets import QGraphicsDropShadowEffect
        from PySide6.QtGui import QColor
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setXOffset(0)
        shadow.setYOffset(2)
        shadow.setColor(QColor(0, 0, 0, 25))
        return shadow
    
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
    
    def update_overview_card(self, overview):
        """Update overview card with counts and stock info."""
        # Update distributor count
        dist_value = self.distributor_label.findChild(QLabel, "value")
        if dist_value:
            dist_value.setText(str(overview['distributor_count']))
        
        # Update ticket types count
        ticket_value = self.ticket_label.findChild(QLabel, "value")
        if ticket_value:
            ticket_value.setText(str(overview['product_count']))
        
        # Update parties count
        party_value = self.party_label.findChild(QLabel, "value")
        if party_value:
            party_value.setText(str(overview['party_count']))
        
        # Update stock info
        stock_value = self.stock_label.findChild(QLabel, "value")
        if stock_value:
            stock_qty = float(overview['stock_qty'] or 0)
            stock_amt = float(overview['stock_amount'] or 0)
            stock_value.setText(f"{stock_qty:,.0f} Qty | ₹ {stock_amt:,.2f}")
    
    def refresh_data(self):
        """Refresh dashboard data."""
        # Get overview stats
        overview = DashboardService.get_overview_stats()
        self.update_overview_card(overview)
        
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
