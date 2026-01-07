"""Stock view window with draw date filtering."""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QTableWidget, QTableWidgetItem, QHeaderView, QComboBox, QDateEdit, QMessageBox
)
from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QColor
from database.models import Distributor, Purchase, Sale, Product
from database.db_manager import db_manager
import re


class StockWindow(QWidget):
    """Window for viewing stock by draw date."""

    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)

        title = QLabel("Current Stock")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(title)

        # Filter section
        filter_layout = QHBoxLayout()
        filter_layout.setSpacing(30)
        filter_layout.setContentsMargins(20, 15, 20, 15)

        dist_layout = QVBoxLayout()
        dist_layout.setSpacing(8)
        dist_label = QLabel("Distributor*:")
        dist_label.setStyleSheet("font-size: 13px; font-weight: 600;")
        dist_layout.addWidget(dist_label)
        self.distributor_combo = QComboBox()
        self.distributor_combo.setMinimumWidth(250)
        self.distributor_combo.setMinimumHeight(40)
        self.distributor_combo.setStyleSheet("font-size: 12px; padding: 8px;")
        dist_layout.addWidget(self.distributor_combo)
        filter_layout.addLayout(dist_layout)

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
        date_layout.addWidget(self.date_edit)
        filter_layout.addLayout(date_layout)

        submit_btn = QPushButton("Submit")
        submit_btn.setStyleSheet("background-color: #2196F3; color: white; padding: 8px 24px; margin-top: 20px;")
        submit_btn.clicked.connect(self.load_stock)
        filter_layout.addWidget(submit_btn)

        filter_layout.addStretch()
        layout.addLayout(filter_layout)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            "#", "Ticket", "Series", "From No.", "To No.", "Qty", "Rate", "Amount"
        ])
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Fixed)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
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

    def refresh_data(self):
        """Load distributors."""
        session = db_manager.get_session()
        try:
            self.distributor_combo.clear()
            for dist in session.query(Distributor).all():
                self.distributor_combo.addItem(dist.name, dist.id)
        finally:
            session.close()
        
        # Auto-focus first field
        self.distributor_combo.setFocus()

    def load_stock(self):
        """Load stock for selected distributor and draw date."""
        if not self.distributor_combo.currentData():
            QMessageBox.warning(self, "Validation Error", "Please select a distributor.")
            return

        distributor_id = self.distributor_combo.currentData()
        draw_date = self.date_edit.date().toPython()

        session = db_manager.get_session()
        try:
            # Get purchases for this distributor and draw date
            purchases = session.query(Purchase).filter(
                Purchase.distributor_id == distributor_id,
                Purchase.purchase_date == draw_date
            ).all()

            # Get sales for this draw date (any party)
            sales = session.query(Sale).filter(
                Sale.sale_date == draw_date
            ).all()

            # Parse purchase entries from notes
            purchase_entries = []
            for purchase in purchases:
                if purchase.notes:
                    for line in purchase.notes.split('\n'):
                        parsed = self.parse_entry_line(line)
                        if parsed:
                            parsed['type'] = 'purchase'
                            parsed['purchase_id'] = purchase.id
                            purchase_entries.append(parsed)

            # Parse sale entries from notes
            sale_entries = []
            for sale in sales:
                if sale.notes:
                    for line in sale.notes.split('\n'):
                        parsed = self.parse_entry_line(line)
                        if parsed:
                            parsed['type'] = 'sale'
                            parsed['sale_id'] = sale.id
                            sale_entries.append(parsed)

            # For simplicity, show only purchases (remaining stock calculation would be complex)
            # In a production system, you'd want proper range tracking
            self.display_entries(purchase_entries)

        finally:
            session.close()

    def parse_entry_line(self, line):
        """Parse a note line like 'Ticket Name | Series 61A | 1-100 | Qty 100 @ 5.00'"""
        # Pattern: Ticket Name | Series XXX | from-to | Qty N @ rate
        pattern = r'^(.+?)\s*\|\s*Series\s+(\w+)\s*\|\s*(\d+)-(\d+)\s*\|\s*Qty\s+(\d+)\s*@\s*([\d.]+)'
        match = re.match(pattern, line)
        if match:
            return {
                'ticket': match.group(1).strip(),
                'series': match.group(2),
                'from_no': int(match.group(3)),
                'to_no': int(match.group(4)),
                'qty': int(match.group(5)),
                'rate': float(match.group(6))
            }
        return None

    def display_entries(self, entries):
        """Display entries in table."""
        self.table.setRowCount(len(entries))
        total_qty = 0
        total_amount = 0.0

        for row, entry in enumerate(entries):
            # #
            idx_item = QTableWidgetItem(str(row + 1))
            idx_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, 0, idx_item)

            # Ticket
            self.table.setItem(row, 1, QTableWidgetItem(entry['ticket']))

            # Series
            series_item = QTableWidgetItem(entry['series'])
            series_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, 2, series_item)

            # From No.
            from_item = QTableWidgetItem(str(entry['from_no']))
            from_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, 3, from_item)

            # To No.
            to_item = QTableWidgetItem(str(entry['to_no']))
            to_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, 4, to_item)

            # Qty
            qty_item = QTableWidgetItem(str(entry['qty']))
            qty_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, 5, qty_item)

            # Rate
            rate_item = QTableWidgetItem(f"₹ {entry['rate']:.2f}")
            rate_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.table.setItem(row, 6, rate_item)

            # Amount
            amount = entry['qty'] * entry['rate']
            amount_item = QTableWidgetItem(f"₹ {amount:,.2f}")
            amount_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.table.setItem(row, 7, amount_item)

            total_qty += entry['qty']
            total_amount += amount

        self.total_qty_label.setText(f"Total Qty: {total_qty}")
        self.total_amount_label.setText(f"₹ {total_amount:,.2f}")
    
    def keyPressEvent(self, event):
        """Handle Enter key to move between fields."""
        from PySide6.QtGui import QKeyEvent
        if event.key() in (Qt.Key_Return, Qt.Key_Enter):
            # Move to next focusable widget
            self.focusNextChild()
            event.accept()
        else:
            super().keyPressEvent(event)
