"""Distributors management panel."""
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                               QTableWidget, QTableWidgetItem, QDialog, QFormLayout,
                               QLineEdit, QTextEdit, QLabel, QMessageBox, QHeaderView)
from PySide6.QtCore import Qt
from database.models import Distributor
from database.db_manager import db_manager


class DistributorsPanel(QWidget):
    """Panel for managing distributors."""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.load_distributors()
    
    def init_ui(self):
        """Initialize UI."""
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Title
        title = QLabel("Distributors Management")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(title)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        add_btn = QPushButton("Add Distributor")
        add_btn.clicked.connect(self.add_distributor)
        button_layout.addWidget(add_btn)
        
        edit_btn = QPushButton("Edit Distributor")
        edit_btn.clicked.connect(self.edit_distributor)
        button_layout.addWidget(edit_btn)
        
        delete_btn = QPushButton("Delete Distributor")
        delete_btn.clicked.connect(self.delete_distributor)
        button_layout.addWidget(delete_btn)
        
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["ID", "Name", "Contact Person", "Phone", "Email"])
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self.table)
    
    def load_distributors(self):
        """Load distributors from database."""
        session = db_manager.get_session()
        try:
            distributors = session.query(Distributor).all()
            self.table.setRowCount(len(distributors))
            
            for row, dist in enumerate(distributors):
                self.table.setItem(row, 0, QTableWidgetItem(str(dist.id)))
                self.table.setItem(row, 1, QTableWidgetItem(dist.name))
                self.table.setItem(row, 2, QTableWidgetItem(dist.contact_person or ""))
                self.table.setItem(row, 3, QTableWidgetItem(dist.phone or ""))
                self.table.setItem(row, 4, QTableWidgetItem(dist.email or ""))
        finally:
            session.close()
    
    def add_distributor(self):
        """Add new distributor."""
        dialog = DistributorDialog(self)
        if dialog.exec():
            self.load_distributors()
    
    def edit_distributor(self):
        """Edit selected distributor."""
        selected_rows = self.table.selectedIndexes()
        if not selected_rows:
            QMessageBox.warning(self, "No Selection", "Please select a distributor to edit.")
            return
        
        distributor_id = int(self.table.item(selected_rows[0].row(), 0).text())
        dialog = DistributorDialog(self, distributor_id)
        if dialog.exec():
            self.load_distributors()
    
    def delete_distributor(self):
        """Delete selected distributor."""
        selected_rows = self.table.selectedIndexes()
        if not selected_rows:
            QMessageBox.warning(self, "No Selection", "Please select a distributor to delete.")
            return
        
        distributor_id = int(self.table.item(selected_rows[0].row(), 0).text())
        
        reply = QMessageBox.question(
            self, "Confirm Delete",
            "Are you sure you want to delete this distributor?\nAll associated data will be removed.",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            session = db_manager.get_session()
            try:
                distributor = session.query(Distributor).get(distributor_id)
                if distributor:
                    session.delete(distributor)
                    session.commit()
                    self.load_distributors()
                    QMessageBox.information(self, "Success", "Distributor deleted successfully.")
            except Exception as e:
                session.rollback()
                QMessageBox.critical(self, "Error", f"Error deleting distributor: {str(e)}")
            finally:
                session.close()


class DistributorDialog(QDialog):
    """Dialog for adding/editing distributor."""
    
    def __init__(self, parent=None, distributor_id=None):
        super().__init__(parent)
        self.distributor_id = distributor_id
        self.init_ui()
        
        if distributor_id:
            self.load_distributor()
    
    def init_ui(self):
        """Initialize UI."""
        self.setWindowTitle("Add Distributor" if not self.distributor_id else "Edit Distributor")
        self.setMinimumWidth(400)
        
        layout = QFormLayout(self)
        
        self.name_input = QLineEdit()
        layout.addRow("Name*:", self.name_input)
        
        self.contact_input = QLineEdit()
        layout.addRow("Contact Person:", self.contact_input)
        
        self.phone_input = QLineEdit()
        layout.addRow("Phone:", self.phone_input)
        
        self.email_input = QLineEdit()
        layout.addRow("Email:", self.email_input)
        
        self.address_input = QTextEdit()
        self.address_input.setMaximumHeight(80)
        layout.addRow("Address:", self.address_input)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.save)
        button_layout.addWidget(save_btn)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        layout.addRow("", button_layout)
    
    def load_distributor(self):
        """Load distributor data."""
        session = db_manager.get_session()
        try:
            distributor = session.query(Distributor).get(self.distributor_id)
            if distributor:
                self.name_input.setText(distributor.name)
                self.contact_input.setText(distributor.contact_person or "")
                self.phone_input.setText(distributor.phone or "")
                self.email_input.setText(distributor.email or "")
                self.address_input.setPlainText(distributor.address or "")
        finally:
            session.close()
    
    def save(self):
        """Save distributor."""
        name = self.name_input.text().strip()
        
        if not name:
            QMessageBox.warning(self, "Validation Error", "Name is required.")
            return
        
        session = db_manager.get_session()
        try:
            if self.distributor_id:
                # Update existing
                distributor = session.query(Distributor).get(self.distributor_id)
                if distributor:
                    distributor.name = name
                    distributor.contact_person = self.contact_input.text().strip() or None
                    distributor.phone = self.phone_input.text().strip() or None
                    distributor.email = self.email_input.text().strip() or None
                    distributor.address = self.address_input.toPlainText().strip() or None
            else:
                # Create new
                distributor = Distributor(
                    name=name,
                    contact_person=self.contact_input.text().strip() or None,
                    phone=self.phone_input.text().strip() or None,
                    email=self.email_input.text().strip() or None,
                    address=self.address_input.toPlainText().strip() or None
                )
                session.add(distributor)
            
            session.commit()
            self.accept()
        except Exception as e:
            session.rollback()
            QMessageBox.critical(self, "Error", f"Error saving distributor: {str(e)}")
        finally:
            session.close()
