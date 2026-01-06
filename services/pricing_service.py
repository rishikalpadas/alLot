"""Pricing service for alLot."""
from database.models import DistributorPrice, PartyPrice, Product
from database.db_manager import db_manager


class PricingService:
    """Handles pricing logic for distributors and parties."""
    
    @staticmethod
    def get_purchase_rate(distributor_id, product_id):
        """
        Get purchase rate for a product from a specific distributor.
        
        Args:
            distributor_id: Distributor ID
            product_id: Product ID
            
        Returns:
            Float rate or None if not found
        """
        session = db_manager.get_session()
        try:
            price = session.query(DistributorPrice).filter_by(
                distributor_id=distributor_id,
                product_id=product_id
            ).first()
            
            return price.purchase_rate if price else None
        finally:
            session.close()
    
    @staticmethod
    def get_sale_rate(party_id, product_id):
        """
        Get sale rate for a product to a specific party.
        
        Args:
            party_id: Party ID
            product_id: Product ID
            
        Returns:
            Float rate or None if not found
        """
        session = db_manager.get_session()
        try:
            price = session.query(PartyPrice).filter_by(
                party_id=party_id,
                product_id=product_id
            ).first()
            
            return price.sale_rate if price else None
        finally:
            session.close()
    
    @staticmethod
    def set_distributor_price(distributor_id, product_id, purchase_rate):
        """
        Set or update purchase rate for a distributor-product combination.
        
        Args:
            distributor_id: Distributor ID
            product_id: Product ID
            purchase_rate: Purchase rate
            
        Returns:
            Tuple (success: bool, message: str)
        """
        session = db_manager.get_session()
        try:
            # Check if price entry exists
            price = session.query(DistributorPrice).filter_by(
                distributor_id=distributor_id,
                product_id=product_id
            ).first()
            
            if price:
                # Update existing
                price.purchase_rate = purchase_rate
            else:
                # Create new
                price = DistributorPrice(
                    distributor_id=distributor_id,
                    product_id=product_id,
                    purchase_rate=purchase_rate
                )
                session.add(price)
            
            session.commit()
            return True, "Price updated successfully"
        except Exception as e:
            session.rollback()
            return False, f"Error updating price: {str(e)}"
        finally:
            session.close()
    
    @staticmethod
    def set_party_price(party_id, product_id, sale_rate):
        """
        Set or update sale rate for a party-product combination.
        
        Args:
            party_id: Party ID
            product_id: Product ID
            sale_rate: Sale rate
            
        Returns:
            Tuple (success: bool, message: str)
        """
        session = db_manager.get_session()
        try:
            # Check if price entry exists
            price = session.query(PartyPrice).filter_by(
                party_id=party_id,
                product_id=product_id
            ).first()
            
            if price:
                # Update existing
                price.sale_rate = sale_rate
            else:
                # Create new
                price = PartyPrice(
                    party_id=party_id,
                    product_id=product_id,
                    sale_rate=sale_rate
                )
                session.add(price)
            
            session.commit()
            return True, "Price updated successfully"
        except Exception as e:
            session.rollback()
            return False, f"Error updating price: {str(e)}"
        finally:
            session.close()
    
    @staticmethod
    def get_all_distributor_prices(distributor_id):
        """Get all product prices for a distributor."""
        session = db_manager.get_session()
        try:
            prices = session.query(DistributorPrice, Product).join(Product).filter(
                DistributorPrice.distributor_id == distributor_id
            ).all()
            
            return [(price, product) for price, product in prices]
        finally:
            session.close()
    
    @staticmethod
    def get_all_party_prices(party_id):
        """Get all product prices for a party."""
        session = db_manager.get_session()
        try:
            prices = session.query(PartyPrice, Product).join(Product).filter(
                PartyPrice.party_id == party_id
            ).all()
            
            return [(price, product) for price, product in prices]
        finally:
            session.close()
