from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QDateEdit, QPushButton, QTableWidget, QTableWidgetItem, QHeaderView
from PySide6.QtCore import QDate, Qt
from database.db_manager import db_manager
from database.models import Distributor, Party, Product, Purchase, Sale
import re


class DateRangeReportDialog(QDialog):
    def __init__(self, parent=None, mode="purchase"):
        super().__init__(parent)
        self.mode = mode  # 'purchase' or 'sale'
        self.setWindowTitle("Purchase Report" if mode == "purchase" else "Sale Report")
        self.resize(900, 500)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        # Date range controls
        top = QHBoxLayout()
        top.setSpacing(10)
        top.addWidget(QLabel("From:"))
        self.from_date = QDateEdit()
        self.from_date.setCalendarPopup(True)
        self.from_date.setDate(QDate.currentDate())
        top.addWidget(self.from_date)
        top.addWidget(QLabel("To:"))
        self.to_date = QDateEdit()
        self.to_date.setCalendarPopup(True)
        self.to_date.setDate(QDate.currentDate())
        top.addWidget(self.to_date)
        top.addStretch()

        self.load_btn = QPushButton("Load")
        self.load_btn.clicked.connect(self.load_report)
        top.addWidget(self.load_btn)
        layout.addLayout(top)

        # Results table
        self.table = QTableWidget()
        self.table.setColumnCount(9)
        self.table.setHorizontalHeaderLabels([
            "Date", "Name", "Ticket", "Series", "From", "To", "Qty", "Rate", "Amount"
        ])
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        layout.addWidget(self.table)

        # Initial load
        self.load_report()

    def parse_entry_line(self, line):
        # Expected format: "<Ticket> | Series <SER> | <from>-<to> | Qty <qty> @ <rate>"
        pattern = r"^(.+?)\s*\|\s*Series\s+(\w*)\s*\|\s*(\d+)-(\d+)\s*\|\s*Qty\s+(\d+)\s*@\s*([\d.]+)"
        m = re.match(pattern, line.strip())
        if not m:
            return None
        ticket, series, from_no, to_no, qty, rate = m.groups()
        qty = int(qty)
        rate = float(rate)
        amount = qty * rate
        return ticket, series, int(from_no), int(to_no), qty, rate, amount

    def load_report(self):
        session = db_manager.get_session()
        self.table.setRowCount(0)
        try:
            from_dt = self.from_date.date().toPython()
            to_dt = self.to_date.date().toPython()
            
            # Extend "to" date to end of day (23:59:59) so it includes the entire day
            from datetime import datetime, time
            from_dt = datetime.combine(from_dt, time.min)
            to_dt = datetime.combine(to_dt, time.max)

            print(f"[Report] Date range: {from_dt} to {to_dt}")
            
            if self.mode == "purchase":
                # First, check ALL purchase records to debug
                all_rows = session.query(Purchase).all()
                print(f"[Report] Total Purchase records in DB: {len(all_rows)}")
                for r in all_rows:
                    print(f"[Report]   - Purchase ID {r.id}: date={r.purchase_date}, distributor={r.distributor.name if r.distributor else 'None'}")
                
                # Now filter by date
                rows = session.query(Purchase).filter(Purchase.purchase_date >= from_dt, Purchase.purchase_date <= to_dt).all()
                print(f"[Report] Filtered Purchase records: {len(rows)}")
            else:
                all_rows = session.query(Sale).all()
                print(f"[Report] Total Sale records in DB: {len(all_rows)}")
                for r in all_rows:
                    print(f"[Report]   - Sale ID {r.id}: date={r.sale_date}, party={r.party.name if r.party else 'None'}")
                
                rows = session.query(Sale).filter(Sale.sale_date >= from_dt, Sale.sale_date <= to_dt).all()
                print(f"[Report] Filtered Sale records: {len(rows)}")

            total_qty = 0
            total_amount = 0.0
            
            for row in rows:
                date_val = row.purchase_date if self.mode == "purchase" else row.sale_date
                name = row.distributor.name if self.mode == "purchase" else row.party.name
                if row.notes:
                    print(f"[Report] Processing notes: {row.notes}")
                    for line in row.notes.splitlines():
                        parsed = self.parse_entry_line(line)
                        if not parsed:
                            print(f"[Report] Failed to parse line: {line}")
                            continue
                        ticket, series, from_no, to_no, qty, rate, amount = parsed
                        total_qty += qty
                        total_amount += amount
                        r = self.table.rowCount()
                        self.table.insertRow(r)
                        self.table.setItem(r, 0, QTableWidgetItem(date_val.strftime("%d-%m-%y")))
                        self.table.setItem(r, 1, QTableWidgetItem(name))
                        self.table.setItem(r, 2, QTableWidgetItem(ticket))
                        self.table.setItem(r, 3, QTableWidgetItem(series))
                        self.table.setItem(r, 4, QTableWidgetItem(str(from_no)))
                        self.table.setItem(r, 5, QTableWidgetItem(str(to_no)))
                        self.table.setItem(r, 6, QTableWidgetItem(str(qty)))
                        self.table.setItem(r, 7, QTableWidgetItem(f"{rate:.2f}"))
                        self.table.setItem(r, 8, QTableWidgetItem(f"{amount:.2f}"))
        finally:
            session.close()
