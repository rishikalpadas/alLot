"""Purchase window for recording purchases."""
from datetime import datetime
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
                               QComboBox, QTableWidget, QTableWidgetItem, QDateEdit,
                               QLineEdit, QTextEdit, QMessageBox, QDoubleSpinBox, QHeaderView)
from PySide6.QtCore import Qt, QDate
from database.models import Distributor, Product
from database.db_manager import db_manager
from services.pricing_service import PricingService
from services.inventory_service import InventoryService


class PurchaseWindow(QWidget):
    """Window for recording purchase transactions."""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        title = QLabel("Purchase")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(title)
        
        # Header form
        header_layout = QHBoxLayout()
        
        # Distributor
        dist_layout = QVBoxLayout()
        dist_label = QLabel("Distributor*:")
        self.distributor_combo = QComboBox()
        self.distributor_combo.currentIndexChanged.connect(self.on_distributor_changed)
        dist_layout.addWidget(dist_label)
        dist_layout.addWidget(self.distributor_combo)
        header_layout.addLayout(dist_layout)
        
        # Date
        date_layout = QVBoxLayout()
        date_label = QLabel("Date*:")
        self.date_edit = QDateEdit()
        self.date_edit.setDate(QDate.currentDate())
        self.date_edit.setCalendarPopup(True)
        date_layout.addWidget(date_label)
        date_layout.addWidget(self.date_edit)
        header_layout.addLayout(date_layout)
        
        # Invoice
        invoice_layout = QVBoxLayout()
        invoice_label = QLabel("Invoice Number:")
        self.invoice_input = QLineEdit()
        invoice_layout.addWidget(invoice_label)
        invoice_layout.addWidget(self.invoice_input)
        header_layout.addLayout(invoice_layout)
        
        layout.addLayout(header_layout)
        
        # Items section
        items_label = QLabel("Items:")
        items_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(items_label)
        
        # Add item row
        add_item_layout = QHBoxLayout()
        
        self.product_combo = QComboBox()
        self.product_combo.currentIndexChanged.connect(self.on_product_selected)
        add_item_layout.addWidget(QLabel("Product:"))
        add_item_layout.addWidget(self.product_combo, 2)
        
        self.quantity_spin = QDoubleSpinBox()
        self.quantity_spin.setRange(0.01, 999999)
        self.quantity_spin.setDecimals(2)
        self.quantity_spin.valueChanged.connect(self.calculate_amount)
        add_item_layout.addWidget(QLabel("Quantity:"))
        add_item_layout.addWidget(self.quantity_spin, 1)
        
        self.rate_spin = QDoubleSpinBox()
        self.rate_spin.setRange(0.01, 999999)
        self.rate_spin.setDecimals(2)
        self.rate_spin.setPrefix("₹ ")
        self.rate_spin.valueChanged.connect(self.calculate_amount)
        add_item_layout.addWidget(QLabel("Rate:"))
        add_item_layout.addWidget(self.rate_spin, 1)
        
        self.amount_label = QLabel("₹ 0.00")
        self.amount_label.setStyleSheet("font-weight: bold;")
        add_item_layout.addWidget(QLabel("Amount:"))
        add_item_layout.addWidget(self.amount_label, 1)
        
        add_btn = QPushButton("Add Item")
        add_btn.clicked.connect(self.add_item)
        add_item_layout.addWidget(add_btn)
        
        layout.addLayout(add_item_layout)
        
        # Items table
        self.items_table = QTableWidget()
        self.items_table.setColumnCount(6)
        self.items_table.setHorizontalHeaderLabels(["Product ID", "Product", "Quantity", "Rate", "Amount", ""])
        self.items_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.items_table.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self.items_table)
        
        # Total
        total_layout = QHBoxLayout()
        total_layout.addStretch()
        total_layout.addWidget(QLabel("Total Amount:"))
        self.total_label = QLabel("₹ 0.00")
        self.total_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #2196F3;")
        total_layout.addWidget(self.total_label)
        layout.addLayout(total_layout)
        
        # Notes
        notes_label = QLabel("Notes:")
        layout.addWidget(notes_label)
        self.notes_input = QTextEdit()
        self.notes_input.setMaximumHeight(60)
        layout.addWidget(self.notes_input)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        clear_btn = QPushButton("Clear")
        clear_btn.clicked.connect(self.clear_form)
        button_layout.addWidget(clear_btn)
        
        save_btn = QPushButton("Save Purchase")
        save_btn.setStyleSheet("background-color: #4CAF50; color: white; padding: 8px 16px;")
        save_btn.clicked.connect(self.save_purchase)
        button_layout.addWidget(save_btn)
        
        layout.addLayout(button_layout)
    
    def refresh_data(self):
        """Refresh distributors and products."""
        session = db_manager.get_session()
        try:
            # Load distributors
            self.distributor_combo.clear()
            distributors = session.query(Distributor).all()
            for dist in distributors:
                self.distributor_combo.addItem(dist.name, dist.id)
            
            # Load products
            self.product_combo.clear()
            products = session.query(Product).all()
            for product in products:
                self.product_combo.addItem(f"{product.name} ({product.sku})", product.id)
        finally:
            session.close()
    
    def on_distributor_changed(self):
        """Handle distributor selection change."""
        self.rate_spin.setValue(0)
    
    def on_product_selected(self):
        """Auto-populate rate based on distributor and product."""
        if self.distributor_combo.currentData() and self.product_combo.currentData():
            rate = PricingService.get_purchase_rate(
                self.distributor_combo.currentData(),
                self.product_combo.currentData()
            )
            if rate:
                self.rate_spin.setValue(rate)
    
    def calculate_amount(self):
        """Calculate amount based on quantity and rate."""
        amount = self.quantity_spin.value() * self.rate_spin.value()
        self.amount_label.setText(f"₹ {amount:,.2f}")
    
    def add_item(self):
        """Add item to table."""
        if not self.product_combo.currentData():
            QMessageBox.warning(self, "Validation Error", "Please select a product.")
            return
        
        if self.quantity_spin.value() <= 0:
            QMessageBox.warning(self, "Validation Error", "Quantity must be greater than 0.")
            return
        
        if self.rate_spin.value() <= 0:
            QMessageBox.warning(self, "Validation Error", "Rate must be greater than 0.")
            return
        
        row = self.items_table.rowCount()
        self.items_table.insertRow(row)
        
        product_id = self.product_combo.currentData()
        product_name = self.product_combo.currentText()
        quantity = self.quantity_spin.value()
        rate = self.rate_spin.value()
        amount = quantity * rate
        
        self.items_table.setItem(row, 0, QTableWidgetItem(str(product_id)))
        self.items_table.setItem(row, 1, QTableWidgetItem(product_name))
        self.items_table.setItem(row, 2, QTableWidgetItem(f"{quantity:.2f}"))
        self.items_table.setItem(row, 3, QTableWidgetItem(f"₹ {rate:.2f}"))
        self.items_table.setItem(row, 4, QTableWidgetItem(f"₹ {amount:.2f}"))
        
        # Remove button
        remove_btn = QPushButton("Remove")
        remove_btn.clicked.connect(lambda: self.remove_item(row))
        self.items_table.setCellWidget(row, 5, remove_btn)
        
        self.update_total()
        
        # Reset inputs
        self.quantity_spin.setValue(1)
        self.rate_spin.setValue(0)
    
    def remove_item(self, row):
        """Remove item from table."""
        self.items_table.removeRow(row)
        self.update_total()
    
    def update_total(self):
        """Update total amount."""
        total = 0
        for row in range(self.items_table.rowCount()):
            amount_text = self.items_table.item(row, 4).text()
            amount = float(amount_text.replace("₹", "").replace(",", "").strip())
            total += amount
        
        self.total_label.setText(f"₹ {total:,.2f}")
    
    def save_purchase(self):
        """Save purchase transaction."""
        if not self.distributor_combo.currentData():
            QMessageBox.warning(self, "Validation Error", "Please select a distributor.")
            return
        
        if self.items_table.rowCount() == 0:
            QMessageBox.warning(self, "Validation Error", "Please add at least one item.")
            return
        
        # Collect items
        items = []
        for row in range(self.items_table.rowCount()):
            product_id = int(self.items_table.item(row, 0).text())
            quantity = float(self.items_table.item(row, 2).text())
            rate_text = self.items_table.item(row, 3).text()
            rate = float(rate_text.replace("₹", "").replace(",", "").strip())
            
            items.append({
                'product_id': product_id,
                'quantity': quantity,
                'rate': rate
            })
        
        # Save purchase
        distributor_id = self.distributor_combo.currentData()
        purchase_date = self.date_edit.date().toPython()
        invoice_number = self.invoice_input.text().strip() or None
        notes = self.notes_input.toPlainText().strip() or None
        
        success, message, purchase_id = InventoryService.create_purchase(
            distributor_id, purchase_date, items, invoice_number, notes
        )
        
        if success:
            QMessageBox.information(self, "Success", f"Purchase saved successfully!\n{message}")
            self.clear_form()
        else:
            QMessageBox.critical(self, "Error", message)
    
    def clear_form(self):
        """Clear form."""
        self.date_edit.setDate(QDate.currentDate())
        self.invoice_input.clear()
        self.notes_input.clear()
        self.items_table.setRowCount(0)
        self.quantity_spin.setValue(1)
        self.rate_spin.setValue(0)
        self.update_total()
