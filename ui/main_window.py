"""Main dashboard window for alLot application."""
from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                               QPushButton, QLabel, QFrame, QMessageBox, QStackedWidget)
from PySide6.QtCore import Qt, QTimer, QDateTime
from PySide6.QtGui import QFont, QAction
from ui.dashboard_home import DashboardHome
from ui.control_panel.distributors import DistributorsPanel
from ui.control_panel.parties import PartiesPanel
from ui.control_panel.products import ProductsPanel
from ui.control_panel.settings import SettingsPanel
from ui.purchase_window import PurchaseWindow
from ui.sale_window import SaleWindow
from ui.stock_window import StockWindow
from ui.reports_window import ReportsWindow


class MainWindow(QMainWindow):
    """Main application window with dashboard."""
    
    def __init__(self, user):
        super().__init__()
        self.user = user
        self.init_ui()
    
    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle("alLot")
        self.setMinimumSize(1200, 700)
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Header
        header = self.create_header()
        main_layout.addWidget(header)
        
        # Content area with sidebar and stacked widget
        content_layout = QHBoxLayout()
        content_layout.setSpacing(0)
        content_layout.setContentsMargins(0, 0, 0, 0)
        
        # Left sidebar
        sidebar = self.create_sidebar()
        content_layout.addWidget(sidebar)
        
        # Stacked widget for content
        self.stacked_widget = QStackedWidget()
        
        # Dashboard home screen
        self.dashboard_home = DashboardHome()
        self.stacked_widget.addWidget(self.dashboard_home)
        
        # Create control panel screens first (needed for control panel home)
        self.distributors_panel = DistributorsPanel()
        self.parties_panel = PartiesPanel()
        self.products_panel = ProductsPanel()
        self.settings_panel = SettingsPanel()
        
        # Control panel home screen (uses panels created above)
        self.control_panel_home = self.create_control_panel_home()
        self.stacked_widget.addWidget(self.control_panel_home)
        
        # Add transaction screens
        self.purchase_window = PurchaseWindow()
        self.sale_window = SaleWindow()
        self.stock_window = StockWindow()
        self.reports_window = ReportsWindow()
        
        self.stacked_widget.addWidget(self.purchase_window)
        self.stacked_widget.addWidget(self.sale_window)
        self.stacked_widget.addWidget(self.stock_window)
        self.stacked_widget.addWidget(self.reports_window)
        
        content_layout.addWidget(self.stacked_widget)
        
        content_widget = QWidget()
        content_widget.setLayout(content_layout)
        main_layout.addWidget(content_widget)
        
        # Set default to dashboard home
        self.stacked_widget.setCurrentWidget(self.dashboard_home)
        
        self.showMaximized()
    
    def create_menu_bar(self):
        """Create menu bar."""
        menubar = self.menuBar()
        
        # Control Panel menu
        control_menu = menubar.addMenu("Control Panel")
        
        distributors_action = QAction("Distributors", self)
        distributors_action.triggered.connect(lambda: self.stacked_widget.setCurrentWidget(self.distributors_panel))
        control_menu.addAction(distributors_action)
        
        parties_action = QAction("Parties", self)
        parties_action.triggered.connect(lambda: self.stacked_widget.setCurrentWidget(self.parties_panel))
        control_menu.addAction(parties_action)
        
        products_action = QAction("Products", self)
        products_action.triggered.connect(lambda: self.stacked_widget.setCurrentWidget(self.products_panel))
        control_menu.addAction(products_action)
        
        control_menu.addSeparator()
        
        settings_action = QAction("Settings", self)
        settings_action.triggered.connect(lambda: self.stacked_widget.setCurrentWidget(self.settings_panel))
        control_menu.addAction(settings_action)
        
        # Transactions menu
        transactions_menu = menubar.addMenu("Transactions")
        
        purchase_action = QAction("Purchase", self)
        purchase_action.triggered.connect(self.show_purchase)
        transactions_menu.addAction(purchase_action)
        
        sale_action = QAction("Sale", self)
        sale_action.triggered.connect(self.show_sale)
        transactions_menu.addAction(sale_action)
        
        # View menu
        view_menu = menubar.addMenu("View")
        
        stock_action = QAction("Stock", self)
        stock_action.triggered.connect(self.show_stock)
        view_menu.addAction(stock_action)
        
        reports_action = QAction("Reports", self)
        reports_action.triggered.connect(self.show_reports)
        view_menu.addAction(reports_action)
        
        view_menu.addSeparator()
        
        home_action = QAction("Dashboard Home", self)
        home_action.triggered.connect(lambda: self.stacked_widget.setCurrentIndex(0))
        view_menu.addAction(home_action)
        
        # Help menu
        help_menu = menubar.addMenu("Help")
        
        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def create_header(self):
        """Create header section."""
        header = QFrame()
        header.setStyleSheet("background-color: #1976D2; color: white;")
        header.setFixedHeight(80)
        
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(30, 10, 30, 10)
        
        # Title
        title_label = QLabel("alLot")
        title_font = QFont()
        title_font.setPointSize(24)
        title_font.setBold(True)
        title_label.setFont(title_font)
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        # Right side container with username and datetime
        self.info_label = QLabel()
        info_font = QFont()
        info_font.setPointSize(11)
        info_font.setBold(True)
        self.info_label.setFont(info_font)
        self.info_label.setAlignment(Qt.AlignRight)
        self.info_label.setStyleSheet("line-height: 1.2;")
        header_layout.addWidget(self.info_label)
        
        # Start timer for updating datetime
        self.datetime_timer = QTimer()
        self.datetime_timer.timeout.connect(self.update_datetime)
        self.datetime_timer.start(1000)  # Update every second
        self.update_datetime()  # Initial update
        
        return header
    
    def update_datetime(self):
        """Update datetime label."""
        current_datetime = QDateTime.currentDateTime()
        time_text = current_datetime.toString("hh:mm:ss AP")
        date_text = current_datetime.toString("ddd, MM/dd/yyyy")
        self.info_label.setText(f"{self.user.username}<br>{time_text}<br>{date_text}")
    
    def create_sidebar(self):
        """Create left sidebar with navigation."""
        sidebar = QFrame()
        sidebar.setStyleSheet("background-color: #263238; color: white;")
        sidebar.setFixedWidth(220)
        
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setSpacing(5)
        sidebar_layout.setContentsMargins(10, 20, 10, 20)
        
        # Dashboard
        btn_dashboard = self.create_sidebar_button("Dashboard")
        btn_dashboard.clicked.connect(lambda: self.stacked_widget.setCurrentWidget(self.dashboard_home))
        sidebar_layout.addWidget(btn_dashboard)
        
        # Purchase
        btn_purchase = self.create_sidebar_button("Purchase")
        btn_purchase.clicked.connect(self.show_purchase)
        sidebar_layout.addWidget(btn_purchase)
        
        # Sale
        btn_sale = self.create_sidebar_button("Sale")
        btn_sale.clicked.connect(self.show_sale)
        sidebar_layout.addWidget(btn_sale)
        
        # View Stock
        btn_stock = self.create_sidebar_button("View Stock")
        btn_stock.clicked.connect(self.show_stock)
        sidebar_layout.addWidget(btn_stock)
        
        # Control Panel
        btn_control_panel = self.create_sidebar_button("Control Panel")
        btn_control_panel.clicked.connect(lambda: self.stacked_widget.setCurrentWidget(self.control_panel_home))
        sidebar_layout.addWidget(btn_control_panel)
        
        sidebar_layout.addStretch()
        
        return sidebar
    
    def create_sidebar_button(self, text):
        """Create a sidebar navigation button."""
        button = QPushButton(text)
        button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: white;
                border: none;
                padding: 12px 15px;
                text-align: left;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #37474F;
            }
            QPushButton:pressed {
                background-color: #1976D2;
            }
        """)
        return button
    
    def create_control_panel_home(self):
        """Create control panel home screen with all sections in one scrollable page."""
        from PySide6.QtWidgets import QScrollArea
        
        # Create scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("QScrollArea { border: none; background-color: #F5F5F5; }")
        
        # Main container widget
        container = QWidget()
        container.setStyleSheet("background-color: #F5F5F5;")
        layout = QVBoxLayout(container)
        layout.setSpacing(30)
        layout.setContentsMargins(40, 35, 40, 35)
        
        # Title
        title_label = QLabel("Control Panel")
        title_font = QFont()
        title_font.setPointSize(22)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setStyleSheet("color: #212121; background: transparent;")
        layout.addWidget(title_label)
        
        # Two-column layout for Distributors and Parties
        top_row_layout = QHBoxLayout()
        top_row_layout.setSpacing(20)
        top_row_layout.addWidget(self.distributors_panel)
        top_row_layout.addWidget(self.parties_panel)
        layout.addLayout(top_row_layout)
        
        # Add remaining sections below
        layout.addWidget(self.products_panel)
        layout.addWidget(self.settings_panel)
        
        layout.addStretch()
        
        scroll_area.setWidget(container)
        return scroll_area
    
    def show_purchase(self):
        """Show purchase window and refresh data."""
        self.purchase_window.refresh_data()
        self.stacked_widget.setCurrentWidget(self.purchase_window)
    
    def show_sale(self):
        """Show sale window and refresh data."""
        self.sale_window.refresh_data()
        self.stacked_widget.setCurrentWidget(self.sale_window)
    
    def show_stock(self):
        """Show stock window and refresh data."""
        self.stock_window.refresh_data()
        self.stacked_widget.setCurrentWidget(self.stock_window)
    
    def show_reports(self):
        """Show reports window."""
        self.stacked_widget.setCurrentWidget(self.reports_window)
    
    def show_about(self):
        """Show about dialog."""
        QMessageBox.about(
            self,
            "About alLot",
            "alLot - Inventory Management & Billing\n\n"
            "Version 1.0\n\n"
            "A comprehensive solution for managing inventory, "
            "purchases, sales, and generating reports."
        )
