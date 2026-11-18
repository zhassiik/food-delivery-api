"""Business logic for restaurants."""

from fastapi import HTTPException
from sqlalchemy import func

from app.models import Restaurant
from app.services import order_service


def get_restaurant(db, restaurant_id):
    """Return the restaurant or raise 404 if it does not exist."""
    restaurant = db.get(Restaurant, restaurant_id)
    if restaurant is None:
        raise HTTPException(status_code=404, detail=f"Restaurant with id {restaurant_id} not found")
    return restaurant


def list_restaurants(db, cuisine_type=None, is_open=None):
    query = db.query(Restaurant)
    if cuisine_type is not None:
        # compare in lower case, so "italian" also finds "Italian"
        query = query.filter(func.lower(Restaurant.cuisine_type) == cuisine_type.lower())
    if is_open is not None:
        query = query.filter(Restaurant.is_open == is_open)
    return query.order_by(Restaurant.id).all()


def create_restaurant(db, restaurant_data):
    restaurant = Restaurant(**restaurant_data.model_dump())
    db.add(restaurant)
    db.commit()
    db.refresh(restaurant)  # load the id that PostgreSQL generated
    return restaurant


def update_restaurant(db, restaurant_id, restaurant_data):
    restaurant = get_restaurant(db, restaurant_id)
    # Only change the fields the client actually sent
    changes = restaurant_data.model_dump(exclude_none=True)
    for field, value in changes.items():
        setattr(restaurant, field, value)
    db.commit()
    db.refresh(restaurant)
    return restaurant


def delete_restaurant(db, restaurant_id):
    restaurant = get_restaurant(db, restaurant_id)

    if order_service.restaurant_has_active_orders(db, restaurant_id):
        raise HTTPException(status_code=409, detail="Cannot delete restaurant: it has active orders")

    if restaurant.orders:
        raise HTTPException(
            status_code=409,
            detail="Cannot delete restaurant: it has order history. Set is_open to false instead",
        )

    # Its menu items are deleted too (cascade)
    db.delete(restaurant)
    db.commit()
