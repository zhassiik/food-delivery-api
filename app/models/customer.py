from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from app.database import Base


class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    # unique=True: two customers cannot have the same phone number
    phone = Column(String(20), nullable=False, unique=True)
    address = Column(String(200), nullable=False)

    # One customer has many orders (one-to-many)
    orders = relationship("Order", back_populates="customer")
