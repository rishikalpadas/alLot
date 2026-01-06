"""Parties management panel."""
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                               QTableWidget, QTableWidgetItem, QDialog, QFormLayout,
                               QLineEdit, QTextEdit, QLabel, QMessageBox, QHeaderView)
from PySide6.QtCore import Qt
from database.models import Party
from database.db_manager import db_manager


class PartiesPanel(QWidget):
    """Panel for managing parties/customers."""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.load_parties()
    
    def init_ui(self):
        """Initialize UI."""
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        title = QLabel("Parties Management")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(title)
        
        button_layout = QHBoxLayout()
        add_btn = QPushButton("Add Party")
        add_btn.clicked.connect(self.add_party)
        button_layout.addWidget(add_btn)
        
        edit_btn = QPushButton("Edit Party")
        edit_btn.clicked.connect(self.edit_party)
        button_layout.addWidget(edit_btn)
        
        delete_btn = QPushButton("Delete Party")
        delete_btn.clicked.connect(self.delete_party)
        button_layout.addWidget(delete_btn)
        
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["ID", "Name", "Contact Person", "Phone", "Email"])
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self.table)
    
    def load_parties(self):
        """Load parties from database."""
        session = db_manager.get_session()
        try:
            parties = session.query(Party).all()
            self.table.setRowCount(len(parties))
            
            for row, party in enumerate(parties):
                self.table.setItem(row, 0, QTableWidgetItem(str(party.id)))
                self.table.setItem(row, 1, QTableWidgetItem(party.name))
                self.table.setItem(row, 2, QTableWidgetItem(party.contact_person or ""))
                self.table.setItem(row, 3, QTableWidgetItem(party.phone or ""))
                self.table.setItem(row, 4, QTableWidgetItem(party.email or ""))
        finally:
            session.close()
    
    def add_party(self):
        dialog = PartyDialog(self)
        if dialog.exec():
            self.load_parties()
    
    def edit_party(self):
        selected_rows = self.table.selectedIndexes()
        if not selected_rows:
            QMessageBox.warning(self, "No Selection", "Please select a party to edit.")
            return
        
        party_id = int(self.table.item(selected_rows[0].row(), 0).text())
        dialog = PartyDialog(self, party_id)
        if dialog.exec():
            self.load_parties()
    
    def delete_party(self):
        selected_rows = self.table.selectedIndexes()
        if not selected_rows:
            QMessageBox.warning(self, "No Selection", "Please select a party to delete.")
            return
        
        party_id = int(self.table.item(selected_rows[0].row(), 0).text())
        
        reply = QMessageBox.question(
            self, "Confirm Delete",
            "Are you sure you want to delete this party?\nAll associated data will be removed.",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            session = db_manager.get_session()
            try:
                party = session.query(Party).get(party_id)
                if party:
                    session.delete(party)
                    session.commit()
                    self.load_parties()
                    QMessageBox.information(self, "Success", "Party deleted successfully.")
            except Exception as e:
                session.rollback()
                QMessageBox.critical(self, "Error", f"Error deleting party: {str(e)}")
            finally:
                session.close()


class PartyDialog(QDialog):
    """Dialog for adding/editing party."""
    
    def __init__(self, parent=None, party_id=None):
        super().__init__(parent)
        self.party_id = party_id
        self.init_ui()
        
        if party_id:
            self.load_party()
    
    def init_ui(self):
        self.setWindowTitle("Add Party" if not self.party_id else "Edit Party")
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
        
        button_layout = QHBoxLayout()
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.save)
        button_layout.addWidget(save_btn)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        layout.addRow("", button_layout)
    
    def load_party(self):
        session = db_manager.get_session()
        try:
            party = session.query(Party).get(self.party_id)
            if party:
                self.name_input.setText(party.name)
                self.contact_input.setText(party.contact_person or "")
                self.phone_input.setText(party.phone or "")
                self.email_input.setText(party.email or "")
                self.address_input.setPlainText(party.address or "")
        finally:
            session.close()
    
    def save(self):
        name = self.name_input.text().strip()
        
        if not name:
            QMessageBox.warning(self, "Validation Error", "Name is required.")
            return
        
        session = db_manager.get_session()
        try:
            if self.party_id:
                party = session.query(Party).get(self.party_id)
                if party:
                    party.name = name
                    party.contact_person = self.contact_input.text().strip() or None
                    party.phone = self.phone_input.text().strip() or None
                    party.email = self.email_input.text().strip() or None
                    party.address = self.address_input.toPlainText().strip() or None
            else:
                party = Party(
                    name=name,
                    contact_person=self.contact_input.text().strip() or None,
                    phone=self.phone_input.text().strip() or None,
                    email=self.email_input.text().strip() or None,
                    address=self.address_input.toPlainText().strip() or None
                )
                session.add(party)
            
            session.commit()
            self.accept()
        except Exception as e:
            session.rollback()
            QMessageBox.critical(self, "Error", f"Error saving party: {str(e)}")
        finally:
            session.close()
