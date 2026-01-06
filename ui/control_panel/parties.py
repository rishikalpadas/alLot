"""Parties management panel."""
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                               QTableWidget, QTableWidgetItem, QDialog, QFormLayout,
                               QLineEdit, QTextEdit, QLabel, QMessageBox, QHeaderView, QCheckBox)
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
import qtawesome as qta
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
        
        edit_btn = QPushButton(" Edit")
        edit_btn.setIcon(qta.icon('fa5s.edit', color='white'))
        edit_btn.clicked.connect(self.edit_party)
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
        delete_btn.clicked.connect(self.delete_party)
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
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["☑", "#", "ID", "Name", "Sell Rate"])
        
        # Hide row numbers
        self.table.verticalHeader().setVisible(False)
        
        # Set column widths - total ~550px to avoid horizontal scrollbar
        self.table.setColumnWidth(0, 40)   # Checkbox column
        self.table.setColumnWidth(1, 50)   # # column
        self.table.setColumnWidth(2, 80)   # ID column
        self.table.setColumnWidth(3, 250)  # Name column - expanded
        self.table.setColumnWidth(4, 110)  # Sell Rate column - shrunk
        
        # Disable horizontal scrollbar and column resizing
        self.table.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Fixed)
        header.setSectionResizeMode(4, QHeaderView.Stretch)  # Last column stretches
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
    
    def load_parties(self):
        """Load parties from database."""
        session = db_manager.get_session()
        try:
            parties = session.query(Party).order_by(Party.id).all()
            self.table.setRowCount(len(parties))
            
            for row, party in enumerate(parties):
                # Checkbox - centered in cell with modern styling
                checkbox = QCheckBox()
                checkbox.setProperty("party_id", party.id)
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
                
                # Display ID - center aligned
                id_item = QTableWidgetItem(party.display_id or f"P{party.id:03d}")
                id_item.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(row, 2, id_item)
                
                # Name - center aligned
                name_item = QTableWidgetItem(party.name)
                name_item.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(row, 3, name_item)
                
                # Sell Rate - center aligned
                rate_item = QTableWidgetItem(f"₹ {party.sell_rate:.2f}")
                rate_item.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(row, 4, rate_item)
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
    
    def add_party(self):
        dialog = PartyDialog(self)
        if dialog.exec():
            self.load_parties()
    
    def edit_party(self):
        selected_rows = self.table.selectedIndexes()
        if not selected_rows:
            QMessageBox.warning(self, "No Selection", "Please select a party to edit.")
            return
        
        # Get party_id from checkbox widget
        row = selected_rows[0].row()
        checkbox_widget = self.table.cellWidget(row, 0)
        checkbox = checkbox_widget.findChild(QCheckBox)
        party_id = checkbox.property("party_id")
        dialog = PartyDialog(self, party_id)
        if dialog.exec():
            self.load_parties()
    
    def delete_party(self):
        """Delete selected party/parties."""
        # Collect checked parties
        selected_ids = []
        for row in range(self.table.rowCount()):
            checkbox_widget = self.table.cellWidget(row, 0)
            if checkbox_widget:
                checkbox = checkbox_widget.findChild(QCheckBox)
                if checkbox and checkbox.isChecked():
                    selected_ids.append(checkbox.property("party_id"))
        
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
