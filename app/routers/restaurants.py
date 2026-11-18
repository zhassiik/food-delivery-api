from typing import List, Optional

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.restaurant import RestaurantCreate, RestaurantResponse, RestaurantUpdate
from app.services import restaurant_service

router = APIRouter(prefix="/restaurants", tags=["Restaurants"])


@router.post("", response_model=RestaurantResponse, status_code=201)
def create_restaurant(restaurant_data: RestaurantCreate, db: Session = Depends(get_db)):
    return restaurant_service.create_restaurant(db, restaurant_data)


@router.get("", response_model=List[RestaurantResponse])
def list_restaurants(
    cuisine_type: Optional[str] = None,
    is_open: Optional[bool] = None,
    db: Session = Depends(get_db),
):
    """List restaurants. Optional filters: ?cuisine_type=Italian&is_open=true"""
    return restaurant_service.list_restaurants(db, cuisine_type, is_open)


@router.get("/{restaurant_id}", response_model=RestaurantResponse)
def get_restaurant(restaurant_id: int, db: Session = Depends(get_db)):
    return restaurant_service.get_restaurant(db, restaurant_id)


@router.patch("/{restaurant_id}", response_model=RestaurantResponse)
def update_restaurant(restaurant_id: int, restaurant_data: RestaurantUpdate, db: Session = Depends(get_db)):
    return restaurant_service.update_restaurant(db, restaurant_id, restaurant_data)


@router.delete("/{restaurant_id}", status_code=204)
def delete_restaurant(restaurant_id: int, db: Session = Depends(get_db)):
    restaurant_service.delete_restaurant(db, restaurant_id)
