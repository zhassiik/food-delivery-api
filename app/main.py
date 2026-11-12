from fastapi import FastAPI

from app import storage
from app.routers import customers, menu_items, orders, restaurants

app = FastAPI(
    title="Food Delivery Service API",
    description="A simple university project: restaurants, menus, customers and orders. "
                "All data is stored in memory.",
    version="1.0.0",
)

# Connect all routers to the application
app.include_router(restaurants.router)
app.include_router(menu_items.router)
app.include_router(customers.router)
app.include_router(orders.router)

# Add a few sample records so Swagger testing is easier
storage.load_sample_data()


@app.get("/", tags=["Root"])
def root():
    return {"message": "Food Delivery Service API is running. Open /docs to test it."}
