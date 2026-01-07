"""Sale window for ticket-based sales with ranges."""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QComboBox, QTableWidget, QTableWidgetItem, QDateEdit,
    QLineEdit, QMessageBox, QDoubleSpinBox, QHeaderView, QSpinBox
)
from PySide6.QtCore import Qt, QDate, QRegularExpression
from PySide6.QtGui import QRegularExpressionValidator
from database.models import Party, Product
from database.db_manager import db_manager
from services.pricing_service import PricingService
from services.inventory_service import InventoryService


class SaleWindow(QWidget):
    """Window for recording ticket sales with ranges."""

    COL_INDEX = 0
    COL_TICKET = 1
    COL_SERIES = 2
    COL_FROM = 3
    COL_TO = 4
    COL_QTY = 5
    COL_RATE = 6
    COL_AMOUNT = 7
    COL_ACTIONS = 8

    def __init__(self):
        super().__init__()
        self.products = []
        self.session_entries = []  # Store current session entries
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)

        title = QLabel("Sale")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(title)

        # Header: Party and Draw Date
        header_layout = QHBoxLayout()
        header_layout.setSpacing(30)
        header_layout.setContentsMargins(20, 15, 20, 15)

        party_layout = QVBoxLayout()
        party_layout.setSpacing(8)
        party_label = QLabel("Party*:")
        party_label.setStyleSheet("font-size: 13px; font-weight: 600;")
        party_layout.addWidget(party_label)
        self.party_combo = QComboBox()
        self.party_combo.setMinimumWidth(250)
        self.party_combo.setMinimumHeight(40)
        self.party_combo.setStyleSheet("font-size: 12px; padding: 8px;")
        self.party_combo.currentIndexChanged.connect(self.on_party_changed)
        party_layout.addWidget(self.party_combo)
        header_layout.addLayout(party_layout)

        date_layout = QVBoxLayout()
        date_layout.setSpacing(8)
        date_label = QLabel("Draw Date*:")
        date_label.setStyleSheet("font-size: 13px; font-weight: 600;")
        date_layout.addWidget(date_label)
        self.date_edit = QDateEdit()
        self.date_edit.setDate(QDate.currentDate())
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setMinimumWidth(150)
        self.date_edit.setMinimumHeight(40)
        self.date_edit.setStyleSheet("font-size: 12px; padding: 8px;")
        self.date_edit.installEventFilter(self)  # Install event filter for Enter key
        date_layout.addWidget(self.date_edit)
        header_layout.addLayout(date_layout)

        header_layout.addStretch()
        layout.addLayout(header_layout)

        # Instructions
        instructions = QLabel("F9: Clear Entries | F10: Save | Enter on date to start adding entries")
        instructions.setStyleSheet("color: #666; font-size: 10px; font-style: italic;")
        layout.addWidget(instructions)

        # Sale entries table
        self.table = QTableWidget()
        self.table.setColumnCount(9)
        self.table.setHorizontalHeaderLabels([
            "#", "Ticket", "Series", "From No.", "To No.", "Qty", "Rate", "Amount", ""
        ])
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Fixed)
        header.setSectionResizeMode(self.COL_TICKET, QHeaderView.Stretch)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        layout.addWidget(self.table)

        # Totals
        totals_layout = QHBoxLayout()
        totals_layout.addStretch()
        self.total_qty_label = QLabel("Total Qty: 0")
        totals_layout.addWidget(self.total_qty_label)
        totals_layout.addSpacing(20)
        totals_layout.addWidget(QLabel("Total Amount:"))
        self.total_amount_label = QLabel("₹ 0.00")
        self.total_amount_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #FF9800;")
        totals_layout.addWidget(self.total_amount_label)
        layout.addLayout(totals_layout)

        # Footer buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        clear_btn = QPushButton("Clear")
        clear_btn.clicked.connect(self.clear_form)
        save_btn = QPushButton("Save Sale")
        save_btn.setStyleSheet("background-color: #FF9800; color: white; padding: 8px 16px;")
        save_btn.clicked.connect(self.save_sale)
        button_layout.addWidget(clear_btn)
        button_layout.addWidget(save_btn)
        layout.addLayout(button_layout)

    def refresh_data(self):
        """Load parties and tickets (products)."""
        session = db_manager.get_session()
        try:
            # Parties
            self.party_combo.clear()
            for party in session.query(Party).all():
                self.party_combo.addItem(party.name, party.id)

            # Products (Tickets)
            self.products = session.query(Product).all()
        finally:
            session.close()

        # Restore session entries if they exist
        if self.session_entries:
            self.restore_session_entries()
        
        # Install event filter on self to catch F9/F10 globally (after all widgets created)
        self.installEventFilter(self)
        
        # Auto-focus first field
        self.party_combo.setFocus()

    def add_row(self):
        row = self.table.rowCount()
        self.table.insertRow(row)

        # Column: #
        idx_item = QTableWidgetItem(str(row + 1))
        idx_item.setTextAlignment(Qt.AlignCenter)
        self.table.setItem(row, self.COL_INDEX, idx_item)

        # Column: Ticket (Product)
        ticket_combo = QComboBox()
        for p in self.products:
            ticket_combo.addItem(p.name, p.id)
        ticket_combo.currentIndexChanged.connect(lambda _=None, r=row: self.on_ticket_changed(r))
        self.table.setCellWidget(row, self.COL_TICKET, ticket_combo)

        # Column: Series (digits + letter, auto uppercase)
        series_edit = QLineEdit()
        validator = QRegularExpressionValidator(QRegularExpression(r"^\d+[A-Za-z]$"))
        series_edit.setValidator(validator)
        series_edit.textChanged.connect(lambda _=None, r=row: self.on_series_changed(r))
        self.table.setCellWidget(row, self.COL_SERIES, series_edit)

        # Columns: From No. / To No.
        from_spin = QSpinBox()
        from_spin.setRange(0, 999999)
        to_spin = QSpinBox()
        to_spin.setRange(0, 999999)
        to_spin.setKeyboardTracking(False)  # Only update on edit finish
        from_spin.valueChanged.connect(lambda _=None, r=row: self.on_range_changed(r))
        to_spin.valueChanged.connect(lambda _=None, r=row: self.on_to_changed(r))
        to_spin.installEventFilter(self)
        self.table.setCellWidget(row, self.COL_FROM, from_spin)
        self.table.setCellWidget(row, self.COL_TO, to_spin)

        # Column: Qty (read-only)
        qty_item = QTableWidgetItem("0")
        qty_item.setFlags(qty_item.flags() & ~Qt.ItemIsEditable)
        qty_item.setTextAlignment(Qt.AlignCenter)
        self.table.setItem(row, self.COL_QTY, qty_item)

        # Column: Rate (auto from party+ticket, editable)
        rate_spin = QDoubleSpinBox()
        rate_spin.setRange(0.00, 999999)
        rate_spin.setDecimals(2)
        rate_spin.valueChanged.connect(lambda _=None, r=row: self.recalc_row_amount(r))
        rate_spin.installEventFilter(self)  # Install event filter for Enter key
        self.table.setCellWidget(row, self.COL_RATE, rate_spin)

        # Column: Amount (read-only)
        amt_item = QTableWidgetItem("₹ 0.00")
        amt_item.setFlags(amt_item.flags() & ~Qt.ItemIsEditable)
        amt_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.table.setItem(row, self.COL_AMOUNT, amt_item)

        # Column: Actions (Remove)
        rm_btn = QPushButton("Remove")
        rm_btn.clicked.connect(lambda _=None, r=row: self.remove_row(r))
        self.table.setCellWidget(row, self.COL_ACTIONS, rm_btn)

        # Initialize rate based on current party and ticket
        self.on_ticket_changed(row)

    def on_series_changed(self, row):
        edit = self.table.cellWidget(row, self.COL_SERIES)
        if not edit:
            return
        text = edit.text()
        if text:
            # Auto uppercase letters
            upper = ''.join([ch.upper() if ch.isalpha() else ch for ch in text])
            if upper != text:
                old_block = edit.blockSignals(True)
                edit.setText(upper)
                edit.blockSignals(old_block)

    def on_to_changed(self, row):
        """Handle To No. changes with smart auto-completion."""
        from_spin = self.table.cellWidget(row, self.COL_FROM)
        to_spin = self.table.cellWidget(row, self.COL_TO)
        if not (from_spin and to_spin):
            return
        
        from_val = from_spin.value()
        to_val = to_spin.value()
        
        # Smart auto-completion: if to_val is shorter than from_val, auto-complete
        if from_val > 0 and to_val > 0:
            from_str = str(from_val)
            to_str = str(to_val)
            
            # If to_val has fewer digits, auto-complete from from_val
            if len(to_str) < len(from_str):
                # Replace last N digits of from_val with to_val
                prefix = from_str[:-len(to_str)]
                completed = int(prefix + to_str)
                if completed != to_val:
                    to_spin.blockSignals(True)
                    to_spin.setValue(completed)
                    to_spin.blockSignals(False)
        
        self.on_range_changed(row)
    
    def on_range_changed(self, row):
        from_spin = self.table.cellWidget(row, self.COL_FROM)
        to_spin = self.table.cellWidget(row, self.COL_TO)
        qty_item = self.table.item(row, self.COL_QTY)
        ticket_combo = self.table.cellWidget(row, self.COL_TICKET)
        if not (from_spin and to_spin and qty_item and ticket_combo):
            return
        f = from_spin.value()
        t = to_spin.value()
        base_qty = t - f + 1 if t >= f and f > 0 and t > 0 else 0
        
        # Extract ticket multiplier from ticket name (e.g., M5 -> 5, D10 -> 10, E200 -> 200)
        ticket_name = ticket_combo.currentText()
        multiplier = self.extract_ticket_multiplier(ticket_name)
        
        qty = base_qty * multiplier
        qty_item.setText(str(qty))
        self.recalc_row_amount(row)
    
    def extract_ticket_multiplier(self, ticket_name):
        """Extract numeric multiplier from ticket name (e.g., 'M5' -> 5, 'D10' -> 10)."""
        import re
        match = re.search(r'\d+', ticket_name)
        return int(match.group()) if match else 1
    
    def is_row_empty(self, row):
        """Check if a row is completely empty (no data entered)."""
        ticket_combo = self.table.cellWidget(row, self.COL_TICKET)
        from_spin = self.table.cellWidget(row, self.COL_FROM)
        to_spin = self.table.cellWidget(row, self.COL_TO)
        
        # Row is empty if ticket is not selected and from/to are both 0
        ticket_selected = ticket_combo and ticket_combo.currentData() is not None
        has_range = from_spin and to_spin and (from_spin.value() > 0 or to_spin.value() > 0)
        
        return not ticket_selected and not has_range

    def on_ticket_changed(self, row):
        # When ticket or party changes, auto-populate rate
        ticket_combo = self.table.cellWidget(row, self.COL_TICKET)
        rate_spin = self.table.cellWidget(row, self.COL_RATE)
        party_id = self.party_combo.currentData()
        if ticket_combo is None or rate_spin is None or not party_id:
            return
        product_id = ticket_combo.currentData()
        if product_id:
            rate = PricingService.get_sale_rate(party_id, product_id)
            old = rate_spin.blockSignals(True)
            rate_spin.setValue(float(rate) if rate is not None else 0.0)
            rate_spin.blockSignals(old)
        # Recalculate quantity with new ticket multiplier
        self.on_range_changed(row)
        self.recalc_row_amount(row)

    def recalc_row_amount(self, row):
        qty_item = self.table.item(row, self.COL_QTY)
        rate_spin = self.table.cellWidget(row, self.COL_RATE)
        amt_item = self.table.item(row, self.COL_AMOUNT)
        if not (qty_item and rate_spin and amt_item):
            return
        try:
            qty = int(qty_item.text())
        except ValueError:
            qty = 0
        amount = qty * rate_spin.value()
        amt_item.setText(f"₹ {amount:,.2f}")
        self.update_totals()

    def remove_row(self, row):
        if row < 0 or row >= self.table.rowCount():
            return
        self.table.removeRow(row)
        # Renumber indexes
        for r in range(self.table.rowCount()):
            item = self.table.item(r, self.COL_INDEX)
            if item:
                item.setText(str(r + 1))
        self.update_totals()

    def update_totals(self):
        total_qty = 0
        total_amount = 0.0
        for r in range(self.table.rowCount()):
            qty_item = self.table.item(r, self.COL_QTY)
            amt_item = self.table.item(r, self.COL_AMOUNT)
            if qty_item:
                try:
                    total_qty += int(qty_item.text())
                except ValueError:
                    pass
            if amt_item:
                txt = amt_item.text().replace("₹", "").replace(",", "").strip()
                try:
                    total_amount += float(txt)
                except ValueError:
                    pass
        self.total_qty_label.setText(f"Total Qty: {total_qty}")
        self.total_amount_label.setText(f"₹ {total_amount:,.2f}")

    def on_party_changed(self):
        # Refresh rate for all rows based on new party
        for r in range(self.table.rowCount()):
            self.on_ticket_changed(r)

    def validate_row(self, row):
        ticket_combo = self.table.cellWidget(row, self.COL_TICKET)
        series_edit = self.table.cellWidget(row, self.COL_SERIES)
        from_spin = self.table.cellWidget(row, self.COL_FROM)
        to_spin = self.table.cellWidget(row, self.COL_TO)
        rate_spin = self.table.cellWidget(row, self.COL_RATE)

        if ticket_combo is None or ticket_combo.currentData() is None:
            return False, "Please select a ticket."
        # Series can be blank - skip validation
        if from_spin is None or to_spin is None:
            return False, "From/To numbers are required."
        if to_spin.value() < from_spin.value() or from_spin.value() <= 0:
            return False, "Invalid range: To No. must be >= From No., both > 0."
        if rate_spin is None or rate_spin.value() <= 0:
            return False, "Rate must be greater than 0."
        return True, None

    def save_current_session(self):
        """Save current table entries to session storage."""
        self.session_entries = []
        for r in range(self.table.rowCount()):
            ticket_combo = self.table.cellWidget(r, self.COL_TICKET)
            series_edit = self.table.cellWidget(r, self.COL_SERIES)
            from_spin = self.table.cellWidget(r, self.COL_FROM)
            to_spin = self.table.cellWidget(r, self.COL_TO)
            rate_spin = self.table.cellWidget(r, self.COL_RATE)
            
            if ticket_combo and series_edit and from_spin and to_spin and rate_spin:
                entry = {
                    'ticket_id': ticket_combo.currentData(),
                    'series': series_edit.text(),
                    'from_no': from_spin.value(),
                    'to_no': to_spin.value(),
                    'rate': rate_spin.value()
                }
                self.session_entries.append(entry)
    
    def restore_session_entries(self):
        """Restore session entries to table."""
        self.table.setRowCount(0)
        for entry in self.session_entries:
            row = self.table.rowCount()
            self.add_row()
            
            # Restore values
            ticket_combo = self.table.cellWidget(row, self.COL_TICKET)
            series_edit = self.table.cellWidget(row, self.COL_SERIES)
            from_spin = self.table.cellWidget(row, self.COL_FROM)
            to_spin = self.table.cellWidget(row, self.COL_TO)
            rate_spin = self.table.cellWidget(row, self.COL_RATE)
            
            if ticket_combo:
                idx = ticket_combo.findData(entry['ticket_id'])
                if idx >= 0:
                    ticket_combo.setCurrentIndex(idx)
            if series_edit:
                series_edit.setText(entry['series'])
            if from_spin:
                from_spin.setValue(entry['from_no'])
            if to_spin:
                to_spin.setValue(entry['to_no'])
            if rate_spin:
                rate_spin.setValue(entry['rate'])
        
        self.update_totals()
    
    def clear_session(self):
        """Clear session entries (F9 handler)."""
        self.session_entries = []
        self.table.setRowCount(0)
        self.update_totals()
        self.party_combo.setFocus()
    
    def save_sale(self):
        if not self.party_combo.currentData():
            QMessageBox.warning(self, "Validation Error", "Please select a party.")
            return
        if self.table.rowCount() == 0:
            QMessageBox.warning(self, "Validation Error", "Please add at least one entry.")
            return

        items = []
        notes_rows = []
        for r in range(self.table.rowCount()):
            # Skip empty rows
            if self.is_row_empty(r):
                continue
                
            ok, err = self.validate_row(r)
            if not ok:
                QMessageBox.warning(self, "Validation Error", f"Row {r+1}: {err}")
                return
            ticket_combo = self.table.cellWidget(r, self.COL_TICKET)
            series_edit = self.table.cellWidget(r, self.COL_SERIES)
            from_spin = self.table.cellWidget(r, self.COL_FROM)
            to_spin = self.table.cellWidget(r, self.COL_TO)
            rate_spin = self.table.cellWidget(r, self.COL_RATE)
            qty_item = self.table.item(r, self.COL_QTY)

            qty = int(qty_item.text()) if qty_item else 0
            items.append({
                'product_id': ticket_combo.currentData(),
                'quantity': qty,
                'rate': float(rate_spin.value())
            })

            notes_rows.append(
                f"{ticket_combo.currentText()} | Series {series_edit.text()} | {from_spin.value()}-{to_spin.value()} | Qty {qty} @ {rate_spin.value():.2f}"
            )
        
        # Check if we have any valid entries after skipping empty rows
        if not items:
            QMessageBox.warning(self, "Validation Error", "Please add at least one valid entry.")
            return

        party_id = self.party_combo.currentData()
        sale_date = self.date_edit.date().toPython()
        notes = "\n".join(notes_rows) if notes_rows else None

        success, message, _sid = InventoryService.create_sale(
            party_id, sale_date, items, None, notes
        )
        if success:
            QMessageBox.information(self, "Success", f"Sale saved successfully!\n{message}")
            self.session_entries = []  # Clear session after successful save
            self.clear_form()
        else:
            QMessageBox.critical(self, "Error", message)

    def clear_form(self):
        self.date_edit.setDate(QDate.currentDate())
        self.table.setRowCount(0)
        self.update_totals()
        self.party_combo.setFocus()
    
    def keyPressEvent(self, event):
        """Handle Enter key to move between fields."""
        from PySide6.QtGui import QKeyEvent
        
        if event.key() in (Qt.Key_Return, Qt.Key_Enter):
            # Move to next focusable widget
            self.focusNextChild()
            event.accept()
        else:
            super().keyPressEvent(event)
    
    def eventFilter(self, obj, event):
        """Filter events to handle Enter on To spinbox, Rate spinbox, date edit, and F9/F10 globally."""
        from PySide6.QtCore import QEvent
        from PySide6.QtGui import QKeyEvent
        
        # Handle F9 and F10 globally (regardless of which widget has focus)
        if event.type() == QEvent.KeyPress:
            if event.key() == Qt.Key_F9:
                self.save_current_session()
                self.clear_session()
                return True
            elif event.key() == Qt.Key_F10:
                self.save_sale()
                return True
        
        # Check if it's Enter key on date edit when table is empty
        if obj == self.date_edit and event.type() == QEvent.KeyPress:
            if event.key() in (Qt.Key_Return, Qt.Key_Enter) and self.table.rowCount() == 0:
                self.add_row()
                ticket_combo = self.table.cellWidget(0, self.COL_TICKET)
                if ticket_combo:
                    ticket_combo.setFocus()
                return True
        
        # Check if it's Enter key on Rate spinbox
        if event.type() == QEvent.KeyPress:
            key_event = event
            if key_event.key() in (Qt.Key_Return, Qt.Key_Enter):
                # Find which row this rate spinbox belongs to
                for r in range(self.table.rowCount()):
                    rate_spin = self.table.cellWidget(r, self.COL_RATE)
                    if obj == rate_spin:
                        # Interpret the current value
                        rate_spin.interpretText()
                        
                        # Validate current row
                        ok, err = self.validate_row(r)
                        if ok:
                            # Create new row and focus ticket
                            self.add_row()
                            next_ticket = self.table.cellWidget(r + 1, self.COL_TICKET)
                            if next_ticket:
                                next_ticket.setFocus()
                        else:
                            # Show validation error
                            QMessageBox.warning(self, "Validation Error", f"Row {r+1}: {err}")
                        
                        return True
        
        # Check if it's Enter key on To spinbox
        if event.type() == QEvent.KeyPress:
            key_event = event
            if key_event.key() in (Qt.Key_Return, Qt.Key_Enter):
                # Find which row this spinbox belongs to
                for r in range(self.table.rowCount()):
                    to_spin = self.table.cellWidget(r, self.COL_TO)
                    if obj == to_spin:
                        # Interpret the current value from line edit
                        to_spin.interpretText()
                        
                        # Move focus to rate spinbox in same row
                        rate_spin = self.table.cellWidget(r, self.COL_RATE)
                        if rate_spin:
                            rate_spin.setFocus()
                            rate_spin.selectAll()
                        
                        return True
        
        return super().eventFilter(obj, event)
    
    def keyPressEvent(self, event):
        """Handle Enter key to move between fields."""
        from PySide6.QtGui import QKeyEvent
        if event.key() in (Qt.Key_Return, Qt.Key_Enter):
            # Move to next focusable widget
            self.focusNextChild()
            event.accept()
        else:
            super().keyPressEvent(event)
