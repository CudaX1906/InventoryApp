import random
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import SessionLocal
from app.db.models import Order, OrderItem, Cart, CartItem, Product, PaymentLog
from app.schemas.order import OrderOut
from app.api.users import get_current_user

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=OrderOut, status_code=201)
def create_order(db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    cart = db.query(Cart).filter(Cart.user_id == current_user.id).first()
    print(cart.items)
    if not cart or not cart.items:
        raise HTTPException(status_code=400, detail="Cart is empty")
    
    for item in cart.items:
        print(item)
        product = db.query(Product).filter(Product.id == item.product_id).first()
        if item.quantity > product.stock:
            raise HTTPException(status_code=400, detail=f"Insufficient stock for {product.name}")
    total_amount = 0
    order = Order(user_id=current_user.id, status="PENDING", total=0)
    db.add(order)
    db.flush()  # get order.id
    for item in cart.items:
        product = db.query(Product).with_for_update().filter(Product.id == item.product_id).first()

        product.stock -= item.quantity
        order_item = OrderItem(order_id=order.id, product_id=item.product_id,
                               quantity=item.quantity, price=product.price)
        total_amount += product.price * item.quantity
        db.add(order_item)
        db.delete(item)  
    order.total = total_amount
    db.commit()
    db.refresh(order)
    
    success = random.choice([True, True, True, False]) 
    payment_log = PaymentLog(order_id=order.id, success=success)
    order.status = "PAID" if success else "FAILED"
    db.add(payment_log)
    db.commit()
    if not success:
        raise HTTPException(status_code=400, detail="Payment failed. Please try again.")
    return order

@router.get("/", response_model=list[OrderOut])
def list_orders(db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    if current_user.is_admin:
        orders = db.query(Order).all()
    else:
        orders = db.query(Order).filter(Order.user_id == current_user.id).all()
    return orders

@router.get("/{order_id}", response_model=OrderOut)
def get_order(order_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    if not current_user.is_admin and order.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    return order
