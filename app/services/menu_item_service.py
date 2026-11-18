"""Business logic for menu items."""

from fastapi import HTTPException

from app.models import MenuItem
from app.services import order_service, restaurant_service


def get_menu_item(db, menu_item_id):
    """Return the menu item or raise 404 if it does not exist."""
    menu_item = db.get(MenuItem, menu_item_id)
    if menu_item is None:
        raise HTTPException(status_code=404, detail=f"Menu item with id {menu_item_id} not found")
    return menu_item


def list_menu_items(db, restaurant_id, is_available=None):
    # 404 if the restaurant does not exist
    restaurant_service.get_restaurant(db, restaurant_id)

    query = db.query(MenuItem).filter(MenuItem.restaurant_id == restaurant_id)
    if is_available is not None:
        query = query.filter(MenuItem.is_available == is_available)
    return query.order_by(MenuItem.id).all()


def create_menu_item(db, restaurant_id, menu_item_data):
    # A menu item cannot be added to a restaurant that does not exist
    restaurant_service.get_restaurant(db, restaurant_id)

    menu_item = MenuItem(restaurant_id=restaurant_id, **menu_item_data.model_dump())
    db.add(menu_item)
    db.commit()
    db.refresh(menu_item)
    return menu_item


def update_menu_item(db, menu_item_id, menu_item_data):
    menu_item = get_menu_item(db, menu_item_id)
    changes = menu_item_data.model_dump(exclude_none=True)
    for field, value in changes.items():
        setattr(menu_item, field, value)
    db.commit()
    db.refresh(menu_item)
    return menu_item


def delete_menu_item(db, menu_item_id):
    menu_item = get_menu_item(db, menu_item_id)

    if order_service.menu_item_in_active_order(db, menu_item_id):
        raise HTTPException(status_code=409, detail="Cannot delete menu item: it is used in an active order")

    # Old (finished) orders keep the item's name and price; their menu_item_id becomes NULL
    db.delete(menu_item)
    db.commit()
