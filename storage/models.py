from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    Boolean,
    DateTime,
    ForeignKey,
)

from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True)

    url = Column(String, nullable=False)
    name = Column(String)

    target_price = Column(Float)
    current_price = Column(Float)

    in_stock = Column(Boolean)

    last_checked = Column(DateTime)
    created_at = Column(DateTime)

    consecutive_failures = Column(Integer, default=0)
    is_broken = Column(Boolean, default=False)

    alert_email = Column(String)

    price_history = relationship(
        "PriceHistory", 
        back_populates="product",
        cascade="all, delete-orphan"
    )

class PriceHistory(Base):
    __tablename__ = "price_history"

    id = Column(Integer, primary_key=True)

    product_id = Column(
        Integer,
        ForeignKey("products.id"),
        nullable=False
    )

    price = Column(Float)
    in_stock = Column(Boolean)

    checked_at = Column(DateTime)

    error = Column(String)

    product = relationship(
        "Product",
        back_populates="price_history"
    )