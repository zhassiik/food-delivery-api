from typing import List, Optional

from fastapi import APIRouter

from app.schemas.order import OrderCreate, OrderResponse, OrderStatus, OrderStatusUpdate
from app.services import order_service

router = APIRouter(prefix="/orders", tags=["Orders"])


@router.post("", response_model=OrderResponse, status_code=201)
def create_order(order_data: OrderCreate):
    # All checks and the total price calculation are in order_service
    return order_service.create_order(order_data)


@router.get("", response_model=List[OrderResponse])
def list_orders(
    status: Optional[OrderStatus] = None,
    customer_id: Optional[int] = None,
    restaurant_id: Optional[int] = None,
):
    """List orders. Optional filters: ?status=pending&customer_id=1&restaurant_id=1"""
    return order_service.get_orders(status, customer_id, restaurant_id)


@router.get("/{order_id}", response_model=OrderResponse)
def get_order(order_id: int):
    return order_service.get_order(order_id)


@router.patch("/{order_id}/status", response_model=OrderResponse)
def update_order_status(order_id: int, status_data: OrderStatusUpdate):
    return order_service.change_order_status(order_id, status_data.status)


@router.delete("/{order_id}", status_code=204)
def delete_order(order_id: int):
    order_service.delete_order(order_id)
