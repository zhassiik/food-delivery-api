"""
Add sample data to an EMPTY database, so the API can be tried in Swagger right away.

Run once, after "alembic upgrade head":
    python -m app.seed
"""

from app.database import SessionLocal
from app.models import Customer, MenuItem, Restaurant


def seed():
    db = SessionLocal()
    try:
        # Do not add the sample data twice
        if db.query(Restaurant).first() is not None:
            print("Database already has data, nothing was added.")
            return

        pizza_palace = Restaurant(name="Pizza Palace", cuisine_type="Italian", address="12 Main Street", is_open=True)
        sushi_corner = Restaurant(name="Sushi Corner", cuisine_type="Japanese", address="5 Lake Road", is_open=False)

        # Menu items are linked through the relationship, SQLAlchemy fills in restaurant_id
        pizza_palace.menu_items = [
            MenuItem(name="Margherita Pizza", description="Tomato, mozzarella, basil", price=8.5, is_available=True),
            MenuItem(name="Pepperoni Pizza", description="Spicy pepperoni and cheese", price=10.0, is_available=True),
            MenuItem(name="Tiramisu", description="Classic Italian dessert", price=4.5, is_available=False),
        ]
        sushi_corner.menu_items = [
            MenuItem(name="California Roll", description="Crab, avocado, cucumber", price=7.0, is_available=True),
        ]

        customer = Customer(name="Alex Johnson", phone="+1-555-0100", address="100 Elm Street, Apt 4")

        db.add_all([pizza_palace, sushi_corner, customer])
        db.commit()
        print("Sample data added: 2 restaurants, 4 menu items, 1 customer.")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
