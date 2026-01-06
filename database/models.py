"""Database models for alLot application."""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class User(Base):
    """Admin user model."""
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)


class Distributor(Base):
    """Distributor/Supplier model."""
    __tablename__ = 'distributors'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    contact_person = Column(String(100))
    phone = Column(String(20))
    email = Column(String(100))
    address = Column(Text)
    created_at = Column(DateTime, default=datetime.now)
    
    # Relationships
    distributor_prices = relationship("DistributorPrice", back_populates="distributor", cascade="all, delete-orphan")
    purchases = relationship("Purchase", back_populates="distributor")


class Party(Base):
    """Customer/Party model."""
    __tablename__ = 'parties'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    contact_person = Column(String(100))
    phone = Column(String(20))
    email = Column(String(100))
    address = Column(Text)
    created_at = Column(DateTime, default=datetime.now)
    
    # Relationships
    party_prices = relationship("PartyPrice", back_populates="party", cascade="all, delete-orphan")
    sales = relationship("Sale", back_populates="party")


class Product(Base):
    """Product model."""
    __tablename__ = 'products'
    
    id = Column(Integer, primary_key=True)
    sku = Column(String(50), unique=True, nullable=False)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    unit = Column(String(20), nullable=False)  # e.g., pcs, kg, ltr
    hsn_code = Column(String(20))
    tax_rate = Column(Float, default=0.0)  # GST/tax percentage
    reorder_level = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.now)
    
    # Relationships
    distributor_prices = relationship("DistributorPrice", back_populates="product", cascade="all, delete-orphan")
    party_prices = relationship("PartyPrice", back_populates="product", cascade="all, delete-orphan")
    stock_ledger_entries = relationship("StockLedger", back_populates="product")


class DistributorPrice(Base):
    """Distributor-specific product pricing."""
    __tablename__ = 'distributor_prices'
    
    id = Column(Integer, primary_key=True)
    distributor_id = Column(Integer, ForeignKey('distributors.id'), nullable=False)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    purchase_rate = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relationships
    distributor = relationship("Distributor", back_populates="distributor_prices")
    product = relationship("Product", back_populates="distributor_prices")


class PartyPrice(Base):
    """Party-specific product pricing."""
    __tablename__ = 'party_prices'
    
    id = Column(Integer, primary_key=True)
    party_id = Column(Integer, ForeignKey('parties.id'), nullable=False)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    sale_rate = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relationships
    party = relationship("Party", back_populates="party_prices")
    product = relationship("Product", back_populates="party_prices")


class Purchase(Base):
    """Purchase transaction header."""
    __tablename__ = 'purchases'
    
    id = Column(Integer, primary_key=True)
    purchase_number = Column(String(50), unique=True, nullable=False)
    distributor_id = Column(Integer, ForeignKey('distributors.id'), nullable=False)
    purchase_date = Column(DateTime, nullable=False)
    invoice_number = Column(String(100))
    total_amount = Column(Float, nullable=False)
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.now)
    
    # Relationships
    distributor = relationship("Distributor", back_populates="purchases")
    items = relationship("PurchaseItem", back_populates="purchase", cascade="all, delete-orphan")


class PurchaseItem(Base):
    """Purchase transaction line item."""
    __tablename__ = 'purchase_items'
    
    id = Column(Integer, primary_key=True)
    purchase_id = Column(Integer, ForeignKey('purchases.id'), nullable=False)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    quantity = Column(Float, nullable=False)
    rate = Column(Float, nullable=False)
    amount = Column(Float, nullable=False)
    
    # Relationships
    purchase = relationship("Purchase", back_populates="items")
    product = relationship("Product")


class Sale(Base):
    """Sale transaction header."""
    __tablename__ = 'sales'
    
    id = Column(Integer, primary_key=True)
    sale_number = Column(String(50), unique=True, nullable=False)
    party_id = Column(Integer, ForeignKey('parties.id'), nullable=False)
    sale_date = Column(DateTime, nullable=False)
    invoice_number = Column(String(100))
    total_amount = Column(Float, nullable=False)
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.now)
    
    # Relationships
    party = relationship("Party", back_populates="sales")
    items = relationship("SaleItem", back_populates="sale", cascade="all, delete-orphan")


class SaleItem(Base):
    """Sale transaction line item."""
    __tablename__ = 'sale_items'
    
    id = Column(Integer, primary_key=True)
    sale_id = Column(Integer, ForeignKey('sales.id'), nullable=False)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    quantity = Column(Float, nullable=False)
    rate = Column(Float, nullable=False)
    amount = Column(Float, nullable=False)
    
    # Relationships
    sale = relationship("Sale", back_populates="items")
    product = relationship("Product")


class StockLedger(Base):
    """Stock movement ledger."""
    __tablename__ = 'stock_ledger'
    
    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    transaction_type = Column(String(20), nullable=False)  # 'purchase' or 'sale'
    transaction_id = Column(Integer, nullable=False)  # ID of purchase or sale
    quantity_delta = Column(Float, nullable=False)  # Positive for purchase, negative for sale
    timestamp = Column(DateTime, default=datetime.now)
    
    # Relationships
    product = relationship("Product", back_populates="stock_ledger_entries")
