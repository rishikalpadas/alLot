"""Products management panel."""
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                               QTableWidget, QTableWidgetItem, QDialog, QFormLayout,
                               QLineEdit, QTextEdit, QLabel, QMessageBox, QHeaderView, QDoubleSpinBox)
from PySide6.QtCore import Qt
from database.models import Product
from database.db_manager import db_manager


class ProductsPanel(QWidget):
    """Panel for managing products."""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.load_products()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        title = QLabel("Products Management")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(title)
        
        button_layout = QHBoxLayout()
        add_btn = QPushButton("Add Product")
        add_btn.clicked.connect(self.add_product)
        button_layout.addWidget(add_btn)
        
        edit_btn = QPushButton("Edit Product")
        edit_btn.clicked.connect(self.edit_product)
        button_layout.addWidget(edit_btn)
        
        delete_btn = QPushButton("Delete Product")
        delete_btn.clicked.connect(self.delete_product)
        button_layout.addWidget(delete_btn)
        
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["ID", "SKU", "Name", "Unit", "Tax Rate %"])
        
        # Hide row numbers
        self.table.verticalHeader().setVisible(False)
        
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.setFixedHeight(240)  # Fixed height for ~5 rows + header
        self.table.setStyleSheet("""
            QTableWidget {
                gridline-color: #E0E0E0;
                background-color: white;
            }
            QTableWidget::item {
                padding: 8px;
            }
            QHeaderView::section {
                background-color: #F5F5F5;
                padding: 8px;
                border: none;
                border-bottom: 2px solid #E0E0E0;
                font-weight: 600;
            }
        """)
        layout.addWidget(self.table)
    
    def load_products(self):
        session = db_manager.get_session()
        try:
            products = session.query(Product).all()
            self.table.setRowCount(len(products))
            
            for row, product in enumerate(products):
                self.table.setItem(row, 0, QTableWidgetItem(str(product.id)))
                self.table.setItem(row, 1, QTableWidgetItem(product.sku))
                self.table.setItem(row, 2, QTableWidgetItem(product.name))
                self.table.setItem(row, 3, QTableWidgetItem(product.unit))
                self.table.setItem(row, 4, QTableWidgetItem(f"{product.tax_rate:.2f}"))
        finally:
            session.close()
    
    def add_product(self):
        dialog = ProductDialog(self)
        if dialog.exec():
            self.load_products()
    
    def edit_product(self):
        selected_rows = self.table.selectedIndexes()
        if not selected_rows:
            QMessageBox.warning(self, "No Selection", "Please select a product to edit.")
            return
        
        product_id = int(self.table.item(selected_rows[0].row(), 0).text())
        dialog = ProductDialog(self, product_id)
        if dialog.exec():
            self.load_products()
    
    def delete_product(self):
        selected_rows = self.table.selectedIndexes()
        if not selected_rows:
            QMessageBox.warning(self, "No Selection", "Please select a product to delete.")
            return
        
        product_id = int(self.table.item(selected_rows[0].row(), 0).text())
        
        reply = QMessageBox.question(
            self, "Confirm Delete",
            "Are you sure you want to delete this product?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            session = db_manager.get_session()
            try:
                product = session.query(Product).get(product_id)
                if product:
                    session.delete(product)
                    session.commit()
                    self.load_products()
                    QMessageBox.information(self, "Success", "Product deleted successfully.")
            except Exception as e:
                session.rollback()
                QMessageBox.critical(self, "Error", f"Error deleting product: {str(e)}")
            finally:
                session.close()


class ProductDialog(QDialog):
    """Dialog for adding/editing product."""
    
    def __init__(self, parent=None, product_id=None):
        super().__init__(parent)
        self.product_id = product_id
        self.init_ui()
        
        if product_id:
            self.load_product()
    
    def init_ui(self):
        self.setWindowTitle("Add Product" if not self.product_id else "Edit Product")
        self.setMinimumWidth(400)
        
        layout = QFormLayout(self)
        
        self.sku_input = QLineEdit()
        layout.addRow("SKU*:", self.sku_input)
        
        self.name_input = QLineEdit()
        layout.addRow("Name*:", self.name_input)
        
        self.unit_input = QLineEdit()
        self.unit_input.setPlaceholderText("e.g., pcs, kg, ltr")
        layout.addRow("Unit*:", self.unit_input)
        
        self.hsn_input = QLineEdit()
        layout.addRow("HSN Code:", self.hsn_input)
        
        self.tax_input = QDoubleSpinBox()
        self.tax_input.setRange(0, 100)
        self.tax_input.setDecimals(2)
        self.tax_input.setSuffix(" %")
        layout.addRow("Tax Rate:", self.tax_input)
        
        self.description_input = QTextEdit()
        self.description_input.setMaximumHeight(80)
        layout.addRow("Description:", self.description_input)
        
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
                self.sku_input.setText(product.sku)
                self.name_input.setText(product.name)
                self.unit_input.setText(product.unit)
                self.hsn_input.setText(product.hsn_code or "")
                self.tax_input.setValue(product.tax_rate)
                self.description_input.setPlainText(product.description or "")
        finally:
            session.close()
    
    def save(self):
        sku = self.sku_input.text().strip()
        name = self.name_input.text().strip()
        unit = self.unit_input.text().strip()
        
        if not sku or not name or not unit:
            QMessageBox.warning(self, "Validation Error", "SKU, Name, and Unit are required.")
            return
        
        session = db_manager.get_session()
        try:
            if self.product_id:
                product = session.query(Product).get(self.product_id)
                if product:
                    product.sku = sku
                    product.name = name
                    product.unit = unit
                    product.hsn_code = self.hsn_input.text().strip() or None
                    product.tax_rate = self.tax_input.value()
                    product.description = self.description_input.toPlainText().strip() or None
            else:
                product = Product(
                    sku=sku,
                    name=name,
                    unit=unit,
                    hsn_code=self.hsn_input.text().strip() or None,
                    tax_rate=self.tax_input.value(),
                    description=self.description_input.toPlainText().strip() or None
                )
                session.add(product)
            
            session.commit()
            self.accept()
        except Exception as e:
            session.rollback()
            QMessageBox.critical(self, "Error", f"Error saving product: {str(e)}")
        finally:
            session.close()
