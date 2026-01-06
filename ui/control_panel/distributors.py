"""Distributors management panel."""
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                               QTableWidget, QTableWidgetItem, QDialog, QFormLayout,
                               QLineEdit, QTextEdit, QLabel, QMessageBox, QHeaderView)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QIcon, QKeyEvent
import qtawesome as qta
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
        button_layout.setSpacing(10)
        
        add_btn = QPushButton(" Add Distributor")
        add_btn.setIcon(qta.icon('fa5s.plus', color='white'))
        add_btn.clicked.connect(self.add_distributor)
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
        edit_btn.clicked.connect(self.edit_distributor)
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
        delete_btn.clicked.connect(self.delete_distributor)
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
        
        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["#", "ID", "Name", "Purchase Rate"])
        
        # Hide row numbers
        self.table.verticalHeader().setVisible(False)
        
        # Set column widths
        self.table.setColumnWidth(0, 50)   # # column
        self.table.setColumnWidth(1, 80)   # ID column
        self.table.setColumnWidth(2, 290)  # Name column
        self.table.setColumnWidth(3, 110)  # Purchase Rate column
        
        # Disable horizontal scrollbar and column resizing
        self.table.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Fixed)
        header.setSectionResizeMode(3, QHeaderView.Stretch)  # Last column stretches
        
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
    
    def load_distributors(self):
        """Load distributors from database."""
        session = db_manager.get_session()
        try:
            distributors = session.query(Distributor).order_by(Distributor.id).all()
            self.table.setRowCount(len(distributors))
            
            for row, dist in enumerate(distributors):
                # Serial number - center aligned
                serial_item = QTableWidgetItem(str(row + 1))
                serial_item.setTextAlignment(Qt.AlignCenter)
                serial_item.setFlags(serial_item.flags() & ~Qt.ItemIsEditable)
                self.table.setItem(row, 0, serial_item)
                
                # Display ID - center aligned
                id_item = QTableWidgetItem(dist.display_id or f"D{dist.id:03d}")
                id_item.setTextAlignment(Qt.AlignCenter)
                id_item.setFlags(id_item.flags() & ~Qt.ItemIsEditable)
                self.table.setItem(row, 1, id_item)
                
                # Name - center aligned
                name_item = QTableWidgetItem(dist.name)
                name_item.setTextAlignment(Qt.AlignCenter)
                name_item.setFlags(name_item.flags() & ~Qt.ItemIsEditable)
                self.table.setItem(row, 2, name_item)
                
                # Purchase Rate - center aligned
                rate_item = QTableWidgetItem(f"₹ {dist.purchase_rate:.2f}")
                rate_item.setTextAlignment(Qt.AlignCenter)
                rate_item.setFlags(rate_item.flags() & ~Qt.ItemIsEditable)
                rate_item.setData(Qt.UserRole, dist.id)
                self.table.setItem(row, 3, rate_item)
        finally:
            session.close()
    
    def save_new_row(self, row):
        """Save the new distributor row to database."""
        name_item = self.table.item(row, 2)
        rate_item = self.table.item(row, 3)
        
        if not name_item or not rate_item:
            return False
            
        name = name_item.text().strip()
        rate_text = rate_item.text().strip()
        
        if not name or not rate_text:
            QMessageBox.warning(self, "Validation Error", "Name and Purchase Rate are required.")
            return False
        
        try:
            purchase_rate = float(rate_text)
        except ValueError:
            QMessageBox.warning(self, "Validation Error", "Purchase Rate must be a valid number.")
            return False
        
        if purchase_rate < 0:
            QMessageBox.warning(self, "Validation Error", "Purchase Rate cannot be negative.")
            return False
        
        session = db_manager.get_session()
        try:
            # Generate display_id
            first_letter = name[0].upper() if name else 'D'
            existing = session.query(Distributor).filter(
                Distributor.display_id.like(f"{first_letter}%")
            ).all()
            max_num = 0
            for dist in existing:
                if dist.display_id and len(dist.display_id) > 1:
                    try:
                        num = int(dist.display_id[1:])
                        max_num = max(max_num, num)
                    except ValueError:
                        pass
            display_id = f"{first_letter}{max_num + 1:03d}"
            
            distributor = Distributor(
                name=name,
                purchase_rate=purchase_rate,
                display_id=display_id
            )
            session.add(distributor)
            session.commit()
            
            # Reload the table
            self.load_distributors()
            
            # Add another new row for quick entry
            self.add_distributor()
            
            return True
        except Exception as e:
            session.rollback()
            QMessageBox.critical(self, "Error", f"Error saving distributor: {str(e)}")
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
    
    def add_distributor(self):
        """Add new distributor with inline editing."""
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
        
        # Purchase Rate - editable
        rate_item = QTableWidgetItem("")
        rate_item.setTextAlignment(Qt.AlignCenter)
        rate_item.setBackground(Qt.yellow)
        self.table.setItem(row, 3, rate_item)
        
        # Scroll to bottom and set focus on name field
        self.table.scrollToBottom()
        self.table.setCurrentCell(row, 2)
        self.table.editItem(name_item)
    
    def edit_distributor(self):
        """Edit selected distributor."""
        selected_rows = self.table.selectedIndexes()
        if not selected_rows:
            QMessageBox.warning(self, "No Selection", "Please select a distributor to edit.")
            return
        
        # Get distributor_id from checkbox widget
        row = selected_rows[0].row()
        checkbox_widget = self.table.cellWidget(row, 0)
        checkbox = checkbox_widget.findChild(QCheckBox)
        distributor_id = checkbox.property("distributor_id")
        dialog = DistributorDialog(self, distributor_id)
        if dialog.exec():
            self.load_distributors()
    
    def delete_distributor(self):
        """Delete selected distributor(s)."""
        # Collect checked distributors
        selected_ids = []
        for row in range(self.table.rowCount()):
            checkbox_widget = self.table.cellWidget(row, 0)
            if checkbox_widget:
                checkbox = checkbox_widget.findChild(QCheckBox)
                if checkbox and checkbox.isChecked():
                    selected_ids.append(checkbox.property("distributor_id"))
        
        if not selected_ids:
            QMessageBox.warning(self, "No Selection", "Please select at least one distributor to delete.")
            return
        
        count = len(selected_ids)
        reply = QMessageBox.question(
            self, "Confirm Delete",
            f"Are you sure you want to delete {count} distributor(s)?\nAll associated data will be removed.",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            session = db_manager.get_session()
            try:
                for distributor_id in selected_ids:
                    distributor = session.query(Distributor).get(distributor_id)
                    if distributor:
                        session.delete(distributor)
                session.commit()
                self.load_distributors()
                QMessageBox.information(self, "Success", f"{count} distributor(s) deleted successfully.")
            except Exception as e:
                session.rollback()
                QMessageBox.critical(self, "Error", f"Error deleting distributors: {str(e)}")
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
        
        self.purchase_rate_input = QLineEdit()
        self.purchase_rate_input.setPlaceholderText("0.00")
        layout.addRow("Purchase Rate*:", self.purchase_rate_input)
        
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
                self.purchase_rate_input.setText(str(distributor.purchase_rate))
        finally:
            session.close()
    
    def save(self):
        """Save distributor."""
        name = self.name_input.text().strip()
        purchase_rate_text = self.purchase_rate_input.text().strip()
        
        if not name:
            QMessageBox.warning(self, "Validation Error", "Name is required.")
            return
        
        try:
            purchase_rate = float(purchase_rate_text) if purchase_rate_text else 0.0
        except ValueError:
            QMessageBox.warning(self, "Validation Error", "Purchase Rate must be a valid number.")
            return
        
        if purchase_rate < 0:
            QMessageBox.warning(self, "Validation Error", "Purchase Rate cannot be negative.")
            return
        
        session = db_manager.get_session()
        try:
            if self.distributor_id:
                # Update existing
                distributor = session.query(Distributor).get(self.distributor_id)
                if distributor:
                    distributor.name = name
                    distributor.purchase_rate = purchase_rate
            else:
                # Create new - generate display_id
                first_letter = name[0].upper() if name else 'D'
                # Find highest number for this letter
                existing = session.query(Distributor).filter(
                    Distributor.display_id.like(f"{first_letter}%")
                ).all()
                max_num = 0
                for dist in existing:
                    if dist.display_id and len(dist.display_id) > 1:
                        try:
                            num = int(dist.display_id[1:])
                            max_num = max(max_num, num)
                        except ValueError:
                            pass
                display_id = f"{first_letter}{max_num + 1:03d}"
                
                distributor = Distributor(
                    name=name,
                    purchase_rate=purchase_rate,
                    display_id=display_id
                )
                session.add(distributor)
            
            session.commit()
            self.accept()
        except Exception as e:
            session.rollback()
            QMessageBox.critical(self, "Error", f"Error saving distributor: {str(e)}")
        finally:
            session.close()
