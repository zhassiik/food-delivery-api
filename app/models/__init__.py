# Import every model here, so SQLAlchemy and Alembic know about all tables
from app.models.customer import Customer
from app.models.menu_item import MenuItem
from app.models.order import Order, OrderItem
from app.models.restaurant import Restaurant
