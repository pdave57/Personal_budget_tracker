from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta

from app.database import get_db
from app.schemas.auth import UserCreate, UserLogin, UserResponse, Token
from app.services.auth_service import (
    get_user_by_email,
    create_user,
    authenticate_user,
    create_access_token,
    get_password_hash,
)
from app.config import get_settings

settings = get_settings()

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    existing_user = get_user_by_email(db, user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    hashed_password = get_password_hash(user_data.password)
    user = create_user(db, user_data.email, hashed_password, user_data.full_name)
    return user


@router.post("/login", response_model=Token)
def login(user_credentials: UserLogin, db: Session = Depends(get_db)):
    user = authenticate_user(db, user_credentials.email, user_credentials.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}