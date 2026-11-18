from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class CustomerCreate(BaseModel):
    """Data the client sends to create a customer."""

    model_config = ConfigDict(str_strip_whitespace=True)

    name: str = Field(min_length=1, max_length=100, examples=["Maria Lopez"])
    phone: str = Field(min_length=1, max_length=20, examples=["+1-555-0199"])
    address: str = Field(min_length=1, max_length=200, examples=["7 River Street"])


class CustomerUpdate(BaseModel):
    """All fields are optional: only the sent fields are changed."""

    model_config = ConfigDict(str_strip_whitespace=True)

    name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    phone: Optional[str] = Field(default=None, min_length=1, max_length=20)
    address: Optional[str] = Field(default=None, min_length=1, max_length=200)


class CustomerResponse(BaseModel):
    """Data the API returns for a customer."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    phone: str
    address: str
