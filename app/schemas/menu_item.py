from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class MenuItemCreate(BaseModel):
    """Data the client sends to add a menu item.

    restaurant_id is not here, because it comes from the URL:
    POST /restaurants/{restaurant_id}/menu-items
    """

    model_config = ConfigDict(str_strip_whitespace=True)

    name: str = Field(min_length=1, max_length=100, examples=["Cheeseburger"])
    description: str = Field(default="", max_length=300, examples=["Beef patty with cheddar"])
    price: float = Field(gt=0, le=10000, examples=[6.5])  # price must be greater than 0
    is_available: bool = True


class MenuItemUpdate(BaseModel):
    """All fields are optional: only the sent fields are changed."""

    model_config = ConfigDict(str_strip_whitespace=True)

    name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    description: Optional[str] = Field(default=None, max_length=300)
    price: Optional[float] = Field(default=None, gt=0, le=10000)
    is_available: Optional[bool] = None


class MenuItemResponse(BaseModel):
    """Data the API returns for a menu item."""

    id: int
    restaurant_id: int
    name: str
    description: str
    price: float
    is_available: bool
