from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class RestaurantCreate(BaseModel):
    """Data the client sends to create a restaurant."""

    # Remove spaces at the start/end, so "   " counts as an empty string
    model_config = ConfigDict(str_strip_whitespace=True)

    name: str = Field(min_length=1, max_length=100, examples=["Burger House"])
    cuisine_type: str = Field(min_length=1, max_length=50, examples=["American"])
    address: str = Field(min_length=1, max_length=200, examples=["25 Oak Avenue"])
    is_open: bool = True


class RestaurantUpdate(BaseModel):
    """All fields are optional: only the sent fields are changed."""

    model_config = ConfigDict(str_strip_whitespace=True)

    name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    cuisine_type: Optional[str] = Field(default=None, min_length=1, max_length=50)
    address: Optional[str] = Field(default=None, min_length=1, max_length=200)
    is_open: Optional[bool] = None


class RestaurantResponse(BaseModel):
    """Data the API returns for a restaurant."""

    id: int
    name: str
    cuisine_type: str
    address: str
    is_open: bool
