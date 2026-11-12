from typing import List

from fastapi import APIRouter, HTTPException

from app import storage
from app.schemas.customer import CustomerCreate, CustomerResponse, CustomerUpdate
from app.services import order_service

router = APIRouter(prefix="/customers", tags=["Customers"])


def find_customer(customer_id):
    """Return the customer or raise ee404 if it does not exist."""
    customer = storage.customers.get(customer_id)
    if customer is None:
        raise HTTPException(status_code=404, detail=f"Customer with id {customer_id} not found")
    return customer


def check_phone_is_free(phone, current_customer_id=None):
    """Two customers cannot have the same phone number (409 Conflict)."""
    for customer in storage.customers.values():
        if customer["phone"] == phone and customer["id"] != current_customer_id:
            raise HTTPException(
                status_code=409,
                detail=f"Phone number {phone} is already used by another customer",
            )


@router.post("", response_model=CustomerResponse, status_code=201)
def create_customer(customer_data: CustomerCreate):
    check_phone_is_free(customer_data.phone)

    new_id = storage.get_next_id("customers")
    customer = customer_data.model_dump()
    customer["id"] = new_id
    storage.customers[new_id] = customer
    return customer


@router.get("", response_model=List[CustomerResponse])
def list_customers():
    return list(storage.customers.values())


@router.get("/{customer_id}", response_model=CustomerResponse)
def get_customer(customer_id: int):
    return find_customer(customer_id)


@router.patch("/{customer_id}", response_model=CustomerResponse)
def update_customer(customer_id: int, customer_data: CustomerUpdate):
    customer = find_customer(customer_id)
    changes = customer_data.model_dump(exclude_none=True)

    if "phone" in changes:
        check_phone_is_free(changes["phone"], current_customer_id=customer_id)

    customer.update(changes)
    return customer


@router.delete("/{customer_id}", status_code=204)
def delete_customer(customer_id: int):
    find_customer(customer_id)

    if order_service.customer_has_active_orders(customer_id):
        raise HTTPException(
            status_code=409,
            detail="Cannot delete customer: they have active orders",
        )

    del storage.customers[customer_id]
