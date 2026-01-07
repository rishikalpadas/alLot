"""Parties management panel."""
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                               QTableWidget, QTableWidgetItem, QDialog, QFormLayout,
                               QLineEdit, QTextEdit, QLabel, QMessageBox, QHeaderView)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QIcon, QKeyEvent
import qtawesome as qta
from database.models import Party
from database.db_manager import db_manager


class PartiesPanel(QWidget):
    """Panel for managing parties/customers."""
    
    def __init__(self):
        super().__init__()
        self.removing_row = False  # Flag to prevent re-entrancy
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
        button_layout.setSpacing(10)
        
        add_btn = QPushButton(" Add Party")
        add_btn.setIcon(qta.icon('fa5s.plus', color='white'))
        add_btn.clicked.connect(self.add_party)
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
        
        self.delete_btn = QPushButton(" Delete")
        self.delete_btn.setIcon(qta.icon('fa5s.trash-alt', color='white'))
        self.delete_btn.clicked.connect(self.delete_party)
        self.delete_btn.setCursor(Qt.PointingHandCursor)
        self.delete_btn.setStyleSheet("""
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
        button_layout.addWidget(self.delete_btn)
        
        # Initially hide delete button (only show when selection exists)
        self.delete_btn.setVisible(False)
        
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["#", "ID", "Name", "Sell Rate"])
        
        # Hide row numbers
        self.table.verticalHeader().setVisible(False)
        
        # Set column widths
        self.table.setColumnWidth(0, 50)   # # column
        self.table.setColumnWidth(1, 80)   # ID column
        self.table.setColumnWidth(2, 290)  # Name column
        self.table.setColumnWidth(3, 110)  # Sell Rate column
        
        # Disable horizontal scrollbar and column resizing
        self.table.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Fixed)
        header.setSectionResizeMode(3, QHeaderView.Stretch)  # Last column stretches
        
        # Connect itemChanged for inline editing workflow
        self.table.itemChanged.connect(self.on_item_changed)
        self.table.itemSelectionChanged.connect(self.update_buttons)
        self.table.itemSelectionChanged.connect(self.on_selection_changed)
        self.table.itemDoubleClicked.connect(self.on_item_double_clicked)
        
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.ExtendedSelection)  # Enable Ctrl+click multi-select
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setFocusPolicy(Qt.NoFocus)  # Disable individual cell focus
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
        
        layout.addWidget(self.table)
    
    def load_parties(self):
        """Load parties from database."""
        session = db_manager.get_session()
        try:
            parties = session.query(Party).order_by(Party.id).all()
            self.table.setRowCount(len(parties))
            
            for row, party in enumerate(parties):
                # Serial number - center aligned
                serial_item = QTableWidgetItem(str(row + 1))
                serial_item.setTextAlignment(Qt.AlignCenter)
                serial_item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
                self.table.setItem(row, 0, serial_item)
                
                # Display ID - center aligned
                id_item = QTableWidgetItem(party.display_id or f"P{party.id:03d}")
                id_item.setTextAlignment(Qt.AlignCenter)
                id_item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
                self.table.setItem(row, 1, id_item)
                
                # Name - center aligned
                name_item = QTableWidgetItem(party.name)
                name_item.setTextAlignment(Qt.AlignCenter)
                name_item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
                self.table.setItem(row, 2, name_item)
                
                # Sell Rate - center aligned
                rate_item = QTableWidgetItem(f"₹ {party.sell_rate:.2f}")
                rate_item.setTextAlignment(Qt.AlignCenter)
                rate_item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
                rate_item.setData(Qt.UserRole, party.id)
                self.table.setItem(row, 3, rate_item)
        finally:
            session.close()
    
    def update_buttons(self):
        """Update button visibility based on selection."""
        selected_rows = self.table.selectionModel().selectedRows()
        count = len(selected_rows)
        
        # Check if any selected row is a new row (serial = "*")
        has_new_row = False
        for index in selected_rows:
            serial_item = self.table.item(index.row(), 0)
            if serial_item and serial_item.text() == "*":
                has_new_row = True
                break
        
        if has_new_row or count == 0:
            # No selection or new row selected: hide delete button
            self.delete_btn.setVisible(False)
        else:
            # Any selection: show delete button
            self.delete_btn.setVisible(True)
    
    def save_new_row(self, row):
        """Save the new party row to database."""
        name_item = self.table.item(row, 2)
        rate_item = self.table.item(row, 3)
        
        if not name_item or not rate_item:
            return False
            
        name = name_item.text().strip()
        rate_text = rate_item.text().strip()
        
        if not name or not rate_text:
            QMessageBox.warning(self, "Validation Error", "Name and Sell Rate are required.")
            return False
        
        try:
            sell_rate = float(rate_text)
        except ValueError:
            QMessageBox.warning(self, "Validation Error", "Sell Rate must be a valid number.")
            return False
        
        if sell_rate < 0:
            QMessageBox.warning(self, "Validation Error", "Sell Rate cannot be negative.")
            return False
        
        session = db_manager.get_session()
        try:
            # Generate display_id
            first_letter = name[0].upper() if name else 'P'
            existing = session.query(Party).filter(
                Party.display_id.like(f"{first_letter}%")
            ).all()
            max_num = 0
            for p in existing:
                if p.display_id and len(p.display_id) > 1:
                    try:
                        num = int(p.display_id[1:])
                        max_num = max(max_num, num)
                    except ValueError:
                        pass
            display_id = f"{first_letter}{max_num + 1:03d}"
            
            party = Party(
                name=name,
                sell_rate=sell_rate,
                display_id=display_id
            )
            session.add(party)
            session.commit()
            
            # Reload the table
            self.load_parties()
            
            # Add another new row for quick entry
            self.add_party()
            
            return True
        except Exception as e:
            session.rollback()
            QMessageBox.critical(self, "Error", f"Error saving party: {str(e)}")
            return False
        finally:
            session.close()
    
    def on_item_changed(self, item):
        """Handle item changes for inline editing workflow."""
        row = item.row()
        col = item.column()
        
        # Check if this is a new row (serial = "*")
        serial_item = self.table.item(row, 0)
        if not serial_item or serial_item.text() != "*":
            return
        
        # If name field was edited, move to rate field
        if col == 2 and item.text().strip():
            self.table.setCurrentCell(row, 3)
            self.table.editItem(self.table.item(row, 3))
        # If rate field was edited, save the row
        elif col == 3 and item.text().strip():
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
        if self.removing_row:  # Prevent re-entrancy
            return
        
        current_row = self.table.currentRow()
        if current_row < 0:
            return
        
        # Check if there's a new row being edited
        for row in range(self.table.rowCount()):
            serial_item = self.table.item(row, 0)
            if serial_item and serial_item.text() == "*":
                # If clicking on a different row, cancel the new row
                if row != current_row:
                    self.removing_row = True
                    self.table.removeRow(row)
                    self.removing_row = False
                return
    
    def add_party(self):
        """Add new party with inline editing."""
        # Add new editable row at the bottom
        row = self.table.rowCount()
        self.table.insertRow(row)
        
        # Serial number
        serial_item = QTableWidgetItem("*")
        serial_item.setTextAlignment(Qt.AlignCenter)
        serial_item.setFlags(serial_item.flags() & ~Qt.ItemIsEditable)
        serial_item.setBackground(Qt.lightGray)
        self.table.setItem(row, 0, serial_item)
        
        # ID (will be auto-generated)
        id_item = QTableWidgetItem("NEW")
        id_item.setTextAlignment(Qt.AlignCenter)
        id_item.setFlags(id_item.flags() & ~Qt.ItemIsEditable)
        id_item.setBackground(Qt.lightGray)
        self.table.setItem(row, 1, id_item)
        
        # Name - editable
        name_item = QTableWidgetItem("")
        name_item.setTextAlignment(Qt.AlignCenter)
        name_item.setBackground(Qt.yellow)
        self.table.setItem(row, 2, name_item)
        
        # Sell Rate - editable
        rate_item = QTableWidgetItem("")
        rate_item.setTextAlignment(Qt.AlignCenter)
        rate_item.setBackground(Qt.yellow)
        self.table.setItem(row, 3, rate_item)
        
        # Scroll to bottom and set focus on name field
        self.table.scrollToBottom()
        self.table.setCurrentCell(row, 2)
        self.table.editItem(name_item)
    
    def on_item_double_clicked(self, item):
        """Handle double-click to edit party."""
        row = item.row()
        serial_item = self.table.item(row, 0)
        
        # Don't allow editing new rows via double-click
        if serial_item and serial_item.text() == "*":
            return
        
        rate_item = self.table.item(row, 3)
        if rate_item:
            party_id = rate_item.data(Qt.UserRole)
            if party_id:
                dialog = PartyDialog(self, party_id)
                if dialog.exec():
                    self.load_parties()
    
    def edit_party(self):
        selected_rows = self.table.selectedIndexes()
        if not selected_rows:
            QMessageBox.warning(self, "No Selection", "Please select a party to edit.")
            return
        
        # Get party_id from rate item's UserRole data
        row = selected_rows[0].row()
        rate_item = self.table.item(row, 3)
        party_id = rate_item.data(Qt.UserRole)
        dialog = PartyDialog(self, party_id)
        if dialog.exec():
            self.load_parties()
    
    def delete_party(self):
        """Delete selected party/parties."""
        # Collect selected parties
        selected_rows = self.table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "No Selection", "Please select at least one party to delete.")
            return
        
        selected_ids = []
        for index in selected_rows:
            row = index.row()
            rate_item = self.table.item(row, 3)
            party_id = rate_item.data(Qt.UserRole)
            if party_id:
                selected_ids.append(party_id)
        
        if not selected_ids:
            QMessageBox.warning(self, "No Selection", "Please select at least one party to delete.")
            return
        
        count = len(selected_ids)
        reply = QMessageBox.question(
            self, "Confirm Delete",
            f"Are you sure you want to delete {count} party/parties?\nAll associated data will be removed.",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            session = db_manager.get_session()
            try:
                for party_id in selected_ids:
                    party = session.query(Party).get(party_id)
                    if party:
                        session.delete(party)
                session.commit()
                self.load_parties()
                QMessageBox.information(self, "Success", f"{count} party/parties deleted successfully.")
            except Exception as e:
                session.rollback()
                QMessageBox.critical(self, "Error", f"Error deleting parties: {str(e)}")
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
                # Create new - generate display_id
                first_letter = name[0].upper() if name else 'P'
                # Find highest number for this letter
                existing = session.query(Party).filter(
                    Party.display_id.like(f"{first_letter}%")
                ).all()
                max_num = 0
                for p in existing:
                    if p.display_id and len(p.display_id) > 1:
                        try:
                            num = int(p.display_id[1:])
                            max_num = max(max_num, num)
                        except ValueError:
                            pass
                display_id = f"{first_letter}{max_num + 1:03d}"
                
                party = Party(
                    name=name,
                    sell_rate=sell_rate,
                    display_id=display_id
                )
                session.add(party)
            
            session.commit()
            self.accept()
        except Exception as e:
            session.rollback()
            QMessageBox.critical(self, "Error", f"Error saving party: {str(e)}")
        finally:
            session.close()
