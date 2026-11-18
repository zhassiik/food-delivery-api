from typing import List, Optional

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.menu_item import MenuItemCreate, MenuItemResponse, MenuItemUpdate
from app.services import menu_item_service

# No prefix: this router has two kinds of paths
#   /restaurants/{restaurant_id}/menu-items  -> items of one restaurant
#   /menu-items/{menu_item_id}               -> one specific item
router = APIRouter(tags=["Menu Items"])


@router.post(
    "/restaurants/{restaurant_id}/menu-items",
    response_model=MenuItemResponse,
    status_code=201,
)
def add_menu_item(restaurant_id: int, menu_item_data: MenuItemCreate, db: Session = Depends(get_db)):
    return menu_item_service.create_menu_item(db, restaurant_id, menu_item_data)


@router.get("/restaurants/{restaurant_id}/menu-items", response_model=List[MenuItemResponse])
def list_menu_items(restaurant_id: int, is_available: Optional[bool] = None, db: Session = Depends(get_db)):
    """List the menu of one restaurant. Optional filter: ?is_available=true"""
    return menu_item_service.list_menu_items(db, restaurant_id, is_available)


@router.get("/menu-items/{menu_item_id}", response_model=MenuItemResponse)
def get_menu_item(menu_item_id: int, db: Session = Depends(get_db)):
    return menu_item_service.get_menu_item(db, menu_item_id)


@router.patch("/menu-items/{menu_item_id}", response_model=MenuItemResponse)
def update_menu_item(menu_item_id: int, menu_item_data: MenuItemUpdate, db: Session = Depends(get_db)):
    return menu_item_service.update_menu_item(db, menu_item_id, menu_item_data)


@router.delete("/menu-items/{menu_item_id}", status_code=204)
def delete_menu_item(menu_item_id: int, db: Session = Depends(get_db)):
    menu_item_service.delete_menu_item(db, menu_item_id)
