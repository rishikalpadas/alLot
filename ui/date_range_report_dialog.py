from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QDateEdit, QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QComboBox
from PySide6.QtCore import QDate, Qt
from PySide6.QtGui import QPainter, QTextDocument
from PySide6.QtPrintSupport import QPrinter, QPrintDialog
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

        # Date range and filter controls
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
        
        # Distributor/Party dropdown
        filter_label = QLabel("Distributor:" if self.mode == "purchase" else "Party:")
        top.addWidget(filter_label)
        self.filter_combo = QComboBox()
        self.populate_filter_combo()
        top.addWidget(self.filter_combo)
        
        top.addStretch()

        self.load_btn = QPushButton("Load")
        self.load_btn.clicked.connect(self.load_report)
        top.addWidget(self.load_btn)
        
        self.print_btn = QPushButton("Print")
        self.print_btn.clicked.connect(self.print_report)
        top.addWidget(self.print_btn)
        
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

    def populate_filter_combo(self):
        """Load all distributors or parties into the filter dropdown."""
        session = db_manager.get_session()
        try:
            self.filter_combo.clear()
            self.filter_combo.addItem("All " + ("Distributors" if self.mode == "purchase" else "Parties"), None)
            
            if self.mode == "purchase":
                items = session.query(Distributor).order_by(Distributor.name).all()
            else:
                items = session.query(Party).order_by(Party.name).all()
            
            for item in items:
                self.filter_combo.addItem(item.name, item.id)
        finally:
            session.close()

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

            # Get selected distributor/party ID
            selected_id = self.filter_combo.currentData()
            
            if self.mode == "purchase":
                query = session.query(Purchase).filter(Purchase.purchase_date >= from_dt, Purchase.purchase_date <= to_dt)
                if selected_id is not None:
                    query = query.filter(Purchase.distributor_id == selected_id)
                rows = query.all()
            else:
                query = session.query(Sale).filter(Sale.sale_date >= from_dt, Sale.sale_date <= to_dt)
                if selected_id is not None:
                    query = query.filter(Sale.party_id == selected_id)
                rows = query.all()

            total_qty = 0
            total_amount = 0.0
            
            for row in rows:
                date_val = row.purchase_date if self.mode == "purchase" else row.sale_date
                name = row.distributor.name if self.mode == "purchase" else row.party.name
                if row.notes:
                    for line in row.notes.splitlines():
                        parsed = self.parse_entry_line(line)
                        if not parsed:
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

    def print_report(self):
        """Print the current report table using a simple HTML document for correct layout."""
        from PySide6.QtPrintSupport import QPrintDialog
        printer = QPrinter(QPrinter.HighResolution)
        dialog = QPrintDialog(printer, self)

        if dialog.exec() == QDialog.Accepted:
            from_date = self.from_date.date().toString("dd-MM-yyyy")
            to_date = self.to_date.date().toString("dd-MM-yyyy")
            filter_name = self.filter_combo.currentText()
            title = f"{'Purchase' if self.mode == 'purchase' else 'Sale'} Report ({from_date} to {to_date}) - {filter_name}"

            # Build HTML table from current data
            headers = ["Date", "Name", "Ticket", "Series", "From", "To", "Qty", "Rate", "Amount"]
            html = ["<html><head><style>table { border-collapse: collapse; width: 100%; font-size: 10pt; } th, td { border: 1px solid #666; padding: 4px; text-align: left; } th { background: #eee; }</style></head><body>"]
            html.append(f"<h3>{title}</h3>")
            html.append("<table><tr>" + "".join(f"<th>{h}</th>" for h in headers) + "</tr>")
            for row in range(self.table.rowCount()):
                html.append("<tr>")
                for col in range(self.table.columnCount()):
                    item = self.table.item(row, col)
                    text = item.text() if item else ""
                    html.append(f"<td>{text}</td>")
                html.append("</tr>")
            html.append("</table></body></html>")

            doc = QTextDocument()
            doc.setHtml("".join(html))
            doc.print_(printer)
