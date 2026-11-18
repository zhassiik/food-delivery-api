"""Business logic for customers."""

from fastapi import HTTPException

from app.models import Customer
from app.services import order_service


def get_customer(db, customer_id):
    """Return the customer or raise 404 if it does not exist."""
    customer = db.get(Customer, customer_id)
    if customer is None:
        raise HTTPException(status_code=404, detail=f"Customer with id {customer_id} not found")
    return customer


def check_phone_is_free(db, phone, current_customer_id=None):
    """Two customers cannot have the same phone number (409 Conflict)."""
    other = db.query(Customer).filter(Customer.phone == phone).first()
    if other is not None and other.id != current_customer_id:
        raise HTTPException(status_code=409, detail=f"Phone number {phone} is already used by another customer")


def list_customers(db):
    return db.query(Customer).order_by(Customer.id).all()


def create_customer(db, customer_data):
    check_phone_is_free(db, customer_data.phone)

    customer = Customer(**customer_data.model_dump())
    db.add(customer)
    db.commit()
    db.refresh(customer)
    return customer


def update_customer(db, customer_id, customer_data):
    customer = get_customer(db, customer_id)
    changes = customer_data.model_dump(exclude_none=True)

    if "phone" in changes:
        check_phone_is_free(db, changes["phone"], current_customer_id=customer_id)

    for field, value in changes.items():
        setattr(customer, field, value)
    db.commit()
    db.refresh(customer)
    return customer


def delete_customer(db, customer_id):
    customer = get_customer(db, customer_id)

    if order_service.customer_has_active_orders(db, customer_id):
        raise HTTPException(status_code=409, detail="Cannot delete customer: they have active orders")

    if customer.orders:
        raise HTTPException(
            status_code=409,
            detail="Cannot delete customer: they have order history. Delete their finished orders first",
        )

    db.delete(customer)
    db.commit()
