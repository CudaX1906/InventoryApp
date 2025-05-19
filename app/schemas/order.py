from pydantic import BaseModel
from typing import List

class OrderItem(BaseModel):
    product_id: int
    quantity: int
    price: float

    class Config:
        orm_mode = True

class OrderOut(BaseModel):
    id: int
    total: float
    status: str
    items: List[OrderItem]

    class Config:
        orm_mode = True
