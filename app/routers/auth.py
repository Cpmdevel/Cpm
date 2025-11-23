from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import Session, select

from ..db import engine, User
from ..security import create_access_token, hash_password, verify_password, decode_token

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_session():
    with Session(engine) as session:
        yield session


def get_current_user(token: str = Depends(oauth2_scheme), session: Session = Depends(get_session)) -> User:
    email = decode_token(token)
    if not email:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    user = session.exec(select(User).where(User.email == email)).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user


@router.post("/signup")
def signup(email: str, password: str, session: Session = Depends(get_session)):
    exists = session.exec(select(User).where(User.email == email)).first()
    if exists:
        raise HTTPException(status_code=400, detail="Email already registered")
    user = User(email=email, password_hash=hash_password(password))
    session.add(user)
    session.commit()
    return {"ok": True}


@router.post("/login")
def login(email: str, password: str, session: Session = Depends(get_session)):
    user = session.exec(select(User).where(User.email == email)).first()
    if not user or not verify_password(password, user.password_hash):
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    token = create_access_token(subject=user.email)
    return {"access_token": token, "token_type": "bearer"}


@router.post("/vip/activate")
def activate_vip(days: int = 30, current_user: User = Depends(get_current_user), session: Session = Depends(get_session)):
    now = datetime.utcnow()
    # Start from payment moment
    if current_user.vip_expires_at and current_user.vip_expires_at > now:
        # Extend from existing expiry
        start = current_user.vip_expires_at
    else:
        start = now
    current_user.is_vip = True
    current_user.vip_started_at = now
    current_user.vip_expires_at = start + timedelta(days=days)
    session.add(current_user)
    session.commit()
    return {"ok": True, "vip_expires_at": current_user.vip_expires_at}


@router.get("/me")
def me(current_user: User = Depends(get_current_user)):
    return {
        "email": current_user.email,
        "is_vip": current_user.is_vip,
        "vip_started_at": current_user.vip_started_at,
        "vip_expires_at": current_user.vip_expires_at,
    }
