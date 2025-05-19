from pydantic import BaseModel

class CartItem(BaseModel):
    id: int
    product_id: int
    quantity: int

    class Config:
        orm_mode = True

class CartItemCreate(BaseModel):
    product_id: int
    quantity: int
