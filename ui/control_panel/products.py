"""Tickets management panel."""
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                               QTableWidget, QTableWidgetItem, QDialog, QFormLayout,
                               QLineEdit, QLabel, QMessageBox, QHeaderView)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QIcon, QKeyEvent
import qtawesome as qta
import re
from database.models import Product
from database.db_manager import db_manager


class ProductsPanel(QWidget):
    """Panel for managing tickets."""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.load_products()
    
    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(30, 30, 30, 30)
        
        title = QLabel("Tickets Management")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        main_layout.addWidget(title)
        
        # Horizontal layout for table and options side by side
        content_layout = QHBoxLayout()
        content_layout.setSpacing(30)
        
        # Left side - Table section
        table_container = QWidget()
        table_layout = QVBoxLayout(table_container)
        table_layout.setContentsMargins(0, 0, 0, 0)
        table_layout.setSpacing(15)
        
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        add_btn = QPushButton(" Add Ticket")
        add_btn.setIcon(qta.icon('fa5s.plus', color='white'))
        add_btn.clicked.connect(self.add_product)
        add_btn.setCursor(Qt.PointingHandCursor)
        add_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: 500;
                text-align: left;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
        """)
        button_layout.addWidget(add_btn)
        
        edit_btn = QPushButton(" Edit")
        edit_btn.setIcon(qta.icon('fa5s.edit', color='white'))
        edit_btn.clicked.connect(self.edit_product)
        edit_btn.setCursor(Qt.PointingHandCursor)
        edit_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: 500;
                text-align: left;
            }
            QPushButton:hover {
                background-color: #0b7dda;
            }
            QPushButton:pressed {
                background-color: #0a6ebd;
            }
        """)
        button_layout.addWidget(edit_btn)
        
        delete_btn = QPushButton(" Delete")
        delete_btn.setIcon(qta.icon('fa5s.trash-alt', color='white'))
        delete_btn.clicked.connect(self.delete_product)
        delete_btn.setCursor(Qt.PointingHandCursor)
        delete_btn.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: 500;
                text-align: left;
            }
            QPushButton:hover {
                background-color: #da190b;
            }
            QPushButton:pressed {
                background-color: #b71c1c;
            }
        """)
        button_layout.addWidget(delete_btn)
        
        button_layout.addStretch()
        table_layout.addLayout(button_layout)
        
        self.table = QTableWidget()
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["#", "Name"])
        
        # Hide row numbers
        self.table.verticalHeader().setVisible(False)
        
        # Set column widths
        self.table.setColumnWidth(0, 50)   # # column
        self.table.setColumnWidth(1, 150)  # Name column - fixed width
        
        # Set fixed table width
        self.table.setFixedWidth(540)
        
        # Disable horizontal scrollbar and column resizing
        self.table.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Fixed)
        header.setSectionResizeMode(1, QHeaderView.Stretch)  # Last column stretches
        
        # Connect itemChanged for inline editing workflow
        self.table.itemChanged.connect(self.on_item_changed)
        self.table.itemSelectionChanged.connect(self.on_selection_changed)
        
        # Install event filter to catch Escape key before editor consumes it
        self.table.installEventFilter(self)
        
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.ExtendedSelection)  # Enable Ctrl+click multi-select
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.setFixedHeight(240)  # Fixed height for ~5 rows + header
        
        # Set row height for better visibility during editing
        self.table.verticalHeader().setDefaultSectionSize(38)
        
        self.table.setStyleSheet("""
            QTableWidget {
                gridline-color: #E8E8E8;
                background-color: white;
                border: 1px solid #E0E0E0;
                border-radius: 6px;
            }
            QTableWidget::item {
                padding: 10px 8px;
                border-bottom: 1px solid #F0F0F0;
            }
            QTableWidget::item:selected {
                background-color: #E3F2FD;
                color: #1976D2;
            }
            QTableWidget::item:hover {
                background-color: #F5F5F5;
            }
            QHeaderView::section {
                background-color: #FAFAFA;
                padding: 10px 8px;
                border: none;
                border-bottom: 2px solid #2196F3;
                border-right: 1px solid #E8E8E8;
                font-weight: 600;
                color: #424242;
            }
            QHeaderView::section:first {
                border-top-left-radius: 6px;
            }
            QHeaderView::section:last {
                border-top-right-radius: 6px;
                border-right: none;
            }
            QHeaderView::section:hover {
                background-color: #F0F0F0;
                cursor: pointer;
            }
            /* Modern Scrollbar */
            QScrollBar:vertical {
                border: none;
                background: #F5F5F5;
                width: 10px;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical {
                background: #BDBDBD;
                border-radius: 5px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background: #9E9E9E;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: none;
            }
        """)
        
        table_layout.addWidget(self.table)
        
        # Add table container to content layout
        content_layout.addWidget(table_container)
        
        # Right side - Options section
        options_container = QWidget()
        options_layout = QVBoxLayout(options_container)
        options_layout.setContentsMargins(0, 0, 0, 0)
        options_layout.setSpacing(15)
        
        # Placeholder for future options
        options_title = QLabel("Quick Actions")
        options_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #424242;")
        options_layout.addWidget(options_title)
        
        # Placeholder text
        placeholder = QLabel("Additional options will be\nadded here")
        placeholder.setStyleSheet("""
            color: #999;
            font-size: 13px;
            padding: 20px;
            border: 2px dashed #E0E0E0;
            border-radius: 6px;
            background-color: #FAFAFA;
        """)
        placeholder.setAlignment(Qt.AlignCenter)
        placeholder.setMinimumHeight(200)
        options_layout.addWidget(placeholder)
        
        options_layout.addStretch()
        
        content_layout.addWidget(options_container)
        content_layout.addStretch()
        
        main_layout.addLayout(content_layout)
    
    def load_products(self):
        session = db_manager.get_session()
        try:
            products = session.query(Product).order_by(Product.id).all()
            self.table.setRowCount(len(products))
            
            for row, product in enumerate(products):
                # Serial number - center aligned
                serial_item = QTableWidgetItem(str(row + 1))
                serial_item.setTextAlignment(Qt.AlignCenter)
                serial_item.setFlags(serial_item.flags() & ~Qt.ItemIsEditable)
                self.table.setItem(row, 0, serial_item)
                
                # Name - center aligned
                name_item = QTableWidgetItem(product.name)
                name_item.setTextAlignment(Qt.AlignCenter)
                name_item.setFlags(name_item.flags() & ~Qt.ItemIsEditable)
                name_item.setData(Qt.UserRole, product.id)
                self.table.setItem(row, 1, name_item)
        finally:
            session.close()
    
    def save_new_row(self, row):
        """Save the new ticket row to database."""
        name_item = self.table.item(row, 1)
        
        if not name_item:
            return False
            
        name = name_item.text().strip().upper()
        
        if not name:
            QMessageBox.warning(self, "Validation Error", "Name is required.")
            return False
        
        # Validate format: capital letters followed by numbers
        if not re.match(r'^[A-Z]+\d+$', name):
            QMessageBox.warning(
                self, 
                "Validation Error", 
                "Name must be in format: Capital letters + numbers\n(e.g., M5, D30, E200, E100)"
            )
            return False
        
        session = db_manager.get_session()
        try:
            # Create new ticket
            product = Product(
                sku=name,
                name=name,
                unit="pcs",
                hsn_code=None,
                tax_rate=0.0,
                description=None
            )
            session.add(product)
            session.commit()
            
            # Reload the table
            self.load_products()
            
            # Add another new row for quick entry
            self.add_product()
            
            return True
        except Exception as e:
            session.rollback()
            QMessageBox.critical(self, "Error", f"Error saving ticket: {str(e)}")
            return False
        finally:
            session.close()
    
    def on_item_changed(self, item):
        """Handle item changes for inline editing workflow."""
        row = item.row()
        col = item.column()
        
        # Check if this is a new row (serial = "*")
        serial_item = self.table.item(row, 1)
        if not serial_item or serial_item.text() != "*":
            return
        
        # If name field was edited, save immediately
        if col == 2 and item.text().strip():
            self.save_new_row(row)
    
    def cancel_new_row(self):
        """Cancel and remove the new row being edited."""
        for row in range(self.table.rowCount()):
            serial_item = self.table.item(row, 0)
            if serial_item and serial_item.text() == "*":
                self.table.removeRow(row)
                return True
        return False
    
    def on_selection_changed(self):
        """Cancel new row when clicking elsewhere."""
        current_row = self.table.currentRow()
        if current_row < 0:
            return
        
        # Check if there's a new row being edited
        for row in range(self.table.rowCount()):
            serial_item = self.table.item(row, 0)
            if serial_item and serial_item.text() == "*":
                # If clicking on a different row, cancel the new row
                if row != current_row:
                    # Temporarily disconnect to avoid recursion
                    self.table.itemSelectionChanged.disconnect(self.on_selection_changed)
                    self.table.removeRow(row)
                    self.table.itemSelectionChanged.connect(self.on_selection_changed)
                return
    
    def eventFilter(self, obj, event):
        """Event filter to catch Escape key before editor consumes it."""
        if obj == self.table and event.type() == event.Type.KeyPress:
            if event.key() == Qt.Key_Escape:
                if self.cancel_new_row():
                    return True  # Event handled
        return super().eventFilter(obj, event)
    
    def add_product(self):
        """Add new ticket with inline editing."""
        # Add new editable row at the bottom
        row = self.table.rowCount()
        self.table.insertRow(row)
        
        # Serial number
        serial_item = QTableWidgetItem("*")
        serial_item.setTextAlignment(Qt.AlignCenter)
        serial_item.setFlags(serial_item.flags() & ~Qt.ItemIsEditable)
        serial_item.setBackground(Qt.lightGray)
        self.table.setItem(row, 0, serial_item)
        
        # Name - editable
        name_item = QTableWidgetItem("")
        name_item.setTextAlignment(Qt.AlignCenter)
        name_item.setBackground(Qt.yellow)
        self.table.setItem(row, 1, name_item)
        
        # Scroll to bottom and set focus on name field
        self.table.scrollToBottom()
        self.table.setCurrentCell(row, 1)
        self.table.editItem(name_item)
    
    def edit_product(self):
        selected_rows = self.table.selectedIndexes()
        if not selected_rows:
            QMessageBox.warning(self, "No Selection", "Please select a ticket to edit.")
            return
        
        # Get product_id from name item's UserRole data
        row = selected_rows[0].row()
        name_item = self.table.item(row, 1)
        product_id = name_item.data(Qt.UserRole)
        dialog = ProductDialog(self, product_id)
        if dialog.exec():
            self.load_products()
    
    def delete_product(self):
        """Delete selected ticket(s)."""
        # Collect selected products
        selected_rows = self.table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "No Selection", "Please select at least one ticket to delete.")
            return
        
        selected_ids = []
        for index in selected_rows:
            row = index.row()
            name_item = self.table.item(row, 1)
            product_id = name_item.data(Qt.UserRole)
            if product_id:
                selected_ids.append(product_id)
        
        if not selected_ids:
            QMessageBox.warning(self, "No Selection", "Please select at least one ticket to delete.")
            return
        
        count = len(selected_ids)
        reply = QMessageBox.question(
            self, "Confirm Delete",
            f"Are you sure you want to delete {count} ticket(s)?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            session = db_manager.get_session()
            try:
                for product_id in selected_ids:
                    product = session.query(Product).get(product_id)
                    if product:
                        session.delete(product)
                session.commit()
                self.load_products()
                QMessageBox.information(self, "Success", f"{count} ticket(s) deleted successfully.")
            except Exception as e:
                session.rollback()
                QMessageBox.critical(self, "Error", f"Error deleting tickets: {str(e)}")
            finally:
                session.close()

class ProductDialog(QDialog):
    """Dialog for adding/editing ticket."""
    
    def __init__(self, parent=None, product_id=None):
        super().__init__(parent)
        self.product_id = product_id
        self.init_ui()
        
        if product_id:
            self.load_product()
    
    def init_ui(self):
        self.setWindowTitle("Add Ticket" if not self.product_id else "Edit Ticket")
        self.setMinimumWidth(400)
        
        layout = QFormLayout(self)
        
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("e.g., M5, D30, E200, E100")
        layout.addRow("Name*:", self.name_input)
        
        # Add hint label
        hint_label = QLabel("Format: Capital letters + numbers (e.g., M5, D30, E200)")
        hint_label.setStyleSheet("color: #666; font-size: 11px; font-style: italic;")
        layout.addRow("", hint_label)
        
        button_layout = QHBoxLayout()
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.save)
        button_layout.addWidget(save_btn)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        layout.addRow("", button_layout)
    
    def load_product(self):
        session = db_manager.get_session()
        try:
            product = session.query(Product).get(self.product_id)
            if product:
                self.name_input.setText(product.name)
        finally:
            session.close()
    
    def save(self):
        name = self.name_input.text().strip().upper()
        
        if not name:
            QMessageBox.warning(self, "Validation Error", "Name is required.")
            return
        
        # Validate format: capital letters followed by numbers
        if not re.match(r'^[A-Z]+\d+$', name):
            QMessageBox.warning(
                self, 
                "Validation Error", 
                "Name must be in format: Capital letters + numbers\n(e.g., M5, D30, E200, E100)"
            )
            return
        
        session = db_manager.get_session()
        try:
            if self.product_id:
                product = session.query(Product).get(self.product_id)
                if product:
                    product.name = name
                    # Keep existing SKU or use name
                    if not product.sku:
                        product.sku = name
            else:
                # Create new ticket with minimal required fields
                product = Product(
                    sku=name,
                    name=name,
                    unit="pcs",  # Default unit
                    hsn_code=None,
                    tax_rate=0.0,
                    description=None
                )
                session.add(product)
            
            session.commit()
            self.accept()
        except Exception as e:
            session.rollback()
            QMessageBox.critical(self, "Error", f"Error saving ticket: {str(e)}")
        finally:
            session.close()
