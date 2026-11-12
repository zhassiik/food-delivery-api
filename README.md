# Food Delivery Service API

A simple REST API for a food delivery service, built with **FastAPI** and **Pydantic**.
Restaurants publish menus, customers place orders, and orders move through a
delivery process (`pending → confirmed → preparing → delivering → delivered`).

All data is stored **in memory** (Python dictionaries). There is no database,
so all data is reset every time the server restarts.

## Team members

| Name | Student ID | Role |
|------|-----------|------|
| Zhassulan Talipbay | 250107072 | Restaurants, menu items, storage |
| Alibek Yesay | 250107048 | Customers, orders, order service |

## Technologies

- Python 3.9+
- FastAPI: web framework and Swagger UI
- Pydantic v2: request and response validation
- Uvicorn: development server
- Git: version control

## Workflows

1. **Restaurant and menu management**: create, view, update and delete restaurants;
   add, view, update and delete the menu items of a restaurant.
2. **Customer order creation**: create customers and place orders. The server checks
   the customer, the restaurant and every menu item, calculates the total price and
   sets the status to `pending`.
3. **Order status management and cancellation**: view and filter orders, move an order
   to the next status, and cancel orders that are not yet being prepared.

## Project structure

```
food-delivery-api/
├── app/
│   ├── __init__.py
│   ├── main.py              # creates the FastAPI app and connects routers
│   ├── storage.py           # in-memory dictionaries, id counters, sample data
│   ├── schemas/             # Pydantic models (Create / Update / Response)
│   │   ├── __init__.py
│   │   ├── restaurant.py
│   │   ├── menu_item.py
│   │   ├── customer.py
│   │   └── order.py
│   ├── routers/             # HTTP endpoints
│   │   ├── __init__.py
│   │   ├── restaurants.py
│   │   ├── menu_items.py
│   │   ├── customers.py
│   │   └── orders.py
│   └── services/
│       ├── __init__.py
│       └── order_service.py # order rules: validation, total price, status changes
├── requirements.txt
├── README.md
└── .gitignore
```

## Setup and run

```bash
# 1. (optional) create a virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 2. install dependencies
pip install -r requirements.txt

# 3. start the server
uvicorn app.main:app --reload
```

Open **http://127.0.0.1:8000/docs** to see Swagger UI.

## Endpoint summary

| Method | Path | Description | Success |
|--------|------|-------------|---------|
| POST | `/restaurants` | Create a restaurant | 201 |
| GET | `/restaurants` | List restaurants (`?cuisine_type=`, `?is_open=`) | 200 |
| GET | `/restaurants/{restaurant_id}` | Get one restaurant | 200 |
| PATCH | `/restaurants/{restaurant_id}` | Update a restaurant | 200 |
| DELETE | `/restaurants/{restaurant_id}` | Delete a restaurant and its menu | 204 |
| POST | `/restaurants/{restaurant_id}/menu-items` | Add a menu item to a restaurant | 201 |
| GET | `/restaurants/{restaurant_id}/menu-items` | List a restaurant's menu (`?is_available=`) | 200 |
| GET | `/menu-items/{menu_item_id}` | Get one menu item | 200 |
| PATCH | `/menu-items/{menu_item_id}` | Update a menu item | 200 |
| DELETE | `/menu-items/{menu_item_id}` | Delete a menu item | 204 |
| POST | `/customers` | Create a customer | 201 |
| GET | `/customers` | List customers | 200 |
| GET | `/customers/{customer_id}` | Get one customer | 200 |
| PATCH | `/customers/{customer_id}` | Update a customer | 200 |
| DELETE | `/customers/{customer_id}` | Delete a customer | 204 |
| POST | `/orders` | Create an order | 201 |
| GET | `/orders` | List orders (`?status=`, `?customer_id=`, `?restaurant_id=`) | 200 |
| GET | `/orders/{order_id}` | Get one order | 200 |
| PATCH | `/orders/{order_id}/status` | Change the order status | 200 |
| DELETE | `/orders/{order_id}` | Delete a finished order | 204 |

## Business rules

**Status codes**
- `404 Not Found`: the resource does not exist.
- `400 Bad Request`: invalid business operation (item from another restaurant, duplicate item in one order).
- `409 Conflict`: the operation conflicts with the current state (closed restaurant, unavailable item, invalid status transition, deleting something used by an active order, duplicate phone number).
- `422 Unprocessable Entity`: Pydantic validation error (empty name, price ≤ 0, quantity < 1, unknown status, etc.).

**Restaurants and menu items**
- Name, cuisine type and address cannot be empty.
- A menu item can only be added to an existing restaurant.
- Price must be greater than 0.
- A restaurant with active orders cannot be deleted. Deleting a restaurant also deletes its menu items.
- A menu item used in an active order cannot be deleted.

**Customers**
- Name, phone and address cannot be empty.
- Two customers cannot have the same phone number (409).
- A customer with active orders cannot be deleted.

**Orders**
- The customer must exist. The restaurant must exist and be open.
- An order must contain at least one item. Quantity must be at least 1.
- Every menu item must exist, be available and belong to the order's restaurant.
- The same menu item cannot appear twice in one order (increase the quantity instead).
- `total_price` is calculated by the server (`price × quantity` for each item). The client cannot send it.
- If `delivery_address` is not given, the customer's address is used.
- A new order always starts with status `pending`.
- The item name and price are saved inside the order, so later menu changes do not change old orders.
- Only `delivered` or `cancelled` orders can be deleted. Active orders must be cancelled first.
- Finished orders are kept as history even if their restaurant, menu item or customer is deleted later.

**Allowed status transitions**

```
pending    → confirmed | cancelled
confirmed  → preparing | cancelled
preparing  → delivering
delivering → delivered
delivered, cancelled → (final, no changes)
```

Moving backward, skipping steps, or cancelling after `preparing` returns `409 Conflict`.

"Active" orders are those with status `pending`, `confirmed`, `preparing` or `delivering`.

## Sample data

On startup the API already contains:

| Type | id | Data |
|------|----|------|
| Restaurant | 1 | Pizza Palace (Italian, **open**) |
| Restaurant | 2 | Sushi Corner (Japanese, **closed**) |
| Menu item | 1 | Margherita Pizza, 8.50, restaurant 1 |
| Menu item | 2 | Pepperoni Pizza, 10.00, restaurant 1 |
| Menu item | 3 | Tiramisu, 4.50, restaurant 1, **not available** |
| Menu item | 4 | California Roll, 7.00, restaurant 2 |
| Customer | 1 | Alex Johnson, 100 Elm Street, Apt 4 |

So new records get these ids: restaurant **3**, menu items **5, 6, 7**, customer **2**, order **1**.

## Swagger testing scenario

Open http://127.0.0.1:8000/docs, click an endpoint → **Try it out** → fill in the body → **Execute**.
Run the steps in this order right after starting the server (the ids below depend on it).

### 1. Create a restaurant: `POST /restaurants` → **201**
```json
{ "name": "Burger House", "cuisine_type": "American", "address": "25 Oak Avenue", "is_open": true }
```
The response has `"id": 3`.

### 2. Add menu items: `POST /restaurants/3/menu-items` → **201** (three times)
```json
{ "name": "Cheeseburger", "description": "Beef patty with cheddar", "price": 6.5 }
```
```json
{ "name": "French Fries", "description": "Crispy fries", "price": 2.5 }
```
```json
{ "name": "Milkshake", "description": "Vanilla", "price": 3.0 }
```
They get ids 5, 6 and 7.
Extra check: `"price": 0` returns **422**. `POST /restaurants/999/menu-items` returns **404**.

### 3. Create a customer: `POST /customers` → **201**
```json
{ "name": "Maria Lopez", "phone": "+1-555-0199", "address": "7 River Street" }
```
The response has `"id": 2`.

### 4. Create an order: `POST /orders` → **201**
```json
{
  "customer_id": 2,
  "restaurant_id": 3,
  "items": [
    { "menu_item_id": 5, "quantity": 2 },
    { "menu_item_id": 6, "quantity": 1 }
  ]
}
```

### 5. Check the calculated total: `GET /orders/1` → **200**
`total_price` is **15.5** (6.5 × 2 + 2.5 × 1), `status` is `"pending"`, and
`delivery_address` is `"7 River Street"` (taken from the customer).

### 6. Move the order through valid statuses: `PATCH /orders/1/status` → **200** each
```json
{ "status": "confirmed" }
```
```json
{ "status": "preparing" }
```
```json
{ "status": "delivering" }
```
```json
{ "status": "delivered" }
```

### 7. Try an invalid status transition: `PATCH /orders/1/status` → **409**
```json
{ "status": "cancelled" }
```
Response: `"Order 1 is already 'delivered' and can no longer be changed"`.

### 8. Try ordering an unavailable item
First make the milkshake unavailable with `PATCH /menu-items/7` → **200**
```json
{ "is_available": false }
```
Then `POST /orders` → **409** (`"Menu item 'Milkshake' is currently not available"`)
```json
{ "customer_id": 2, "restaurant_id": 3, "items": [ { "menu_item_id": 7, "quantity": 1 } ] }
```

### 9. Try a nonexistent resource
- `GET /restaurants/999` → **404**
- `POST /orders` with an unknown customer → **404**
```json
{ "customer_id": 999, "restaurant_id": 3, "items": [ { "menu_item_id": 5, "quantity": 1 } ] }
```

### 10. Cancel an eligible order
Create a new order with `POST /orders` → **201** (gets id 2, status `pending`)
```json
{ "customer_id": 2, "restaurant_id": 3, "items": [ { "menu_item_id": 6, "quantity": 3 } ], "delivery_address": "Office, 9 Hill Road" }
```
Cancel it with `PATCH /orders/2/status` → **200**
```json
{ "status": "cancelled" }
```

### More checks you can try

| Request | Expected |
|---------|----------|
| `POST /orders` to closed restaurant 2 with item 4 | 409 |
| `POST /orders` to restaurant 3 with item 1 (belongs to restaurant 1) | 400 |
| `POST /orders` with `"items": []` | 422 |
| `POST /orders` with `"quantity": 0` | 422 |
| `POST /orders` with an extra `"total_price": 1` | 422 |
| `PATCH /orders/{id}/status` from `pending` to `delivered` | 409 |
| Create a new order for restaurant 3, then `DELETE /restaurants/3` while it is still `pending` | 409 |
| `GET /orders?status=pending` | 200, only pending orders |
| `GET /restaurants?is_open=true` | 200, only open restaurants |
