from typing import List, Optional

from fastapi import APIRouter, HTTPException

from app import storage
from app.schemas.menu_item import MenuItemCreate, MenuItemResponse, MenuItemUpdate
from app.services import order_service

# No prefix: this router has two kinds of paths
#   /restaurants/{restaurant_id}/menu-items  -> items of one restaurant
#   /menu-items/{menu_item_id}               -> one specific item
router = APIRouter(tags=["Menu Items"])


def find_menu_item(menu_item_id):
    """Return the menu item or raise 404 if it does not exist."""
    menu_item = storage.menu_items.get(menu_item_id)
    if menu_item is None:
        raise HTTPException(status_code=404, detail=f"Menu item with id {menu_item_id} not found")
    return menu_item


def check_restaurant_exists(restaurant_id):
    if restaurant_id not in storage.restaurants:
        raise HTTPException(status_code=404, detail=f"Restaurant with id {restaurant_id} not found")


@router.post(
    "/restaurants/{restaurant_id}/menu-items",
    response_model=MenuItemResponse,
    status_code=201,
)
def add_menu_item(restaurant_id: int, menu_item_data: MenuItemCreate):
    # A menu item cannot be added to a restaurant that does not exist
    check_restaurant_exists(restaurant_id)

    new_id = storage.get_next_id("menu_items")
    menu_item = menu_item_data.model_dump()
    menu_item["id"] = new_id
    menu_item["restaurant_id"] = restaurant_id
    storage.menu_items[new_id] = menu_item
    return menu_item


@router.get("/restaurants/{restaurant_id}/menu-items", response_model=List[MenuItemResponse])
def list_menu_items(restaurant_id: int, is_available: Optional[bool] = None):
    """List the menu of one restaurant. Optional filter: ?is_available=true"""
    check_restaurant_exists(restaurant_id)

    result = []
    for menu_item in storage.menu_items.values():
        if menu_item["restaurant_id"] != restaurant_id:
            continue
        if is_available is not None and menu_item["is_available"] != is_available:
            continue
        result.append(menu_item)
    return result


@router.get("/menu-items/{menu_item_id}", response_model=MenuItemResponse)
def get_menu_item(menu_item_id: int):
    return find_menu_item(menu_item_id)


@router.patch("/menu-items/{menu_item_id}", response_model=MenuItemResponse)
def update_menu_item(menu_item_id: int, menu_item_data: MenuItemUpdate):
    menu_item = find_menu_item(menu_item_id)
    changes = menu_item_data.model_dump(exclude_none=True)
    menu_item.update(changes)
    return menu_item


@router.delete("/menu-items/{menu_item_id}", status_code=204)
def delete_menu_item(menu_item_id: int):
    find_menu_item(menu_item_id)

    if order_service.menu_item_in_active_order(menu_item_id):
        raise HTTPException(
            status_code=409,
            detail="Cannot delete menu item: it is used in an active order",
        )

    del storage.menu_items[menu_item_id]
