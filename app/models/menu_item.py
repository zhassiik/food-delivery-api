from sqlalchemy import Boolean, CheckConstraint, Column, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import relationship

from app.database import Base


class MenuItem(Base):
    __tablename__ = "menu_items"
    __table_args__ = (
        # The database itself also refuses a price of 0 or less
        CheckConstraint("price > 0", name="ck_menu_items_price_positive"),
    )

    id = Column(Integer, primary_key=True)
    # Foreign key: every menu item belongs to one restaurant
    restaurant_id = Column(
        Integer,
        ForeignKey("restaurants.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name = Column(String(100), nullable=False)
    description = Column(String(300), nullable=False, default="")
    # Numeric(10, 2) stores money exactly, e.g. 8.50 (float could give 8.4999...)
    price = Column(Numeric(10, 2), nullable=False)
    is_available = Column(Boolean, nullable=False, default=True)

    restaurant = relationship("Restaurant", back_populates="menu_items")
