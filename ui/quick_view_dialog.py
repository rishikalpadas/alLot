"""Quick View Dialog for accessing other screens in a popup."""
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QComboBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QShortcut, QKeySequence


class QuickViewDialog(QDialog):
    """Dialog for quick access to other screens."""
    
    def __init__(self, parent=None, current_screen=None):
        super().__init__(parent)
        self.current_screen = current_screen
        self.current_widget = None
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("Quick View")
        self.setModal(False)  # Non-modal so you can interact with parent
        self.resize(1200, 700)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Header with screen selector
        header_layout = QHBoxLayout()
        header_layout.setSpacing(10)
        
        screen_label = QLabel("View:")
        screen_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        header_layout.addWidget(screen_label)
        
        self.screen_combo = QComboBox()
        self.screen_combo.setMinimumWidth(200)
        self.screen_combo.setMinimumHeight(35)
        self.screen_combo.setStyleSheet("font-size: 13px; padding: 5px;")
        
        # Add available screens (exclude current screen)
        screens = [
            ("Purchase", "purchase"),
            ("Sale", "sale"),
            ("Stock", "stock")
        ]
        
        for name, key in screens:
            if key != self.current_screen:
                self.screen_combo.addItem(name, key)
        
        self.screen_combo.currentIndexChanged.connect(self.on_screen_changed)
        header_layout.addWidget(self.screen_combo)
        
        header_layout.addStretch()
        
        close_btn = QPushButton("Close (Esc)")
        close_btn.setStyleSheet("padding: 8px 16px;")
        close_btn.clicked.connect(self.close)
        header_layout.addWidget(close_btn)
        
        layout.addLayout(header_layout)
        
        # Container for the screen widget
        self.screen_container = QVBoxLayout()
        layout.addLayout(self.screen_container)
        
        # Load initial screen
        if self.screen_combo.count() > 0:
            self.on_screen_changed(0)
        
        # Esc to close
        esc_shortcut = QShortcut(QKeySequence("Esc"), self)
        esc_shortcut.activated.connect(self.close)
        
    def on_screen_changed(self, index):
        """Load the selected screen."""
        # Remove current widget if any
        if self.current_widget:
            self.screen_container.removeWidget(self.current_widget)
            self.current_widget.deleteLater()
            self.current_widget = None
        
        screen_key = self.screen_combo.currentData()
        if not screen_key:
            return
        
        # Import and create the appropriate screen
        if screen_key == "purchase":
            from ui.purchase_window import PurchaseWindow
            self.current_widget = PurchaseWindow()
        elif screen_key == "sale":
            from ui.sale_window import SaleWindow
            self.current_widget = SaleWindow()
        elif screen_key == "stock":
            from ui.stock_window import StockWindow
            self.current_widget = StockWindow()
        
        if self.current_widget:
            self.screen_container.addWidget(self.current_widget)
            # Refresh data for the screen
            if hasattr(self.current_widget, 'refresh_data'):
                self.current_widget.refresh_data()
    
    def closeEvent(self, event):
        """Clean up when dialog is closed."""
        if self.current_widget:
            self.current_widget.deleteLater()
        super().closeEvent(event)
