from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from sqlalchemy.orm import Session

from app.db.database import SessionLocal
from app.db.models import Product, Category
from app.schemas.product import ProductCreate, ProductOut, ProductUpdate

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

from app.api.users import get_current_admin

@router.get("/", response_model=List[ProductOut])
def list_products(category: Optional[str] = Query(None), skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    query = db.query(Product)
    if category:
        query = query.join(Category).filter(Category.name == category)
    products = query.offset(skip).limit(limit).all()
    return products

@router.post("/", response_model=ProductOut)
def create_product(product: ProductCreate, db: Session = Depends(get_db), current_user: dict = Depends(get_current_admin)):
    category = db.query(Category).filter(Category.id == product.category_id).first()
    if category is None:
        raise HTTPException(status_code=400, detail="Invalid category")
    db_product = Product(**product.dict())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

@router.get("/{product_id}", response_model=ProductOut)
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@router.put("/{product_id}", response_model=ProductOut)
def update_product(product_id: int, updates: ProductUpdate, db: Session = Depends(get_db), current_user: dict = Depends(get_current_admin)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    update_data = updates.dict(exclude_unset=True)
    for var, value in update_data.items():
        setattr(product, var, value)
    db.commit()
    db.refresh(product)
    return product

@router.delete("/{product_id}")
def delete_product(product_id: int, db: Session = Depends(get_db), current_user: dict = Depends(get_current_admin)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    db.delete(product)
    db.commit()
    return {"detail": "Product deleted"}
