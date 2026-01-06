"""Inventory and stock management service."""
from datetime import datetime
from sqlalchemy import func
from database.models import Product, StockLedger, Purchase, PurchaseItem, Sale, SaleItem
from database.db_manager import db_manager


class InventoryService:
    """Handles inventory and stock operations."""
    
    @staticmethod
    def get_current_stock(product_id=None):
        """
        Get current stock level(s).
        
        Args:
            product_id: Optional product ID. If None, returns all products.
            
        Returns:
            List of tuples (product, current_quantity) or single tuple if product_id specified
        """
        session = db_manager.get_session()
        try:
            if product_id:
                # Get stock for specific product
                total = session.query(func.sum(StockLedger.quantity_delta)).filter(
                    StockLedger.product_id == product_id
                ).scalar() or 0.0
                
                product = session.query(Product).get(product_id)
                return [(product, total)] if product else []
            else:
                # Get stock for all products
                stock_query = session.query(
                    Product,
                    func.coalesce(func.sum(StockLedger.quantity_delta), 0).label('stock')
                ).outerjoin(StockLedger).group_by(Product.id).all()
                
                return stock_query
        finally:
            session.close()
    
    @staticmethod
    def create_purchase(distributor_id, purchase_date, items, invoice_number=None, notes=None):
        """
        Create a purchase transaction.
        
        Args:
            distributor_id: Distributor ID
            purchase_date: Purchase date
            items: List of dicts with keys: product_id, quantity, rate
            invoice_number: Optional invoice number
            notes: Optional notes
            
        Returns:
            Tuple (success: bool, message: str, purchase_id: int or None)
        """
        session = db_manager.get_session()
        try:
            # Generate purchase number
            last_purchase = session.query(Purchase).order_by(Purchase.id.desc()).first()
            purchase_num = f"PUR{(last_purchase.id + 1):06d}" if last_purchase else "PUR000001"
            
            # Calculate total
            total_amount = sum(item['quantity'] * item['rate'] for item in items)
            
            # Create purchase header
            purchase = Purchase(
                purchase_number=purchase_num,
                distributor_id=distributor_id,
                purchase_date=purchase_date,
                invoice_number=invoice_number,
                total_amount=total_amount,
                notes=notes
            )
            session.add(purchase)
            session.flush()  # Get purchase ID
            
            # Create purchase items and stock ledger entries
            for item in items:
                purchase_item = PurchaseItem(
                    purchase_id=purchase.id,
                    product_id=item['product_id'],
                    quantity=item['quantity'],
                    rate=item['rate'],
                    amount=item['quantity'] * item['rate']
                )
                session.add(purchase_item)
                
                # Add to stock ledger
                stock_entry = StockLedger(
                    product_id=item['product_id'],
                    transaction_type='purchase',
                    transaction_id=purchase.id,
                    quantity_delta=item['quantity']
                )
                session.add(stock_entry)
            
            session.commit()
            return True, "Purchase created successfully", purchase.id
        except Exception as e:
            session.rollback()
            return False, f"Error creating purchase: {str(e)}", None
        finally:
            session.close()
    
    @staticmethod
    def create_sale(party_id, sale_date, items, invoice_number=None, notes=None):
        """
        Create a sale transaction.
        
        Args:
            party_id: Party ID
            sale_date: Sale date
            items: List of dicts with keys: product_id, quantity, rate
            invoice_number: Optional invoice number
            notes: Optional notes
            
        Returns:
            Tuple (success: bool, message: str, sale_id: int or None)
        """
        session = db_manager.get_session()
        try:
            # Check stock availability
            for item in items:
                current_stock = session.query(func.sum(StockLedger.quantity_delta)).filter(
                    StockLedger.product_id == item['product_id']
                ).scalar() or 0.0
                
                if current_stock < item['quantity']:
                    product = session.query(Product).get(item['product_id'])
                    return False, f"Insufficient stock for {product.name}. Available: {current_stock}", None
            
            # Generate sale number
            last_sale = session.query(Sale).order_by(Sale.id.desc()).first()
            sale_num = f"SAL{(last_sale.id + 1):06d}" if last_sale else "SAL000001"
            
            # Calculate total
            total_amount = sum(item['quantity'] * item['rate'] for item in items)
            
            # Create sale header
            sale = Sale(
                sale_number=sale_num,
                party_id=party_id,
                sale_date=sale_date,
                invoice_number=invoice_number,
                total_amount=total_amount,
                notes=notes
            )
            session.add(sale)
            session.flush()  # Get sale ID
            
            # Create sale items and stock ledger entries
            for item in items:
                sale_item = SaleItem(
                    sale_id=sale.id,
                    product_id=item['product_id'],
                    quantity=item['quantity'],
                    rate=item['rate'],
                    amount=item['quantity'] * item['rate']
                )
                session.add(sale_item)
                
                # Deduct from stock ledger
                stock_entry = StockLedger(
                    product_id=item['product_id'],
                    transaction_type='sale',
                    transaction_id=sale.id,
                    quantity_delta=-item['quantity']  # Negative for sale
                )
                session.add(stock_entry)
            
            session.commit()
            return True, "Sale created successfully", sale.id
        except Exception as e:
            session.rollback()
            return False, f"Error creating sale: {str(e)}", None
        finally:
            session.close()
