"""Main dashboard window for alLot application."""
from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                               QPushButton, QLabel, QFrame, QMessageBox, QStackedWidget)
from PySide6.QtCore import Qt, QTimer, QDateTime
from PySide6.QtGui import QFont, QAction
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
        
        # Content area with stacked widget
        self.stacked_widget = QStackedWidget()
        
        # Dashboard home
        dashboard_home = self.create_dashboard_home()
        self.stacked_widget.addWidget(dashboard_home)
        
        # Add control panel screens
        self.distributors_panel = DistributorsPanel()
        self.parties_panel = PartiesPanel()
        self.products_panel = ProductsPanel()
        self.settings_panel = SettingsPanel()
        
        self.stacked_widget.addWidget(self.distributors_panel)
        self.stacked_widget.addWidget(self.parties_panel)
        self.stacked_widget.addWidget(self.products_panel)
        self.stacked_widget.addWidget(self.settings_panel)
        
        # Add transaction screens
        self.purchase_window = PurchaseWindow()
        self.sale_window = SaleWindow()
        self.stock_window = StockWindow()
        self.reports_window = ReportsWindow()
        
        self.stacked_widget.addWidget(self.purchase_window)
        self.stacked_widget.addWidget(self.sale_window)
        self.stacked_widget.addWidget(self.stock_window)
        self.stacked_widget.addWidget(self.reports_window)
        
        main_layout.addWidget(self.stacked_widget)
        
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
    
    def create_dashboard_home(self):
        """Create dashboard home screen."""
        home_widget = QWidget()
        layout = QVBoxLayout(home_widget)
        layout.setSpacing(30)
        layout.setContentsMargins(50, 50, 50, 50)
        
        # Welcome message
        welcome_label = QLabel("Welcome to alLot")
        welcome_font = QFont()
        welcome_font.setPointSize(20)
        welcome_font.setBold(True)
        welcome_label.setFont(welcome_font)
        layout.addWidget(welcome_label)
        
        # Quick access buttons grid
        buttons_layout = QVBoxLayout()
        buttons_layout.setSpacing(20)
        
        # Row 1: Control Panel
        row1 = QHBoxLayout()
        row1.setSpacing(20)
        
        btn_distributors = self.create_dashboard_button("Distributors", "Manage distributors and purchase rates")
        btn_distributors.clicked.connect(lambda: self.stacked_widget.setCurrentWidget(self.distributors_panel))
        row1.addWidget(btn_distributors)
        
        btn_parties = self.create_dashboard_button("Parties", "Manage parties and sale rates")
        btn_parties.clicked.connect(lambda: self.stacked_widget.setCurrentWidget(self.parties_panel))
        row1.addWidget(btn_parties)
        
        btn_products = self.create_dashboard_button("Products", "Manage product catalog")
        btn_products.clicked.connect(lambda: self.stacked_widget.setCurrentWidget(self.products_panel))
        row1.addWidget(btn_products)
        
        buttons_layout.addLayout(row1)
        
        # Row 2: Transactions
        row2 = QHBoxLayout()
        row2.setSpacing(20)
        
        btn_purchase = self.create_dashboard_button("Purchase", "Record purchase transactions", "#4CAF50")
        btn_purchase.clicked.connect(self.show_purchase)
        row2.addWidget(btn_purchase)
        
        btn_sale = self.create_dashboard_button("Sale", "Record sale transactions", "#FF9800")
        btn_sale.clicked.connect(self.show_sale)
        row2.addWidget(btn_sale)
        
        btn_stock = self.create_dashboard_button("Stock", "View current stock levels")
        btn_stock.clicked.connect(self.show_stock)
        row2.addWidget(btn_stock)
        
        buttons_layout.addLayout(row2)
        
        # Row 3: Reports
        row3 = QHBoxLayout()
        row3.setSpacing(20)
        
        btn_reports = self.create_dashboard_button("Reports", "Generate and view reports", "#9C27B0")
        btn_reports.clicked.connect(self.show_reports)
        row3.addWidget(btn_reports)
        
        btn_settings = self.create_dashboard_button("Settings", "Application settings")
        btn_settings.clicked.connect(lambda: self.stacked_widget.setCurrentWidget(self.settings_panel))
        row3.addWidget(btn_settings)
        
        # Empty placeholder
        row3.addWidget(QWidget())
        
        buttons_layout.addLayout(row3)
        
        layout.addLayout(buttons_layout)
        layout.addStretch()
        
        return home_widget
    
    def create_dashboard_button(self, title, description, color="#2196F3"):
        """Create a styled dashboard button."""
        button = QPushButton()
        button_layout = QVBoxLayout(button)
        button_layout.setSpacing(10)
        
        title_label = QLabel(title)
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        button_layout.addWidget(title_label)
        
        desc_label = QLabel(description)
        desc_label.setWordWrap(True)
        desc_label.setAlignment(Qt.AlignCenter)
        button_layout.addWidget(desc_label)
        
        button.setFixedHeight(120)
        button.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: white;
                border: none;
                border-radius: 8px;
                padding: 20px;
            }}
            QPushButton:hover {{
                opacity: 0.9;
                background-color: {color};
                filter: brightness(110%);
            }}
            QPushButton:pressed {{
                background-color: {color};
                filter: brightness(90%);
            }}
        """)
        
        return button
    
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
