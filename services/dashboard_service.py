"""Dashboard statistics service."""
from datetime import datetime, timedelta
from sqlalchemy import func, and_
from database.models import Purchase, PurchaseItem, Sale, SaleItem
from database.db_manager import db_manager


class DashboardService:
    """Handles dashboard statistics."""
    
    @staticmethod
    def get_today_stats():
        """Get today's purchase and sale statistics."""
        session = db_manager.get_session()
        try:
            today = datetime.now().date()
            today_start = datetime.combine(today, datetime.min.time())
            today_end = datetime.combine(today, datetime.max.time())
            
            # Today's purchases
            purchase_stats = session.query(
                func.sum(PurchaseItem.quantity),
                func.sum(PurchaseItem.amount)
            ).join(Purchase).filter(
                and_(
                    Purchase.purchase_date >= today_start,
                    Purchase.purchase_date <= today_end
                )
            ).first()
            
            purchase_qty = purchase_stats[0] or 0
            purchase_amount = purchase_stats[1] or 0
            
            # Today's sales
            sale_stats = session.query(
                func.sum(SaleItem.quantity),
                func.sum(SaleItem.amount)
            ).join(Sale).filter(
                and_(
                    Sale.sale_date >= today_start,
                    Sale.sale_date <= today_end
                )
            ).first()
            
            sale_qty = sale_stats[0] or 0
            sale_amount = sale_stats[1] or 0
            
            return {
                'purchase_qty': purchase_qty,
                'purchase_amount': purchase_amount,
                'sale_qty': sale_qty,
                'sale_amount': sale_amount
            }
        finally:
            session.close()
    
    @staticmethod
    def get_month_stats():
        """Get current month's purchase and sale statistics."""
        session = db_manager.get_session()
        try:
            today = datetime.now()
            month_start = datetime(today.year, today.month, 1)
            
            # This month's purchases
            purchase_stats = session.query(
                func.sum(PurchaseItem.quantity),
                func.sum(PurchaseItem.amount)
            ).join(Purchase).filter(
                Purchase.purchase_date >= month_start
            ).first()
            
            purchase_qty = purchase_stats[0] or 0
            purchase_amount = purchase_stats[1] or 0
            
            # This month's sales
            sale_stats = session.query(
                func.sum(SaleItem.quantity),
                func.sum(SaleItem.amount)
            ).join(Sale).filter(
                Sale.sale_date >= month_start
            ).first()
            
            sale_qty = sale_stats[0] or 0
            sale_amount = sale_stats[1] or 0
            
            return {
                'purchase_qty': purchase_qty,
                'purchase_amount': purchase_amount,
                'sale_qty': sale_qty,
                'sale_amount': sale_amount
            }
        finally:
            session.close()
    
    @staticmethod
    def get_monthly_chart_data():
        """Get daily purchase and sale data for current month."""
        session = db_manager.get_session()
        try:
            today = datetime.now()
            month_start = datetime(today.year, today.month, 1)
            
            # Get daily purchase data
            purchase_data = session.query(
                func.date(Purchase.purchase_date).label('date'),
                func.sum(PurchaseItem.quantity).label('quantity'),
                func.sum(PurchaseItem.amount).label('amount')
            ).join(Purchase).filter(
                Purchase.purchase_date >= month_start
            ).group_by(func.date(Purchase.purchase_date)).all()
            
            # Get daily sale data
            sale_data = session.query(
                func.date(Sale.sale_date).label('date'),
                func.sum(SaleItem.quantity).label('quantity'),
                func.sum(SaleItem.amount).label('amount')
            ).join(Sale).filter(
                Sale.sale_date >= month_start
            ).group_by(func.date(Sale.sale_date)).all()
            
            # Convert to dictionaries
            purchase_dict = {str(row.date): {'qty': float(row.quantity), 'amt': float(row.amount)} 
                           for row in purchase_data}
            sale_dict = {str(row.date): {'qty': float(row.quantity), 'amt': float(row.amount)} 
                        for row in sale_data}
            
            # Generate all dates in month up to today
            dates = []
            current = month_start.date()
            while current <= today.date():
                dates.append(current)
                current += timedelta(days=1)
            
            # Build data arrays
            chart_data = {
                'dates': [d.strftime('%d/%m') for d in dates],
                'purchase_qty': [purchase_dict.get(str(d), {}).get('qty', 0) for d in dates],
                'purchase_amt': [purchase_dict.get(str(d), {}).get('amt', 0) for d in dates],
                'sale_qty': [sale_dict.get(str(d), {}).get('qty', 0) for d in dates],
                'sale_amt': [sale_dict.get(str(d), {}).get('amt', 0) for d in dates]
            }
            
            return chart_data
        finally:
            session.close()
