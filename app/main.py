from fastapi import FastAPI
from app.api import auth, users, products, cart, orders
from app.db import models
from app.db.database import engine


# models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="E-Commerce Order and Inventory API")

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(products.router, prefix="/products", tags=["products"])
app.include_router(cart.router, prefix="/cart", tags=["cart"])
app.include_router(orders.router, prefix="/orders", tags=["orders"])
