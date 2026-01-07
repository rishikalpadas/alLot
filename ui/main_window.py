"""Main dashboard window for alLot application."""
from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                               QPushButton, QLabel, QFrame, QMessageBox, QStackedWidget, QTableWidget, QApplication)
from PySide6.QtCore import Qt, QTimer, QDateTime, QEvent
from PySide6.QtGui import QFont, QAction, QKeyEvent
from ui.dashboard_home import DashboardHome
from ui.control_panel.distributors import DistributorsPanel
from ui.control_panel.parties import PartiesPanel
from ui.control_panel.products import TicketsPanel
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
        self.products_panel = TicketsPanel()
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
        
        # Install global application-level event filter for Escape key and shortcuts
        # This catches all key events even if no widget has focus
        QApplication.instance().installEventFilter(self)
        
        self.showMaximized()
    
    def check_unsaved_before_switch(self):
        """Check for unsaved entries in purchase/sale windows before switching screens."""
        current_widget = self.stacked_widget.currentWidget()
        
        # Check if current screen is purchase or sale with unsaved entries
        if current_widget == self.purchase_window and self.purchase_window.has_unsaved_entries():
            reply = QMessageBox.question(
                self,
                "Unsaved Entries",
                "You have unsaved purchase entries. Do you want to save them?",
                QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel,
                QMessageBox.Cancel
            )
            if reply == QMessageBox.Yes:
                self.purchase_window.save_purchase()
                return True
            elif reply == QMessageBox.Cancel:
                return False
        
        elif current_widget == self.sale_window and self.sale_window.has_unsaved_entries():
            reply = QMessageBox.question(
                self,
                "Unsaved Entries",
                "You have unsaved sale entries. Do you want to save them?",
                QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel,
                QMessageBox.Cancel
            )
            if reply == QMessageBox.Yes:
                self.sale_window.save_sale()
                return True
            elif reply == QMessageBox.Cancel:
                return False
        
        return True
    
    def keyPressEvent(self, event: QKeyEvent):
        """Handle global keyboard shortcuts."""
        if event.key() == Qt.Key_F1:
            self.stacked_widget.setCurrentWidget(self.dashboard_home)
            event.accept()
        elif event.key() == Qt.Key_F2:
            self.show_purchase()
            event.accept()
        elif event.key() == Qt.Key_F3:
            self.show_sale()
            event.accept()
        elif event.key() == Qt.Key_F4:
            self.show_stock()
            event.accept()
        elif event.key() == Qt.Key_F5:
            self.stacked_widget.setCurrentWidget(self.control_panel_home)
            event.accept()
        else:
            super().keyPressEvent(event)
    
    def create_menu_bar(self):
        """Create menu bar."""
        menubar = self.menuBar()
        
        # Control Panel menu
        control_menu = menubar.addMenu("Control Panel")
        
        distributors_action = QAction("Distributors", self)
        distributors_action.triggered.connect(lambda: self.navigate_to_panel(self.distributors_panel))
        control_menu.addAction(distributors_action)
        
        parties_action = QAction("Parties", self)
        parties_action.triggered.connect(lambda: self.navigate_to_panel(self.parties_panel))
        control_menu.addAction(parties_action)
        
        products_action = QAction("Products", self)
        products_action.triggered.connect(lambda: self.navigate_to_panel(self.products_panel))
        control_menu.addAction(products_action)
        
        control_menu.addSeparator()
        
        settings_action = QAction("Settings", self)
        settings_action.triggered.connect(lambda: self.navigate_to_panel(self.settings_panel))
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
        btn_dashboard = self.create_sidebar_button("Dashboard (F1)")
        btn_dashboard.clicked.connect(lambda: self.stacked_widget.setCurrentWidget(self.dashboard_home))
        sidebar_layout.addWidget(btn_dashboard)
        
        # Purchase
        btn_purchase = self.create_sidebar_button("Purchase (F2)")
        btn_purchase.clicked.connect(self.show_purchase)
        sidebar_layout.addWidget(btn_purchase)
        
        # Sale
        btn_sale = self.create_sidebar_button("Sale (F3)")
        btn_sale.clicked.connect(self.show_sale)
        sidebar_layout.addWidget(btn_sale)
        
        # View Stock
        btn_stock = self.create_sidebar_button("View Stock (F4)")
        btn_stock.clicked.connect(self.show_stock)
        sidebar_layout.addWidget(btn_stock)
        
        # Control Panel
        btn_control_panel = self.create_sidebar_button("Control Panel (F5)")
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
    
    def navigate_to_panel(self, panel):
        """Navigate to a panel after checking for unsaved entries."""
        if not self.check_unsaved_before_switch():
            return
        self.stacked_widget.setCurrentWidget(panel)
    
    def show_purchase(self):
        """Show purchase window and refresh data."""
        if not self.check_unsaved_before_switch():
            return
        self.purchase_window.refresh_data()
        self.stacked_widget.setCurrentWidget(self.purchase_window)
    
    def show_sale(self):
        """Show sale window and refresh data."""
        if not self.check_unsaved_before_switch():
            return
        self.sale_window.refresh_data()
        self.stacked_widget.setCurrentWidget(self.sale_window)
    
    def show_stock(self):
        """Show stock window and refresh data."""
        if not self.check_unsaved_before_switch():
            return
        self.stock_window.refresh_data()
        self.stacked_widget.setCurrentWidget(self.stock_window)
    
    def show_reports(self):
        """Show reports window."""
        if not self.check_unsaved_before_switch():
            return
        self.stacked_widget.setCurrentWidget(self.reports_window)
    
    def eventFilter(self, obj, event):
        """Global event filter to handle Escape key and mouse clicks for clearing selections."""
        # Handle Escape key globally - prioritize removing new rows
        if event.type() == QEvent.Type.KeyPress:
            key_event = QKeyEvent(event)
            if key_event.key() == Qt.Key_Escape:
                # First, try to remove any new rows being edited
                for panel in [self.distributors_panel, self.parties_panel, self.products_panel]:
                    if hasattr(panel, 'table') and hasattr(panel, 'removing_row'):
                        # Check if there's a new row being edited
                        for row in range(panel.table.rowCount()):
                            serial_item = panel.table.item(row, 0)
                            if serial_item and serial_item.text() == "*":
                                # Remove the new row
                                if not panel.removing_row:
                                    panel.removing_row = True
                                    panel.table.closePersistentEditor(panel.table.currentItem())
                                    panel.table.removeRow(row)
                                    panel.removing_row = False
                                    return True
                
                # If no new row found, clear all selections
                for panel in [self.distributors_panel, self.parties_panel, self.products_panel]:
                    if hasattr(panel, 'table') and panel.table.selectedItems():
                        panel.table.clearSelection()
                return True
        
        # Handle mouse clicks outside tables
        if event.type() == QEvent.Type.MouseButtonPress:
            # Get the widget under the mouse
            widget = self.childAt(event.pos())
            # Check all panels for new rows and selections
            for panel in [self.distributors_panel, self.parties_panel, self.products_panel]:
                if hasattr(panel, 'table') and hasattr(panel, 'removing_row'):
                    # Check if there's a new row being edited
                    has_new_row = False
                    new_row_index = -1
                    for row in range(panel.table.rowCount()):
                        serial_item = panel.table.item(row, 0)
                        if serial_item and serial_item.text() == "*":
                            has_new_row = True
                            new_row_index = row
                            break
                    
                    # If there's a new row and click is outside the table, remove it
                    if has_new_row and not self._is_click_in_table(widget, panel.table):
                        if not panel.removing_row:
                            panel.removing_row = True
                            panel.table.closePersistentEditor(panel.table.currentItem())
                            panel.table.removeRow(new_row_index)
                            panel.removing_row = False
                    # If no new row, clear selection if clicking outside table
                    elif panel.table.selectedItems() and not self._is_click_in_table(widget, panel.table):
                        if not self._is_click_in_table(widget, panel):
                            panel.table.clearSelection()
        
        return super().eventFilter(obj, event)
    
    def _is_click_in_table(self, widget, table):
        """Check if a widget is the table or a child of the table."""
        if widget is None:
            return False
        if widget == table:
            return True
        # Check if widget is a child of table
        parent = widget.parent()
        while parent is not None:
            if parent == table:
                return True
            parent = parent.parent()
        return False
    
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
