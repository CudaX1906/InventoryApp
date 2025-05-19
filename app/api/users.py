from fastapi import APIRouter, Depends, HTTPException
from typing import List
from sqlalchemy.orm import Session

from app.db.database import SessionLocal
from app.db.models import User
from app.schemas.user import UserOut
from app.core.security import decode_access_token
from fastapi.security import HTTPAuthorizationCredentials,HTTPBearer

oauth2_scheme = HTTPBearer()

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(token: HTTPAuthorizationCredentials = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(status_code=401, detail="Could not validate credentials")
    payload = decode_access_token(token.credentials)
    if payload is None or payload.get("sub") is None:
        raise credentials_exception
    user = db.query(User).filter(User.email == payload.get("sub")).first()
    if user is None:
        raise credentials_exception
    return user

def get_current_admin(current_user: User = Depends(get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return current_user

@router.get("/me", response_model=UserOut)
def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user

@router.get("/", response_model=List[UserOut])
def read_users(db: Session = Depends(get_db), current_admin: User = Depends(get_current_admin)):
    return db.query(User).all()
