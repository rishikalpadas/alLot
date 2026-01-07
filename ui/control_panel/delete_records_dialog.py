"""Dialog for deleting database records."""
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton, 
                               QRadioButton, QButtonGroup, QLabel, QMessageBox,
                               QDateEdit, QCheckBox)
from PySide6.QtCore import Qt, QDate
from database.models import Purchase, Sale, Distributor, Party, Product
from database.db_manager import db_manager


class DeleteRecordsDialog(QDialog):
    """Dialog for selecting what records to delete."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Delete Records")
        self.setMinimumWidth(500)
        self.init_ui()
    
    def init_ui(self):
        """Initialize UI."""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        
        # Title
        title = QLabel("Select Records to Delete")
        title.setStyleSheet("font-size: 14px; font-weight: bold;")
        layout.addWidget(title)
        
        # Radio buttons for different delete options
        self.button_group = QButtonGroup()
        
        # Option 1: Delete by date range (purchases/sales)
        self.transactions_radio = QRadioButton("Delete Transactions by Date Range")
        self.transactions_radio.setChecked(True)
        self.transactions_radio.toggled.connect(self.on_option_changed)
        self.button_group.addButton(self.transactions_radio, 0)
        layout.addWidget(self.transactions_radio)
        
        # Transaction options
        self.trans_options_layout = QVBoxLayout()
        self.trans_options_layout.setContentsMargins(20, 10, 0, 10)
        
        self.purchase_checkbox = QCheckBox("Delete Purchase Records")
        self.purchase_checkbox.setChecked(True)
        self.trans_options_layout.addWidget(self.purchase_checkbox)
        
        self.sale_checkbox = QCheckBox("Delete Sale Records")
        self.sale_checkbox.setChecked(True)
        self.trans_options_layout.addWidget(self.sale_checkbox)
        
        date_range_layout = QHBoxLayout()
        date_range_layout.addWidget(QLabel("From:"))
        self.from_date = QDateEdit()
        self.from_date.setDate(QDate.currentDate().addMonths(-1))
        date_range_layout.addWidget(self.from_date)
        
        date_range_layout.addWidget(QLabel("To:"))
        self.to_date = QDateEdit()
        self.to_date.setDate(QDate.currentDate())
        date_range_layout.addWidget(self.to_date)
        self.trans_options_layout.addLayout(date_range_layout)
        
        layout.addLayout(self.trans_options_layout)
        
        # Option 2: Delete all parties
        self.parties_radio = QRadioButton("Delete All Parties")
        self.button_group.addButton(self.parties_radio, 1)
        layout.addWidget(self.parties_radio)
        
        # Option 3: Delete all distributors
        self.distributors_radio = QRadioButton("Delete All Distributors")
        self.button_group.addButton(self.distributors_radio, 2)
        layout.addWidget(self.distributors_radio)
        
        # Option 4: Delete all tickets/products
        self.products_radio = QRadioButton("Delete All Tickets/Products")
        self.button_group.addButton(self.products_radio, 3)
        layout.addWidget(self.products_radio)
        
        layout.addStretch()
        
        # Buttons
        button_layout = QHBoxLayout()
        
        delete_btn = QPushButton("Delete")
        delete_btn.clicked.connect(self.delete_records)
        delete_btn.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #da190b;
            }
        """)
        button_layout.addWidget(delete_btn)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #888;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #777;
            }
        """)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
    
    def on_option_changed(self):
        """Handle option change."""
        # Enable/disable date options based on selection
        is_transactions = self.transactions_radio.isChecked()
        self.from_date.setEnabled(is_transactions)
        self.to_date.setEnabled(is_transactions)
        self.purchase_checkbox.setEnabled(is_transactions)
        self.sale_checkbox.setEnabled(is_transactions)
    
    def delete_records(self):
        """Delete selected records."""
        selected_id = self.button_group.checkedId()
        
        # Confirm deletion
        confirmation = QMessageBox.question(
            self,
            "Confirm Deletion",
            "This action cannot be undone. Continue?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if confirmation != QMessageBox.Yes:
            return
        
        session = db_manager.get_session()
        try:
            if selected_id == 0:  # Delete transactions by date
                from_date = self.from_date.date().toPython()
                to_date = self.to_date.date().toPython()
                
                count = 0
                if self.purchase_checkbox.isChecked():
                    purchases = session.query(Purchase).filter(
                        Purchase.date >= from_date,
                        Purchase.date <= to_date
                    ).all()
                    count += len(purchases)
                    for purchase in purchases:
                        session.delete(purchase)
                
                if self.sale_checkbox.isChecked():
                    sales = session.query(Sale).filter(
                        Sale.date >= from_date,
                        Sale.date <= to_date
                    ).all()
                    count += len(sales)
                    for sale in sales:
                        session.delete(sale)
                
                session.commit()
                QMessageBox.information(self, "Success", f"Deleted {count} transaction(s).")
                
            elif selected_id == 1:  # Delete all parties
                parties = session.query(Party).all()
                for party in parties:
                    session.delete(party)
                session.commit()
                QMessageBox.information(self, "Success", f"Deleted {len(parties)} party/parties.")
                
            elif selected_id == 2:  # Delete all distributors
                distributors = session.query(Distributor).all()
                for distributor in distributors:
                    session.delete(distributor)
                session.commit()
                QMessageBox.information(self, "Success", f"Deleted {len(distributors)} distributor(s).")
                
            elif selected_id == 3:  # Delete all products
                products = session.query(Product).all()
                for product in products:
                    session.delete(product)
                session.commit()
                QMessageBox.information(self, "Success", f"Deleted {len(products)} product(s).")
            
            self.accept()
            
        except Exception as e:
            session.rollback()
            QMessageBox.critical(self, "Error", f"Error deleting records: {str(e)}")
        finally:
            session.close()
