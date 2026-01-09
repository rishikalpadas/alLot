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

        from_date_layout = QVBoxLayout()
        from_date_layout.setSpacing(8)
        from_date_label = QLabel("From Date*:")
        from_date_label.setStyleSheet("font-size: 13px; font-weight: 600;")
        from_date_layout.addWidget(from_date_label)
        self.from_date_edit = QDateEdit()
        self.from_date_edit.setDate(QDate.currentDate())
        self.from_date_edit.setCalendarPopup(True)
        self.from_date_edit.setMinimumWidth(150)
        self.from_date_edit.setMinimumHeight(40)
        self.from_date_edit.setStyleSheet("font-size: 12px; padding: 8px;")
        from_date_layout.addWidget(self.from_date_edit)
        filter_layout.addLayout(from_date_layout)

        to_date_layout = QVBoxLayout()
        to_date_layout.setSpacing(8)
        to_date_label = QLabel("To Date*:")
        to_date_label.setStyleSheet("font-size: 13px; font-weight: 600;")
        to_date_layout.addWidget(to_date_label)
        self.to_date_edit = QDateEdit()
        self.to_date_edit.setDate(QDate.currentDate())
        self.to_date_edit.setCalendarPopup(True)
        self.to_date_edit.setMinimumWidth(150)
        self.to_date_edit.setMinimumHeight(40)
        self.to_date_edit.setStyleSheet("font-size: 12px; padding: 8px;")
        to_date_layout.addWidget(self.to_date_edit)
        filter_layout.addLayout(to_date_layout)

        self.submit_btn = QPushButton("Submit")
        self.submit_btn.setStyleSheet("background-color: #2196F3; color: white; padding: 8px 24px; margin-top: 20px;")
        self.submit_btn.clicked.connect(self.load_stock)
        filter_layout.addWidget(self.submit_btn)

        filter_layout.addStretch()
        layout.addLayout(filter_layout)
        
        # Connect key press handlers after widgets are created
        self.distributor_combo.installEventFilter(self)
        self.from_date_edit.installEventFilter(self)
        self.to_date_edit.installEventFilter(self)
        self.submit_btn.installEventFilter(self)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(9)
        self.table.setHorizontalHeaderLabels([
            "#", "Distributor", "Ticket", "Series", "From No.", "To No.", "Qty", "Rate", "Amount"
        ])
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Fixed)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
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

        # Set tab order
        self.setTabOrder(self.distributor_combo, self.from_date_edit)
        self.setTabOrder(self.from_date_edit, self.to_date_edit)
        self.setTabOrder(self.to_date_edit, self.submit_btn)

    def refresh_data(self):
        """Load distributors."""
        session = db_manager.get_session()
        try:
            self.distributor_combo.clear()
            self.distributor_combo.addItem("All Distributors", None)
            for dist in session.query(Distributor).all():
                self.distributor_combo.addItem(dist.name, dist.id)
        finally:
            session.close()
        
        # Auto-focus first field
        self.distributor_combo.setFocus()

    def load_stock(self):
        """Load stock for selected distributor and date range."""
        distributor_id = self.distributor_combo.currentData()
        from_date = self.from_date_edit.date().toPython()
        to_date = self.to_date_edit.date().toPython()

        if from_date > to_date:
            QMessageBox.warning(self, "Validation Error", "From Date cannot be after To Date.")
            return

        session = db_manager.get_session()
        try:
            # Get purchases for distributor(s) and date range
            from sqlalchemy import func
            purchase_query = session.query(Purchase).filter(
                func.date(Purchase.purchase_date) >= from_date,
                func.date(Purchase.purchase_date) <= to_date
            )
            
            # If specific distributor selected, filter by it
            if distributor_id is not None:
                purchase_query = purchase_query.filter(Purchase.distributor_id == distributor_id)
            
            purchases = purchase_query.all()

            # Get sales for this date range (any party)
            sales = session.query(Sale).filter(
                func.date(Sale.sale_date) >= from_date,
                func.date(Sale.sale_date) <= to_date
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
                            parsed['distributor_name'] = purchase.distributor.name
                            parsed['purchase_date'] = purchase.purchase_date.date()
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
                            parsed['sale_date'] = sale.sale_date.date()
                            sale_entries.append(parsed)

            # Calculate remaining stock by subtracting sold ranges from purchased ranges
            remaining_stock = self.calculate_remaining_stock(purchase_entries, sale_entries)
            self.display_entries(remaining_stock)

        finally:
            session.close()
    
    def calculate_remaining_stock(self, purchase_entries, sale_entries):
        """Calculate remaining stock by subtracting sold ranges from purchased ranges."""
        # Group purchases by ticket, series, and date
        from collections import defaultdict
        purchase_groups = defaultdict(list)
        
        for entry in purchase_entries:
            key = (entry['ticket'], entry['series'], entry['purchase_date'])
            purchase_groups[key].append(entry)
        
        # Group sales by ticket, series, and date
        sale_groups = defaultdict(list)
        for entry in sale_entries:
            key = (entry['ticket'], entry['series'], entry['sale_date'])
            sale_groups[key].append(entry)
        
        # Calculate remaining stock for each group
        remaining = []
        for key, purchases in purchase_groups.items():
            ticket, series, draw_date = key
            
            # Get all purchased ranges for this group
            purchased_ranges = [(p['from_no'], p['to_no']) for p in purchases]
            
            # Get all sold ranges for this group
            sold_ranges = [(s['from_no'], s['to_no']) for s in sale_groups.get(key, [])]
            
            # Calculate remaining ranges
            available_ranges = self._subtract_ranges(purchased_ranges, sold_ranges)
            
            # Create entries for each remaining range
            for from_no, to_no in available_ranges:
                qty = to_no - from_no + 1
                # Use the first purchase entry as template
                template = purchases[0]
                remaining.append({
                    'ticket': ticket,
                    'series': series,
                    'from_no': from_no,
                    'to_no': to_no,
                    'qty': qty,
                    'rate': template['rate'],
                    'distributor_name': template['distributor_name']
                })
        
        return remaining
    
    def _subtract_ranges(self, purchased_ranges, sold_ranges):
        """Calculate remaining available ranges by subtracting sold ranges from purchased ranges."""
        if not sold_ranges:
            return purchased_ranges
        
        # Merge overlapping purchased ranges
        merged_purchased = self._merge_ranges(purchased_ranges)
        # Merge overlapping sold ranges
        merged_sold = self._merge_ranges(sold_ranges)
        
        remaining = []
        for p_from, p_to in merged_purchased:
            current_ranges = [(p_from, p_to)]
            
            # Subtract each sold range from current ranges
            for s_from, s_to in merged_sold:
                new_ranges = []
                for c_from, c_to in current_ranges:
                    # Check for overlap
                    if s_to < c_from or s_from > c_to:
                        # No overlap, keep the range
                        new_ranges.append((c_from, c_to))
                    else:
                        # There's overlap, split the range
                        if c_from < s_from:
                            new_ranges.append((c_from, s_from - 1))
                        if c_to > s_to:
                            new_ranges.append((s_to + 1, c_to))
                current_ranges = new_ranges
            
            remaining.extend(current_ranges)
        
        # Merge any overlapping resulting ranges
        return self._merge_ranges(remaining)
    
    def _merge_ranges(self, ranges):
        """Merge overlapping or adjacent ranges."""
        if not ranges:
            return []
        
        sorted_ranges = sorted(ranges)
        merged = [sorted_ranges[0]]
        
        for current_from, current_to in sorted_ranges[1:]:
            last_from, last_to = merged[-1]
            if current_from <= last_to + 1:  # Overlapping or adjacent
                merged[-1] = (last_from, max(last_to, current_to))
            else:
                merged.append((current_from, current_to))
        
        return merged

    def parse_entry_line(self, line):
        """Parse a note line like 'Ticket Name | Series 61A | 1-100 | Qty 100 @ 5.00' or 'D10 | Series  | 45450-45499 | Qty 500 @ 6.44'"""
        # Pattern: Ticket Name | Series XXX | from-to | Qty N @ rate
        # Series field can be empty/spaces or contain alphanumeric code
        pattern = r'^(.+?)\s*\|\s*Series\s+(\w*)\s*\|\s*(\d+)-(\d+)\s*\|\s*Qty\s+(\d+)\s*@\s*([\d.]+)'
        match = re.match(pattern, line)
        if match:
            return {
                'ticket': match.group(1).strip(),
                'series': match.group(2) if match.group(2) else '',
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

            # Distributor
            self.table.setItem(row, 1, QTableWidgetItem(entry.get('distributor_name', '')))

            # Ticket
            self.table.setItem(row, 2, QTableWidgetItem(entry['ticket']))

            # Series
            series_item = QTableWidgetItem(entry['series'])
            series_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, 3, series_item)

            # From No.
            from_item = QTableWidgetItem(str(entry['from_no']))
            from_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, 4, from_item)

            # To No.
            to_item = QTableWidgetItem(str(entry['to_no']))
            to_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, 5, to_item)

            # Qty
            qty_item = QTableWidgetItem(str(entry['qty']))
            qty_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, 6, qty_item)

            # Rate
            rate_item = QTableWidgetItem(f"₹ {entry['rate']:.2f}")
            rate_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.table.setItem(row, 7, rate_item)

            # Amount
            amount = entry['qty'] * entry['rate']
            amount_item = QTableWidgetItem(f"₹ {amount:,.2f}")
            amount_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.table.setItem(row, 8, amount_item)

            total_qty += entry['qty']
            total_amount += amount

        self.total_qty_label.setText(f"Total Qty: {total_qty}")
        self.total_amount_label.setText(f"₹ {total_amount:,.2f}")
    
    def eventFilter(self, obj, event):
        """Handle Enter key for combo box and date edits."""
        from PySide6.QtCore import QEvent
        if event.type() == QEvent.KeyPress:
            if event.key() in (Qt.Key_Return, Qt.Key_Enter):
                print(f"DEBUG: Enter key pressed on {obj.__class__.__name__}")
                
                # If on to_date_edit or submit button, trigger submit
                if obj == self.to_date_edit or obj == self.submit_btn:
                    print("DEBUG: Triggering load_stock")
                    self.load_stock()
                    return True
                # Otherwise move to next field
                print("DEBUG: Moving to next field")
                self.focusNextChild()
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
