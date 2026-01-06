"""Tickets management panel."""
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                               QTableWidget, QTableWidgetItem, QDialog, QFormLayout,
                               QLineEdit, QLabel, QMessageBox, QHeaderView, QCheckBox)
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
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
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        title = QLabel("Tickets Management")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(title)
        
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
        layout.addLayout(button_layout)
        
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["☑", "#", "Name"])
        
        # Hide row numbers
        self.table.verticalHeader().setVisible(False)
        
        # Set column widths
        self.table.setColumnWidth(0, 40)   # Checkbox column
        self.table.setColumnWidth(1, 50)   # # column
        
        # Disable horizontal scrollbar and column resizing
        self.table.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Fixed)
        header.setSectionResizeMode(2, QHeaderView.Stretch)  # Name column stretches
        header.sectionClicked.connect(self.header_clicked)
        
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.setFixedHeight(240)  # Fixed height for ~5 rows + header
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
        
        # Apply modern checkbox styling separately
        self.checkbox_style = """
            QCheckBox::indicator {
                width: 20px;
                height: 20px;
                border-radius: 4px;
                border: 2px solid #BDBDBD;
                background-color: white;
            }
            QCheckBox::indicator:hover {
                border: 2px solid #2196F3;
                background-color: #E3F2FD;
            }
            QCheckBox::indicator:checked {
                background-color: #2196F3;
                border: 2px solid #2196F3;
            }
        """
        
        layout.addWidget(self.table)
        
        # Track select all state
        self.all_selected = False
    
    def load_products(self):
        session = db_manager.get_session()
        try:
            products = session.query(Product).order_by(Product.id).all()
            self.table.setRowCount(len(products))
            
            for row, product in enumerate(products):
                # Checkbox - centered in cell with modern styling
                checkbox = QCheckBox()
                checkbox.setProperty("product_id", product.id)
                checkbox.setStyleSheet(self.checkbox_style)
                
                # Set white checkmark icon for checked state
                pixmap = qta.icon('fa5s.check', color='white').pixmap(16, 16)
                checkbox.setProperty('checkedIcon', pixmap)
                
                # Update icon when toggled
                def update_icon(checked, cb=checkbox):
                    if checked:
                        icon = qta.icon('fa5s.check', color='white')
                        cb.setIcon(icon)
                    else:
                        cb.setIcon(QIcon())
                
                checkbox.toggled.connect(update_icon)
                checkbox.setIconSize(checkbox.iconSize() * 0.6)
                
                # Center the checkbox
                checkbox_widget = QWidget()
                checkbox_layout = QHBoxLayout(checkbox_widget)
                checkbox_layout.addWidget(checkbox)
                checkbox_layout.setAlignment(Qt.AlignCenter)
                checkbox_layout.setContentsMargins(0, 0, 0, 0)
                self.table.setCellWidget(row, 0, checkbox_widget)
                
                # Serial number - center aligned
                serial_item = QTableWidgetItem(str(row + 1))
                serial_item.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(row, 1, serial_item)
                
                # Name - center aligned
                name_item = QTableWidgetItem(product.name)
                name_item.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(row, 2, name_item)
        finally:
            session.close()
    
    def toggle_all_checkboxes(self):
        """Toggle all row checkboxes."""
        self.all_selected = not self.all_selected
        # Update header label with better checkbox symbols
        header_item = self.table.horizontalHeaderItem(0)
        if header_item:
            header_item.setText("☑" if self.all_selected else "☐")
        
        for row in range(self.table.rowCount()):
            checkbox_widget = self.table.cellWidget(row, 0)
            if checkbox_widget:
                checkbox = checkbox_widget.findChild(QCheckBox)
                if checkbox:
                    checkbox.setChecked(self.all_selected)
    
    def header_clicked(self, index):
        """Handle header click to toggle select all."""
        if index == 0:
            self.toggle_all_checkboxes()
    
    def add_product(self):
        dialog = ProductDialog(self)
        if dialog.exec():
            self.load_products()
    
    def edit_product(self):
        selected_rows = self.table.selectedIndexes()
        if not selected_rows:
            QMessageBox.warning(self, "No Selection", "Please select a ticket to edit.")
            return
        
        # Get product_id from checkbox widget
        row = selected_rows[0].row()
        checkbox_widget = self.table.cellWidget(row, 0)
        checkbox = checkbox_widget.findChild(QCheckBox)
        product_id = checkbox.property("product_id")
        dialog = ProductDialog(self, product_id)
        if dialog.exec():
            self.load_products()
    
    def delete_product(self):
        """Delete selected ticket(s)."""
        # Collect checked products
        selected_ids = []
        for row in range(self.table.rowCount()):
            checkbox_widget = self.table.cellWidget(row, 0)
            if checkbox_widget:
                checkbox = checkbox_widget.findChild(QCheckBox)
                if checkbox and checkbox.isChecked():
                    selected_ids.append(checkbox.property("product_id"))
        
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
