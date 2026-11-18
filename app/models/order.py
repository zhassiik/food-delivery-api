from sqlalchemy import (
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import relationship

from app.database import Base


class Order(Base):
    __tablename__ = "orders"
    __table_args__ = (
        # Only these six values are allowed in the status column
        CheckConstraint(
            "status IN ('pending', 'confirmed', 'preparing', 'delivering', 'delivered', 'cancelled')",
            name="ck_orders_status_valid",
        ),
        CheckConstraint("total_price >= 0", name="ck_orders_total_not_negative"),
    )

    id = Column(Integer, primary_key=True)
    # RESTRICT: the database refuses to delete a customer/restaurant that still has orders
    customer_id = Column(Integer, ForeignKey("customers.id", ondelete="RESTRICT"), nullable=False, index=True)
    restaurant_id = Column(Integer, ForeignKey("restaurants.id", ondelete="RESTRICT"), nullable=False, index=True)
    total_price = Column(Numeric(10, 2), nullable=False)
    delivery_address = Column(String(200), nullable=False)
    status = Column(String(20), nullable=False, default="pending")
    # Filled in automatically by PostgreSQL when the order is inserted
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    customer = relationship("Customer", back_populates="orders")
    restaurant = relationship("Restaurant", back_populates="orders")

    # One order has many order items (one-to-many).
    # lazy="selectin" loads the items together with the order.
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan", lazy="selectin")


class OrderItem(Base):
    """One line of an order: which menu item, how many, and the price at the moment of ordering."""

    __tablename__ = "order_items"
    __table_args__ = (
        CheckConstraint("quantity >= 1", name="ck_order_items_quantity_min_1"),
        CheckConstraint("unit_price > 0", name="ck_order_items_unit_price_positive"),
        # The same menu item cannot appear twice in one order
        UniqueConstraint("order_id", "menu_item_id", name="uq_order_items_order_menu_item"),
    )

    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey("orders.id", ondelete="CASCADE"), nullable=False, index=True)
    # SET NULL: if the menu item is deleted later, the old order keeps its name and price
    menu_item_id = Column(Integer, ForeignKey("menu_items.id", ondelete="SET NULL"), nullable=True)
    name = Column(String(100), nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Numeric(10, 2), nullable=False)
    subtotal = Column(Numeric(10, 2), nullable=False)

    order = relationship("Order", back_populates="items")
