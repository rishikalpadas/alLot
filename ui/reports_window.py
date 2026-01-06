"""Reports window."""
from datetime import datetime, timedelta
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
                               QComboBox, QDateEdit, QMessageBox, QFileDialog, QGroupBox, QFormLayout)
from PySide6.QtCore import Qt, QDate
from services.report_service import ReportService
from database.models import Distributor, Party
from database.db_manager import db_manager


class ReportsWindow(QWidget):
    """Window for generating reports."""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        title = QLabel("Reports")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(title)
        
        # Purchase Report Section
        purchase_group = QGroupBox("Purchase Report")
        purchase_layout = QFormLayout()
        
        self.purchase_start_date = QDateEdit()
        self.purchase_start_date.setDate(QDate.currentDate().addMonths(-1))
        self.purchase_start_date.setCalendarPopup(True)
        purchase_layout.addRow("From Date:", self.purchase_start_date)
        
        self.purchase_end_date = QDateEdit()
        self.purchase_end_date.setDate(QDate.currentDate())
        self.purchase_end_date.setCalendarPopup(True)
        purchase_layout.addRow("To Date:", self.purchase_end_date)
        
        self.purchase_distributor_combo = QComboBox()
        self.purchase_distributor_combo.addItem("All Distributors", None)
        purchase_layout.addRow("Distributor:", self.purchase_distributor_combo)
        
        purchase_btn_layout = QHBoxLayout()
        purchase_pdf_btn = QPushButton("Generate PDF")
        purchase_pdf_btn.clicked.connect(self.generate_purchase_pdf)
        purchase_btn_layout.addWidget(purchase_pdf_btn)
        purchase_btn_layout.addStretch()
        
        purchase_layout.addRow("", purchase_btn_layout)
        purchase_group.setLayout(purchase_layout)
        layout.addWidget(purchase_group)
        
        # Sale Report Section
        sale_group = QGroupBox("Sale Report")
        sale_layout = QFormLayout()
        
        self.sale_start_date = QDateEdit()
        self.sale_start_date.setDate(QDate.currentDate().addMonths(-1))
        self.sale_start_date.setCalendarPopup(True)
        sale_layout.addRow("From Date:", self.sale_start_date)
        
        self.sale_end_date = QDateEdit()
        self.sale_end_date.setDate(QDate.currentDate())
        self.sale_end_date.setCalendarPopup(True)
        sale_layout.addRow("To Date:", self.sale_end_date)
        
        self.sale_party_combo = QComboBox()
        self.sale_party_combo.addItem("All Parties", None)
        sale_layout.addRow("Party:", self.sale_party_combo)
        
        sale_btn_layout = QHBoxLayout()
        sale_pdf_btn = QPushButton("Generate PDF")
        sale_pdf_btn.clicked.connect(self.generate_sale_pdf)
        sale_btn_layout.addWidget(sale_pdf_btn)
        sale_btn_layout.addStretch()
        
        sale_layout.addRow("", sale_btn_layout)
        sale_group.setLayout(sale_layout)
        layout.addWidget(sale_group)
        
        layout.addStretch()
        
        # Load distributors and parties
        self.load_filters()
    
    def load_filters(self):
        """Load distributors and parties for filters."""
        session = db_manager.get_session()
        try:
            # Load distributors
            distributors = session.query(Distributor).all()
            for dist in distributors:
                self.purchase_distributor_combo.addItem(dist.name, dist.id)
            
            # Load parties
            parties = session.query(Party).all()
            for party in parties:
                self.sale_party_combo.addItem(party.name, party.id)
        finally:
            session.close()
    
    def generate_purchase_pdf(self):
        """Generate purchase report PDF."""
        start_date = self.purchase_start_date.date().toPython()
        end_date = self.purchase_end_date.date().toPython()
        distributor_id = self.purchase_distributor_combo.currentData()
        
        # Get report data
        report_data = ReportService.get_purchase_report(start_date, end_date, distributor_id)
        
        if not report_data:
            QMessageBox.information(self, "No Data", "No purchase records found for the selected criteria.")
            return
        
        # Ask for save location
        file_name, _ = QFileDialog.getSaveFileName(
            self,
            "Save Purchase Report",
            f"Purchase_Report_{datetime.now().strftime('%Y%m%d')}.pdf",
            "PDF Files (*.pdf)"
        )
        
        if file_name:
            try:
                ReportService.generate_purchase_pdf(report_data, file_name, start_date, end_date)
                QMessageBox.information(self, "Success", f"Purchase report generated successfully!\n\nSaved to: {file_name}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error generating PDF: {str(e)}")
    
    def generate_sale_pdf(self):
        """Generate sale report PDF."""
        start_date = self.sale_start_date.date().toPython()
        end_date = self.sale_end_date.date().toPython()
        party_id = self.sale_party_combo.currentData()
        
        # Get report data
        report_data = ReportService.get_sale_report(start_date, end_date, party_id)
        
        if not report_data:
            QMessageBox.information(self, "No Data", "No sale records found for the selected criteria.")
            return
        
        # Ask for save location
        file_name, _ = QFileDialog.getSaveFileName(
            self,
            "Save Sale Report",
            f"Sale_Report_{datetime.now().strftime('%Y%m%d')}.pdf",
            "PDF Files (*.pdf)"
        )
        
        if file_name:
            try:
                ReportService.generate_sale_pdf(report_data, file_name, start_date, end_date)
                QMessageBox.information(self, "Success", f"Sale report generated successfully!\n\nSaved to: {file_name}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error generating PDF: {str(e)}")
