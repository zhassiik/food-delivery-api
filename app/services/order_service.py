"""
Business logic for orders.

The routers only receive the request and call these functions.
All order rules (validation, total price, status changes) live here.
"""

from decimal import Decimal

from fastapi import HTTPException

from app.models import Customer, MenuItem, Order, OrderItem, Restaurant

# Which status can follow which status.
# Statuses not listed as a "next" status are not allowed (e.g. moving backward).
ALLOWED_TRANSITIONS = {
    "pending": ["confirmed", "cancelled"],
    "confirmed": ["preparing", "cancelled"],
    "preparing": ["delivering"],
    "delivering": ["delivered"],
    "delivered": [],  # final status
    "cancelled": [],  # final status
}

# Orders in these statuses are still "in progress"
ACTIVE_STATUSES = ["pending", "confirmed", "preparing", "delivering"]

# Orders in these statuses can never change again
FINAL_STATUSES = ["delivered", "cancelled"]


# ---------- Reading orders ----------

def get_order(db, order_id):
    """Return the order or raise 404 if it does not exist."""
    order = db.get(Order, order_id)
    if order is None:
        raise HTTPException(status_code=404, detail=f"Order with id {order_id} not found")
    return order


def get_orders(db, status=None, customer_id=None, restaurant_id=None):
    """Return all orders, optionally filtered by status, customer or restaurant."""
    query = db.query(Order)
    if status is not None:
        query = query.filter(Order.status == status.value)
    if customer_id is not None:
        query = query.filter(Order.customer_id == customer_id)
    if restaurant_id is not None:
        query = query.filter(Order.restaurant_id == restaurant_id)
    return query.order_by(Order.id).all()


# ---------- Creating an order ----------

def create_order(db, order_data):
    """Validate a new order, calculate the total price and save it."""

    # 1. The customer must exist
    customer = db.get(Customer, order_data.customer_id)
    if customer is None:
        raise HTTPException(status_code=404, detail=f"Customer with id {order_data.customer_id} not found")

    # 2. The restaurant must exist and be open
    restaurant = db.get(Restaurant, order_data.restaurant_id)
    if restaurant is None:
        raise HTTPException(status_code=404, detail=f"Restaurant with id {order_data.restaurant_id} not found")
    if not restaurant.is_open:
        raise HTTPException(
            status_code=409,
            detail=f"Restaurant '{restaurant.name}' is closed and cannot accept orders",
        )

    # 3. Check every item and calculate the total price
    order_items = []
    used_menu_item_ids = []
    total_price = Decimal("0")

    for item in order_data.items:
        if item.menu_item_id in used_menu_item_ids:
            raise HTTPException(
                status_code=400,
                detail=f"Menu item {item.menu_item_id} appears more than once. Increase its quantity instead",
            )
        used_menu_item_ids.append(item.menu_item_id)

        menu_item = db.get(MenuItem, item.menu_item_id)
        if menu_item is None:
            raise HTTPException(status_code=404, detail=f"Menu item with id {item.menu_item_id} not found")

        # All items must come from the restaurant of this order
        if menu_item.restaurant_id != order_data.restaurant_id:
            raise HTTPException(
                status_code=400,
                detail=(
                    f"Menu item {item.menu_item_id} does not belong to restaurant "
                    f"{order_data.restaurant_id}. All items in one order must be from the same restaurant"
                ),
            )

        if not menu_item.is_available:
            raise HTTPException(status_code=409, detail=f"Menu item '{menu_item.name}' is currently not available")

        subtotal = menu_item.price * item.quantity
        total_price = total_price + subtotal

        # Save name and price now, so the order stays correct if the menu changes later
        order_items.append(OrderItem(
            menu_item_id=menu_item.id,
            name=menu_item.name,
            quantity=item.quantity,
            unit_price=menu_item.price,
            subtotal=subtotal,
        ))

    # 4. Use the customer's address if no delivery address was given
    delivery_address = order_data.delivery_address
    if delivery_address is None:
        delivery_address = customer.address

    # 5. Save the order and its items in ONE transaction, with status "pending"
    order = Order(
        customer_id=customer.id,
        restaurant_id=restaurant.id,
        total_price=total_price,
        delivery_address=delivery_address,
        status="pending",
        items=order_items,
    )
    db.add(order)
    db.commit()
    db.refresh(order)
    return order


# ---------- Changing the status ----------

def change_order_status(db, order_id, new_status):
    """Move an order to a new status if the transition is allowed."""
    order = get_order(db, order_id)
    current_status = order.status
    new_status = new_status.value  # Enum -> plain string, e.g. "confirmed"

    if current_status in FINAL_STATUSES:
        raise HTTPException(
            status_code=409,
            detail=f"Order {order_id} is already '{current_status}' and can no longer be changed",
        )

    if new_status == current_status:
        raise HTTPException(status_code=409, detail=f"Order {order_id} already has status '{current_status}'")

    if new_status == "cancelled" and current_status in ["preparing", "delivering"]:
        raise HTTPException(
            status_code=409,
            detail=f"Order {order_id} cannot be cancelled because it is already '{current_status}'",
        )

    allowed_next = ALLOWED_TRANSITIONS[current_status]
    if new_status not in allowed_next:
        raise HTTPException(
            status_code=409,
            detail=(
                f"Invalid status transition: '{current_status}' -> '{new_status}'. "
                f"Allowed next statuses: {allowed_next}"
            ),
        )

    order.status = new_status
    db.commit()
    db.refresh(order)
    return order


# ---------- Deleting an order ----------

def delete_order(db, order_id):
    """Delete an order. Only finished (delivered or cancelled) orders can be deleted."""
    order = get_order(db, order_id)
    if order.status in ACTIVE_STATUSES:
        raise HTTPException(
            status_code=409,
            detail=(
                f"Order {order_id} is still active ('{order.status}'). "
                "Only delivered or cancelled orders can be deleted"
            ),
        )
    # Its order items are deleted too (cascade)
    db.delete(order)
    db.commit()


# ---------- Helpers used by other services before deleting ----------

def restaurant_has_active_orders(db, restaurant_id):
    order = (
        db.query(Order)
        .filter(Order.restaurant_id == restaurant_id, Order.status.in_(ACTIVE_STATUSES))
        .first()
    )
    return order is not None


def customer_has_active_orders(db, customer_id):
    order = (
        db.query(Order)
        .filter(Order.customer_id == customer_id, Order.status.in_(ACTIVE_STATUSES))
        .first()
    )
    return order is not None


def menu_item_in_active_order(db, menu_item_id):
    order_item = (
        db.query(OrderItem)
        .join(Order)
        .filter(OrderItem.menu_item_id == menu_item_id, Order.status.in_(ACTIVE_STATUSES))
        .first()
    )
    return order_item is not None
