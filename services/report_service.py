"""Reporting service for alLot."""
from datetime import datetime
from sqlalchemy import func, and_
from database.models import Purchase, PurchaseItem, Sale, SaleItem, Product, Distributor, Party, StockLedger
from database.db_manager import db_manager
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.enums import TA_CENTER, TA_RIGHT


class ReportService:
    """Handles report generation."""
    
    @staticmethod
    def get_purchase_report(start_date=None, end_date=None, distributor_id=None):
        """
        Get purchase report data.
        
        Args:
            start_date: Optional start date filter
            end_date: Optional end date filter
            distributor_id: Optional distributor filter
            
        Returns:
            List of purchase records with details
        """
        session = db_manager.get_session()
        try:
            query = session.query(Purchase, Distributor).join(Distributor)
            
            if start_date:
                query = query.filter(Purchase.purchase_date >= start_date)
            if end_date:
                query = query.filter(Purchase.purchase_date <= end_date)
            if distributor_id:
                query = query.filter(Purchase.distributor_id == distributor_id)
            
            purchases = query.order_by(Purchase.purchase_date.desc()).all()
            
            result = []
            for purchase, distributor in purchases:
                items = session.query(PurchaseItem, Product).join(Product).filter(
                    PurchaseItem.purchase_id == purchase.id
                ).all()
                
                result.append({
                    'purchase': purchase,
                    'distributor': distributor,
                    'items': items
                })
            
            return result
        finally:
            session.close()
    
    @staticmethod
    def get_sale_report(start_date=None, end_date=None, party_id=None):
        """
        Get sale report data.
        
        Args:
            start_date: Optional start date filter
            end_date: Optional end date filter
            party_id: Optional party filter
            
        Returns:
            List of sale records with details
        """
        session = db_manager.get_session()
        try:
            query = session.query(Sale, Party).join(Party)
            
            if start_date:
                query = query.filter(Sale.sale_date >= start_date)
            if end_date:
                query = query.filter(Sale.sale_date <= end_date)
            if party_id:
                query = query.filter(Sale.party_id == party_id)
            
            sales = query.order_by(Sale.sale_date.desc()).all()
            
            result = []
            for sale, party in sales:
                items = session.query(SaleItem, Product).join(Product).filter(
                    SaleItem.sale_id == sale.id
                ).all()
                
                result.append({
                    'sale': sale,
                    'party': party,
                    'items': items
                })
            
            return result
        finally:
            session.close()
    
    @staticmethod
    def generate_purchase_pdf(report_data, output_path, start_date=None, end_date=None):
        """Generate purchase report PDF."""
        doc = SimpleDocTemplate(output_path, pagesize=A4)
        elements = []
        styles = getSampleStyleSheet()
        
        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            alignment=TA_CENTER,
            spaceAfter=30
        )
        elements.append(Paragraph("alLot - Purchase Report", title_style))
        
        # Date range
        if start_date or end_date:
            date_text = f"Period: {start_date.strftime('%d/%m/%Y') if start_date else 'Start'} to {end_date.strftime('%d/%m/%Y') if end_date else 'End'}"
            elements.append(Paragraph(date_text, styles['Normal']))
        
        elements.append(Spacer(1, 0.3 * inch))
        
        # Summary table
        total_purchases = len(report_data)
        total_amount = sum(item['purchase'].total_amount for item in report_data)
        
        summary_data = [
            ['Total Purchases', str(total_purchases)],
            ['Total Amount', f"₹ {total_amount:,.2f}"]
        ]
        summary_table = Table(summary_data, colWidths=[3 * inch, 2 * inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.lightgrey),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ]))
        elements.append(summary_table)
        elements.append(Spacer(1, 0.3 * inch))
        
        # Detailed table
        table_data = [['Date', 'Purchase #', 'Distributor', 'Items', 'Amount']]
        
        for item in report_data:
            purchase = item['purchase']
            distributor = item['distributor']
            items_count = len(item['items'])
            
            table_data.append([
                purchase.purchase_date.strftime('%d/%m/%Y'),
                purchase.purchase_number,
                distributor.name,
                str(items_count),
                f"₹ {purchase.total_amount:,.2f}"
            ])
        
        detail_table = Table(table_data, colWidths=[1.2 * inch, 1.3 * inch, 2 * inch, 0.8 * inch, 1.2 * inch])
        detail_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ]))
        elements.append(detail_table)
        
        doc.build(elements)
    
    @staticmethod
    def generate_sale_pdf(report_data, output_path, start_date=None, end_date=None):
        """Generate sale report PDF."""
        doc = SimpleDocTemplate(output_path, pagesize=A4)
        elements = []
        styles = getSampleStyleSheet()
        
        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            alignment=TA_CENTER,
            spaceAfter=30
        )
        elements.append(Paragraph("alLot - Sale Report", title_style))
        
        # Date range
        if start_date or end_date:
            date_text = f"Period: {start_date.strftime('%d/%m/%Y') if start_date else 'Start'} to {end_date.strftime('%d/%m/%Y') if end_date else 'End'}"
            elements.append(Paragraph(date_text, styles['Normal']))
        
        elements.append(Spacer(1, 0.3 * inch))
        
        # Summary table
        total_sales = len(report_data)
        total_amount = sum(item['sale'].total_amount for item in report_data)
        
        summary_data = [
            ['Total Sales', str(total_sales)],
            ['Total Amount', f"₹ {total_amount:,.2f}"]
        ]
        summary_table = Table(summary_data, colWidths=[3 * inch, 2 * inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.lightgrey),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ]))
        elements.append(summary_table)
        elements.append(Spacer(1, 0.3 * inch))
        
        # Detailed table
        table_data = [['Date', 'Sale #', 'Party', 'Items', 'Amount']]
        
        for item in report_data:
            sale = item['sale']
            party = item['party']
            items_count = len(item['items'])
            
            table_data.append([
                sale.sale_date.strftime('%d/%m/%Y'),
                sale.sale_number,
                party.name,
                str(items_count),
                f"₹ {sale.total_amount:,.2f}"
            ])
        
        detail_table = Table(table_data, colWidths=[1.2 * inch, 1.3 * inch, 2 * inch, 0.8 * inch, 1.2 * inch])
        detail_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ]))
        elements.append(detail_table)
        
        doc.build(elements)
