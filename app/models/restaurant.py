from sqlalchemy import Boolean, Column, Integer, String
from sqlalchemy.orm import relationship

from app.database import Base


class Restaurant(Base):
    __tablename__ = "restaurants"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    cuisine_type = Column(String(50), nullable=False)
    address = Column(String(200), nullable=False)
    is_open = Column(Boolean, nullable=False, default=True)

    # One restaurant has many menu items (one-to-many).
    # Deleting a restaurant also deletes its menu items.
    menu_items = relationship("MenuItem", back_populates="restaurant", cascade="all, delete-orphan")

    # One restaurant has many orders (one-to-many)
    orders = relationship("Order", back_populates="restaurant")
