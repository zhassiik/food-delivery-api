"""
In-memory data storage.

All data is kept in plain Python dictionaries:
    key   = id of the record
    value = dictionary with the record's fields

Nothing is saved to disk, so all data is reset when the server restarts.
"""

restaurants = {}
menu_items = {}
customers = {}
orders = {}

# The next free id for every resource
id_counters = {
    "restaurants": 1,
    "menu_items": 1,
    "customers": 1,
    "orders": 1,
}


def get_next_id(resource_name):
    """Return a new unique id for the given resource and increase its counter."""
    new_id = id_counters[resource_name]
    id_counters[resource_name] += 1
    return new_id


def load_sample_data():
    """Add a few records so the API can be tried in Swagger right away."""
    # Do not load the sample data twice
    if restaurants:
        return

    sample_restaurants = [
        {"name": "Pizza Palace", "cuisine_type": "Italian", "address": "12 Main Street", "is_open": True},
        {"name": "Sushi Corner", "cuisine_type": "Japanese", "address": "5 Lake Road", "is_open": False},
    ]
    for restaurant in sample_restaurants:
        new_id = get_next_id("restaurants")
        restaurant["id"] = new_id
        restaurants[new_id] = restaurant

    sample_menu_items = [
        {"restaurant_id": 1, "name": "Margherita Pizza", "description": "Tomato, mozzarella, basil", "price": 8.5, "is_available": True},
        {"restaurant_id": 1, "name": "Pepperoni Pizza", "description": "Spicy pepperoni and cheese", "price": 10.0, "is_available": True},
        {"restaurant_id": 1, "name": "Tiramisu", "description": "Classic Italian dessert", "price": 4.5, "is_available": False},
        {"restaurant_id": 2, "name": "California Roll", "description": "Crab, avocado, cucumber", "price": 7.0, "is_available": True},
    ]
    for menu_item in sample_menu_items:
        new_id = get_next_id("menu_items")
        menu_item["id"] = new_id
        menu_items[new_id] = menu_item

    new_id = get_next_id("customers")
    customers[new_id] = {
        "id": new_id,
        "name": "Alex Johnson",
        "phone": "+1-555-0100",
        "address": "100 Elm Street, Apt 4",
    }
