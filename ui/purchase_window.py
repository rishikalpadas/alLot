"""Purchase window for ticket-based purchases with ranges."""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QComboBox, QTableWidget, QTableWidgetItem, QDateEdit,
    QLineEdit, QMessageBox, QDoubleSpinBox, QHeaderView, QSpinBox
)
from PySide6.QtCore import Qt, QDate, QRegularExpression
from PySide6.QtGui import QRegularExpressionValidator
from database.models import Distributor, Product
from database.db_manager import db_manager
from services.pricing_service import PricingService
from services.inventory_service import InventoryService


class PurchaseWindow(QWidget):
    """Window for recording ticket purchases with ranges."""

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
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)

        title = QLabel("Purchase")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(title)

        # Header: Distributor and Draw Date
        header_layout = QHBoxLayout()

        dist_layout = QVBoxLayout()
        dist_layout.addWidget(QLabel("Distributor*:"))
        self.distributor_combo = QComboBox()
        self.distributor_combo.currentIndexChanged.connect(self.on_distributor_changed)
        dist_layout.addWidget(self.distributor_combo)
        header_layout.addLayout(dist_layout)

        date_layout = QVBoxLayout()
        date_layout.addWidget(QLabel("Draw Date*:"))
        self.date_edit = QDateEdit()
        self.date_edit.setDate(QDate.currentDate())
        self.date_edit.setCalendarPopup(True)
        date_layout.addWidget(self.date_edit)
        header_layout.addLayout(date_layout)

        header_layout.addStretch()
        layout.addLayout(header_layout)

        # Table controls
        controls_layout = QHBoxLayout()
        add_row_btn = QPushButton("Add Row")
        add_row_btn.clicked.connect(self.add_row)
        controls_layout.addWidget(add_row_btn)
        controls_layout.addStretch()
        layout.addLayout(controls_layout)

        # Purchase entries table
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
        self.total_amount_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #2196F3;")
        totals_layout.addWidget(self.total_amount_label)
        layout.addLayout(totals_layout)

        # Footer buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        clear_btn = QPushButton("Clear")
        clear_btn.clicked.connect(self.clear_form)
        save_btn = QPushButton("Save Purchase")
        save_btn.setStyleSheet("background-color: #4CAF50; color: white; padding: 8px 16px;")
        save_btn.clicked.connect(self.save_purchase)
        button_layout.addWidget(clear_btn)
        button_layout.addWidget(save_btn)
        layout.addLayout(button_layout)

    def refresh_data(self):
        """Load distributors and tickets (products)."""
        session = db_manager.get_session()
        try:
            # Distributors
            self.distributor_combo.clear()
            for dist in session.query(Distributor).all():
                self.distributor_combo.addItem(dist.name, dist.id)

            # Products (Tickets)
            self.products = session.query(Product).all()
        finally:
            session.close()

        # Reset table for fresh entry session
        self.table.setRowCount(0)
        self.add_row()
        self.update_totals()

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
        from_spin.valueChanged.connect(lambda _=None, r=row: self.on_range_changed(r))
        to_spin.valueChanged.connect(lambda _=None, r=row: self.on_range_changed(r))
        self.table.setCellWidget(row, self.COL_FROM, from_spin)
        self.table.setCellWidget(row, self.COL_TO, to_spin)

        # Column: Qty (read-only)
        qty_item = QTableWidgetItem("0")
        qty_item.setFlags(qty_item.flags() & ~Qt.ItemIsEditable)
        qty_item.setTextAlignment(Qt.AlignCenter)
        self.table.setItem(row, self.COL_QTY, qty_item)

        # Column: Rate (auto from distributor+ticket, editable)
        rate_spin = QDoubleSpinBox()
        rate_spin.setRange(0.00, 999999)
        rate_spin.setDecimals(2)
        rate_spin.valueChanged.connect(lambda _=None, r=row: self.recalc_row_amount(r))
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

        # Initialize rate based on current distributor and ticket
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

    def on_range_changed(self, row):
        from_spin = self.table.cellWidget(row, self.COL_FROM)
        to_spin = self.table.cellWidget(row, self.COL_TO)
        qty_item = self.table.item(row, self.COL_QTY)
        if not (from_spin and to_spin and qty_item):
            return
        f = from_spin.value()
        t = to_spin.value()
        qty = t - f + 1 if t >= f and f > 0 and t > 0 else 0
        qty_item.setText(str(qty))
        self.recalc_row_amount(row)

    def on_ticket_changed(self, row):
        # When ticket or distributor changes, auto-populate rate
        ticket_combo = self.table.cellWidget(row, self.COL_TICKET)
        rate_spin = self.table.cellWidget(row, self.COL_RATE)
        dist_id = self.distributor_combo.currentData()
        if ticket_combo is None or rate_spin is None or not dist_id:
            return
        product_id = ticket_combo.currentData()
        if product_id:
            rate = PricingService.get_purchase_rate(dist_id, product_id)
            if rate is not None:
                old = rate_spin.blockSignals(True)
                rate_spin.setValue(float(rate))
                rate_spin.blockSignals(old)
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

    def on_distributor_changed(self):
        # Refresh rate for all rows based on new distributor
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
        if series_edit is None or not series_edit.text():
            return False, "Series is required (e.g., 61A)."
        # Validator ensures pattern, re-check for safety
        import re as _re
        if not _re.match(r"^\d+[A-Z]$", series_edit.text()):
            return False, "Series must be digits followed by a letter (e.g., 61A)."
        if from_spin is None or to_spin is None:
            return False, "From/To numbers are required."
        if to_spin.value() < from_spin.value() or from_spin.value() <= 0:
            return False, "Invalid range: To No. must be >= From No., both > 0."
        if rate_spin is None or rate_spin.value() <= 0:
            return False, "Rate must be greater than 0."
        return True, None

    def save_purchase(self):
        if not self.distributor_combo.currentData():
            QMessageBox.warning(self, "Validation Error", "Please select a distributor.")
            return
        if self.table.rowCount() == 0:
            QMessageBox.warning(self, "Validation Error", "Please add at least one entry.")
            return

        items = []
        notes_rows = []
        for r in range(self.table.rowCount()):
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

        distributor_id = self.distributor_combo.currentData()
        purchase_date = self.date_edit.date().toPython()
        notes = "\n".join(notes_rows) if notes_rows else None

        success, message, _pid = InventoryService.create_purchase(
            distributor_id, purchase_date, items, None, notes
        )
        if success:
            QMessageBox.information(self, "Success", f"Purchase saved successfully!\n{message}")
            self.clear_form()
        else:
            QMessageBox.critical(self, "Error", message)

    def clear_form(self):
        self.date_edit.setDate(QDate.currentDate())
        self.table.setRowCount(0)
        self.add_row()
        self.update_totals()
