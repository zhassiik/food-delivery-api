from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class OrderStatus(str, Enum):
    """All possible statuses of an order."""

    pending = "pending"
    confirmed = "confirmed"
    preparing = "preparing"
    delivering = "delivering"
    delivered = "delivered"
    cancelled = "cancelled"


class OrderItemCreate(BaseModel):
    """One line of a new order: which menu item and how many."""

    menu_item_id: int = Field(examples=[1])
    quantity: int = Field(ge=1, le=100, examples=[2])  # at least 1


class OrderCreate(BaseModel):
    """Data the client sends to create an order.

    total_price and status are NOT accepted from the client:
    the server calculates the total and always starts with "pending".
    extra="forbid" returns 422 if the client sends unknown fields like total_price.
    """

    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    customer_id: int = Field(examples=[1])
    restaurant_id: int = Field(examples=[1])
    items: List[OrderItemCreate] = Field(min_length=1)  # an order cannot be empty
    delivery_address: Optional[str] = Field(default=None, min_length=1, max_length=200)


class OrderStatusUpdate(BaseModel):
    """Body for PATCH /orders/{order_id}/status."""

    status: OrderStatus


class OrderItemResponse(BaseModel):
    """One line of an order, with the price saved at the moment of ordering."""

    menu_item_id: int
    name: str
    quantity: int
    unit_price: float
    subtotal: float


class OrderResponse(BaseModel):
    """Data the API returns for an order."""

    id: int
    customer_id: int
    restaurant_id: int
    items: List[OrderItemResponse]
    total_price: float
    delivery_address: str
    status: OrderStatus
