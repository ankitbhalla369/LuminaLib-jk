from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db import get_db
from app.models import User
from app.schemas import UserCreate, UserResponse, UserUpdate, TokenResponse, LoginRequest
from app.auth import hash_password, verify_password, create_token
from app.deps import get_current_user

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/signup", response_model=UserResponse)
async def signup(data: UserCreate, db: AsyncSession = Depends(get_db)):
    r = await db.execute(select(User).where(User.email == data.email))
    if r.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    user = User(email=data.email, hashed_password=hash_password(data.password), full_name=data.full_name)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


@router.post("/login", response_model=TokenResponse)
async def login(data: LoginRequest, db: AsyncSession = Depends(get_db)):
    r = await db.execute(select(User).where(User.email == data.email))
    user = r.scalar_one_or_none()
    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    token = create_token({"sub": str(user.id)})
    return TokenResponse(access_token=token)


@router.get("/me", response_model=UserResponse)
async def me(user: User = Depends(get_current_user)):
    return user


@router.put("/me", response_model=UserResponse)
async def update_profile(data: UserUpdate, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    if data.full_name is not None:
        user.full_name = data.full_name
    await db.commit()
    await db.refresh(user)
    return user


@router.post("/signout")
async def signout():
    return {"message": "Signed out"}
