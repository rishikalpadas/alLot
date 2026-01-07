"""Stock view window."""
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
                               QTableWidget, QTableWidgetItem, QHeaderView)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from services.inventory_service import InventoryService


class StockWindow(QWidget):
    """Window for viewing current stock levels."""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        title = QLabel("Current Stock")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(title)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self.refresh_data)
        button_layout.addWidget(refresh_btn)
        
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["SKU", "Product Name", "Unit", "Current Stock", "Status"])
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self.table)
    
    def refresh_data(self):
        """Load current stock data."""
        stock_data = InventoryService.get_current_stock()
        
        self.table.setRowCount(len(stock_data))
        
        for row, (product, quantity) in enumerate(stock_data):
            self.table.setItem(row, 0, QTableWidgetItem(product.sku))
            self.table.setItem(row, 1, QTableWidgetItem(product.name))
            self.table.setItem(row, 2, QTableWidgetItem(product.unit))
            
            qty_item = QTableWidgetItem(f"{quantity:.2f}")
            qty_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, 3, qty_item)
            
            # Status
            if quantity <= 0:
                status = "Out of Stock"
                color = "#F44336"
            elif quantity <= product.reorder_level:
                status = "Low Stock"
                color = "#FF9800"
            else:
                status = "In Stock"
                color = "#4CAF50"
            
            status_item = QTableWidgetItem(status)
            status_item.setTextAlignment(Qt.AlignCenter)
            status_item.setForeground(QColor(color))
            self.table.setItem(row, 4, status_item)
