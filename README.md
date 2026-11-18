# Food Delivery Service API

A REST API for a food delivery service, built with **FastAPI**, **PostgreSQL** and **SQLAlchemy**.
Restaurants publish menus, customers place orders, and orders move through a
delivery process (`pending → confirmed → preparing → delivering → delivered`).

- **Assignment 5:** REST API with in-memory storage.
- **Assignment 6 (this version):** the in-memory dictionaries are replaced by a **PostgreSQL** database.
  Tables and relationships are defined with **SQLAlchemy** models, and the schema is created by **Alembic** migrations.
  Data now stays saved after the server restarts.

## Team members

| Name | Student ID | Role |
|------|-----------|------|
| Zhassulan Talipbay | 250107072 | Restaurants, menu items, database setup |
| Alibek Yesay | 250107048 | Customers, orders, order service, migrations |

## Technologies

- Python 3.9+
- FastAPI: web framework and Swagger UI
- Pydantic v2: request and response validation
- PostgreSQL: database
- SQLAlchemy 2.0: ORM (Python classes ↔ database tables)
- Alembic: database migrations
- psycopg2: PostgreSQL driver
- python-dotenv: reads settings from the `.env` file
- Uvicorn: development server

## Project structure

```
food-delivery-api/
├── app/
│   ├── main.py                 # creates the FastAPI app and connects routers
│   ├── database.py             # engine, session, Base, get_db() dependency
│   ├── seed.py                 # optional sample data (python -m app.seed)
│   ├── models/                 # SQLAlchemy models = database tables
│   │   ├── restaurant.py
│   │   ├── menu_item.py
│   │   ├── customer.py
│   │   └── order.py            # Order and OrderItem
│   ├── schemas/                # Pydantic models (Create / Update / Response)
│   │   ├── restaurant.py
│   │   ├── menu_item.py
│   │   ├── customer.py
│   │   └── order.py
│   ├── routers/                # HTTP endpoints (only receive requests, call services)
│   │   ├── restaurants.py
│   │   ├── menu_items.py
│   │   ├── customers.py
│   │   └── orders.py
│   └── services/               # business logic + database operations
│       ├── restaurant_service.py
│       ├── menu_item_service.py
│       ├── customer_service.py
│       └── order_service.py
├── alembic/
│   ├── env.py                  # reads DATABASE_URL, uses our models
│   └── versions/               # migration files
├── alembic.ini
├── .env.example                # example database settings
├── requirements.txt
└── README.md
```

**Layers:** `routers` (HTTP) → `schemas` (validation) → `services` (business rules) → `models` (database tables).

## Database design

```
restaurants 1 ──< menu_items          (menu_items.restaurant_id)
restaurants 1 ──< orders              (orders.restaurant_id)
customers   1 ──< orders              (orders.customer_id)
orders      1 ──< order_items         (order_items.order_id)
menu_items  1 ──< order_items         (order_items.menu_item_id)
```

All five relationships are **one-to-many**.

| Table | Columns | Constraints |
|-------|---------|-------------|
| `restaurants` | id, name, cuisine_type, address, is_open | PK id, all NOT NULL |
| `menu_items` | id, restaurant_id, name, description, price `NUMERIC(10,2)`, is_available | FK → restaurants (ON DELETE CASCADE), `CHECK price > 0` |
| `customers` | id, name, phone, address | `UNIQUE phone` |
| `orders` | id, customer_id, restaurant_id, total_price `NUMERIC(10,2)`, delivery_address, status, created_at | FK → customers, FK → restaurants (ON DELETE RESTRICT), `CHECK status IN (...)`, `CHECK total_price >= 0` |
| `order_items` | id, order_id, menu_item_id, name, quantity, unit_price, subtotal | FK → orders (ON DELETE CASCADE), FK → menu_items (ON DELETE SET NULL), `CHECK quantity >= 1`, `UNIQUE (order_id, menu_item_id)` |

Design decisions:
- **`NUMERIC(10,2)` for money:** stores prices exactly (a `float` can give 8.4999…).
- **`order_items` stores name and price:** an old order does not change if the menu changes later.
- **ON DELETE rules:**
  - deleting a restaurant deletes its menu items (`CASCADE`);
  - deleting an order deletes its items (`CASCADE`);
  - a customer or restaurant that still has orders cannot be deleted (`RESTRICT`);
  - deleting a menu item keeps old orders but sets their `menu_item_id` to `NULL` (`SET NULL`).
- Rules are checked twice: first in the service (clear error message for the client), then by the database itself (protection against bad data).

## Setup and run

### 1. Install PostgreSQL
- **macOS:** install [Postgres.app](https://postgresapp.com/) and click **Initialize**. User = your Mac username, no password, port 5432.
- **Windows:** install PostgreSQL from [postgresql.org/download](https://www.postgresql.org/download/). User `postgres`, with the password you choose in the installer.

### 2. Create the database
In `psql` (or pgAdmin):
```sql
CREATE DATABASE food_delivery;
```

### 3. Install Python packages
```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 4. Configure the connection
```bash
cp .env.example .env            # Windows: copy .env.example .env
```
Edit `.env`:
```
DATABASE_URL=postgresql+psycopg2://USER:PASSWORD@localhost:5432/food_delivery
```
Examples: `postgresql+psycopg2://postgres:mypassword@localhost:5432/food_delivery` (Windows),
or `postgresql+psycopg2://yourmacname@localhost:5432/food_delivery` (Postgres.app, no password).
The `.env` file is in `.gitignore`, so passwords are never pushed to GitHub.

### 5. Create the tables with Alembic
```bash
alembic upgrade head
```

### 6. (Optional) Add sample data
```bash
python -m app.seed
```

### 7. Start the server
```bash
uvicorn app.main:app --reload
```
Open **http://127.0.0.1:8000/docs**.

## Migrations (Alembic)

| Command | What it does |
|---------|--------------|
| `alembic upgrade head` | Apply all migrations (create/update tables) |
| `alembic downgrade base` | Undo all migrations (drop tables) |
| `alembic current` | Show which migration the database is on |
| `alembic history` | List all migrations |
| `alembic revision --autogenerate -m "message"` | Create a new migration after changing a model |

The migration file `alembic/versions/f99239699c96_create_tables.py` creates all five tables
with their keys, constraints and indexes. Running `alembic downgrade base` and then `alembic upgrade head`
recreates the whole schema from zero.

## Endpoint summary

| Method | Path | Description | Success |
|--------|------|-------------|---------|
| POST | `/restaurants` | Create a restaurant | 201 |
| GET | `/restaurants` | List restaurants (`?cuisine_type=`, `?is_open=`) | 200 |
| GET | `/restaurants/{restaurant_id}` | Get one restaurant | 200 |
| PATCH | `/restaurants/{restaurant_id}` | Update a restaurant | 200 |
| DELETE | `/restaurants/{restaurant_id}` | Delete a restaurant (and its menu) | 204 |
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
- `409 Conflict`: conflicts with the current state (closed restaurant, unavailable item, invalid status transition, deleting something that still has orders, duplicate phone number).
- `422 Unprocessable Entity`: Pydantic validation error (empty name, price ≤ 0, quantity < 1, unknown status, etc.).

**Restaurants and menu items**
- Name, cuisine type and address cannot be empty. Price must be greater than 0.
- A menu item can only be added to an existing restaurant.
- A restaurant with orders cannot be deleted. Close it instead with `PATCH {"is_open": false}`. Deleting a restaurant without orders also deletes its menu items.
- A menu item used in an active order cannot be deleted.

**Customers**
- Name, phone and address cannot be empty. The phone number must be unique.
- A customer with orders cannot be deleted. Delete their finished orders first.

**Orders**
- The customer must exist. The restaurant must exist and be open.
- At least one item. Quantity at least 1. The same item cannot appear twice.
- Every menu item must exist, be available and belong to the order's restaurant.
- `total_price` is calculated by the server. The client cannot send it (422).
- If `delivery_address` is not given, the customer's address is used.
- New orders start as `pending`. The order and its items are saved in **one transaction**.
- Only `delivered` or `cancelled` orders can be deleted.

**Allowed status transitions**
```
pending    → confirmed | cancelled
confirmed  → preparing | cancelled
preparing  → delivering
delivering → delivered
delivered, cancelled → (final)
```

## Swagger testing scenario

Start with an empty database: `alembic upgrade head`, then `python -m app.seed`.
The sample data contains restaurant 1 (Pizza Palace, open), restaurant 2 (Sushi Corner, closed),
menu items 1–4 (item 3 is unavailable) and customer 1.

| # | Request | Body | Expected |
|---|---------|------|----------|
| 1 | `POST /restaurants` | `{"name": "Burger House", "cuisine_type": "American", "address": "25 Oak Avenue", "is_open": true}` | 201, id 3 |
| 2 | `POST /restaurants/3/menu-items` | `{"name": "Cheeseburger", "description": "Beef patty with cheddar", "price": 6.5}` | 201, id 5 |
| 3 | `POST /restaurants/3/menu-items` | `{"name": "French Fries", "description": "Crispy fries", "price": 2.5}` | 201, id 6 |
| 4 | `POST /restaurants/3/menu-items` | `{"name": "Milkshake", "description": "Vanilla", "price": 3.0}` | 201, id 7 |
| 5 | `POST /restaurants/3/menu-items` | `{"name": "Free", "price": 0}` | 422 |
| 6 | `POST /customers` | `{"name": "Maria Lopez", "phone": "+1-555-0199", "address": "7 River Street"}` | 201, id 2 |
| 7 | `POST /orders` | `{"customer_id": 2, "restaurant_id": 3, "items": [{"menu_item_id": 5, "quantity": 2}, {"menu_item_id": 6, "quantity": 1}]}` | 201, `total_price` 15.5, `pending` |
| 8 | `PATCH /orders/1/status` | `{"status": "confirmed"}`, then `preparing`, `delivering`, `delivered` | 200 each |
| 9 | `PATCH /orders/1/status` | `{"status": "cancelled"}` | 409 |
| 10 | `PATCH /menu-items/7` | `{"is_available": false}` | 200 |
| 11 | `POST /orders` | `{"customer_id": 2, "restaurant_id": 3, "items": [{"menu_item_id": 7, "quantity": 1}]}` | 409, not available |
| 12 | `GET /restaurants/999` | none | 404 |
| 13 | `POST /orders` | `{"customer_id": 2, "restaurant_id": 3, "items": [{"menu_item_id": 6, "quantity": 3}]}` | 201, id 2 |
| 14 | `PATCH /orders/2/status` | `{"status": "cancelled"}` | 200 |
| 15 | `DELETE /restaurants/3` | none | 409, has order history |
| 16 | `POST /orders` to closed restaurant 2 with item 4 | `{"customer_id": 1, "restaurant_id": 2, "items": [{"menu_item_id": 4, "quantity": 1}]}` | 409 |

**Persistence check:** stop the server (Ctrl+C), start it again, and call `GET /orders`.
The orders are still there, because they are stored in PostgreSQL.
