import hashlib
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.hash import sha256_crypt
from sqlalchemy.orm import Session

from app.config import get_settings
from app.models.user import User
from app.schemas.auth import TokenData

settings = get_settings()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return sha256_crypt.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return sha256_crypt.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt


def decode_token(token: str) -> Optional[TokenData]:
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        email: str = payload.get("sub")
        if email is None:
            return None
        return TokenData(email=email)
    except JWTError:
        return None


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    return db.query(User).filter(User.email == email).first()


def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    user = get_user_by_email(db, email)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


def create_user(db: Session, email: str, hashed_password: str, full_name: Optional[str] = None) -> User:
    user = User(email=email, hashed_password=hashed_password, full_name=full_name)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user