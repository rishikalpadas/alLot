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
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["ID", "Name", "Sell Rate"])
        
        # Hide row numbers
        self.table.verticalHeader().setVisible(False)
        
        # Set column widths
        self.table.setColumnWidth(0, 60)  # ID column - narrow
        self.table.setColumnWidth(1, 300)  # Name column - moderate
        self.table.setColumnWidth(2, 150)  # Sell Rate column - moderate
        
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
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
    
    def load_parties(self):
        """Load parties from database."""
        session = db_manager.get_session()
        try:
            parties = session.query(Party).all()
            self.table.setRowCount(len(parties))
            
            for row, party in enumerate(parties):
                self.table.setItem(row, 0, QTableWidgetItem(str(party.id)))
                self.table.setItem(row, 1, QTableWidgetItem(party.name))
                self.table.setItem(row, 2, QTableWidgetItem(f"₹ {party.sell_rate:.2f}"))
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
        
        self.sell_rate_input = QLineEdit()
        self.sell_rate_input.setPlaceholderText("0.00")
        layout.addRow("Sell Rate*:", self.sell_rate_input)
        
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
                self.sell_rate_input.setText(str(party.sell_rate))
        finally:
            session.close()
    
    def save(self):
        name = self.name_input.text().strip()
        sell_rate_text = self.sell_rate_input.text().strip()
        
        if not name:
            QMessageBox.warning(self, "Validation Error", "Name is required.")
            return
        
        try:
            sell_rate = float(sell_rate_text) if sell_rate_text else 0.0
        except ValueError:
            QMessageBox.warning(self, "Validation Error", "Sell Rate must be a valid number.")
            return
        
        if sell_rate < 0:
            QMessageBox.warning(self, "Validation Error", "Sell Rate cannot be negative.")
            return
        
        session = db_manager.get_session()
        try:
            if self.party_id:
                party = session.query(Party).get(self.party_id)
                if party:
                    party.name = name
                    party.sell_rate = sell_rate
            else:
                party = Party(
                    name=name,
                    sell_rate=sell_rate
                )
                session.add(party)
            
            session.commit()
            self.accept()
        except Exception as e:
            session.rollback()
            QMessageBox.critical(self, "Error", f"Error saving party: {str(e)}")
        finally:
            session.close()
