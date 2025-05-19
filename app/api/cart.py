from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import SessionLocal
from app.db.models import Cart, CartItem, Product
from app.schemas.cart import CartItemCreate, CartItem as CartItemOut
from app.api.users import get_current_user

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/", response_model=list[CartItemOut])
def get_cart_items(db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    cart = db.query(Cart).filter(Cart.user_id == current_user.id).first()
    if not cart:
        return []
    return cart.items

@router.post("/items", response_model=CartItemOut, status_code=201)
def add_item_to_cart(item: CartItemCreate, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    cart = db.query(Cart).filter(Cart.user_id == current_user.id).first()
    if not cart:
        cart = Cart(user_id=current_user.id)
        db.add(cart)
        db.commit()
        db.refresh(cart)
    product = db.query(Product).filter(Product.id == item.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    if item.quantity > product.stock:
        raise HTTPException(status_code=400, detail="Insufficient stock")
    cart_item = db.query(CartItem).filter(CartItem.cart_id == cart.id, CartItem.product_id == item.product_id).first()
    if cart_item:
        cart_item.quantity += item.quantity
    else:
        cart_item = CartItem(cart_id=cart.id, product_id=item.product_id, quantity=item.quantity)
        db.add(cart_item)
    db.commit()
    db.refresh(cart_item)
    return cart_item

@router.put("/items/{item_id}", response_model=CartItemOut)
def update_cart_item(item_id: int, quantity: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    cart_item = db.query(CartItem).join(Cart).filter(CartItem.id == item_id, Cart.user_id == current_user.id).first()
    if not cart_item:
        raise HTTPException(status_code=404, detail="Cart item not found")
    if quantity < 1:
        db.delete(cart_item)
        db.commit()
        return {}
    product = db.query(Product).filter(Product.id == cart_item.product_id).first()
    if quantity > product.stock:
        raise HTTPException(status_code=400, detail="Insufficient stock")
    cart_item.quantity = quantity
    db.commit()
    db.refresh(cart_item)
    return cart_item

@router.delete("/items/{item_id}")
def delete_cart_item(item_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    cart_item = db.query(CartItem).join(Cart).filter(CartItem.id == item_id, Cart.user_id == current_user.id).first()
    if not cart_item:
        raise HTTPException(status_code=404, detail="Cart item not found")
    db.delete(cart_item)
    db.commit()
    return {"detail": "Item removed"}
