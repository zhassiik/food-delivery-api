from typing import List, Optional

from fastapi import APIRouter, HTTPException

from app import storage
from app.schemas.restaurant import RestaurantCreate, RestaurantResponse, RestaurantUpdate
from app.services import order_service

router = APIRouter(prefix="/restaurants", tags=["Restaurants"])


def find_restaurant(restaurant_id):
    """Return the restaurant or raise 404 if it does not exist."""
    restaurant = storage.restaurants.get(restaurant_id)
    if restaurant is None:
        raise HTTPException(status_code=404, detail=f"Restaurant with id {restaurant_id} not found")
    return restaurant


@router.post("", response_model=RestaurantResponse, status_code=201)
def create_restaurant(restaurant_data: RestaurantCreate):
    new_id = storage.get_next_id("restaurants")
    restaurant = restaurant_data.model_dump()
    restaurant["id"] = new_id
    storage.restaurants[new_id] = restaurant
    return restaurant


@router.get("", response_model=List[RestaurantResponse])
def list_restaurants(cuisine_type: Optional[str] = None, is_open: Optional[bool] = None):
    """List restaurants. Optional filters: ?cuisine_type=Italian&is_open=true"""
    result = []
    for restaurant in storage.restaurants.values():
        # cuisine filter ignores upper/lower case
        if cuisine_type is not None and restaurant["cuisine_type"].lower() != cuisine_type.lower():
            continue
        if is_open is not None and restaurant["is_open"] != is_open:
            continue
        result.append(restaurant)
    return result


@router.get("/{restaurant_id}", response_model=RestaurantResponse)
def get_restaurant(restaurant_id: int):
    return find_restaurant(restaurant_id)


@router.patch("/{restaurant_id}", response_model=RestaurantResponse)
def update_restaurant(restaurant_id: int, restaurant_data: RestaurantUpdate):
    restaurant = find_restaurant(restaurant_id)
    # Only change the fields the client actually sent
    changes = restaurant_data.model_dump(exclude_none=True)
    restaurant.update(changes)
    return restaurant


@router.delete("/{restaurant_id}", status_code=204)
def delete_restaurant(restaurant_id: int):
    find_restaurant(restaurant_id)

    if order_service.restaurant_has_active_orders(restaurant_id):
        raise HTTPException(
            status_code=409,
            detail="Cannot delete restaurant: it has active orders",
        )

    # Also delete the restaurant's menu items, so no item points to a missing restaurant
    item_ids_to_delete = []
    for menu_item in storage.menu_items.values():
        if menu_item["restaurant_id"] == restaurant_id:
            item_ids_to_delete.append(menu_item["id"])
    for item_id in item_ids_to_delete:
        del storage.menu_items[item_id]

    del storage.restaurants[restaurant_id]
