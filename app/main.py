from fastapi import FastAPI

from app.routers import customers, menu_items, orders, restaurants

app = FastAPI(
    title="Food Delivery Service API",
    description="A simple university project: restaurants, menus, customers and orders. "
                "Data is stored in PostgreSQL using SQLAlchemy; the schema is managed by Alembic.",
    version="2.0.0",
)

# Connect all routers to the application.
# Tables are NOT created here: run "alembic upgrade head" once before starting the server.
app.include_router(restaurants.router)
app.include_router(menu_items.router)
app.include_router(customers.router)
app.include_router(orders.router)


@app.get("/", tags=["Root"])
def root():
    return {"message": "Food Delivery Service API is running. Open /docs to test it."}
@app.get("/health",tags=["Health"]):
def health():
    return {"status:ok"}
