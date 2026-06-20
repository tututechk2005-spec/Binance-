from fastapi import APIRouter, Depends, HTTPException, status, Request, BackgroundTasks
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timezone
from loguru import logger

from core.database import get_db
from core.security import (
    verify_password, get_password_hash,
    create_access_token, create_refresh_token, decode_token
)
from core.redis_client import redis_client
from database.models import User, UserRole, Wallet
from .schemas import (
    RegisterRequest, LoginRequest, TokenResponse,
    RefreshTokenRequest, ChangePasswordRequest, ForgotPasswordRequest, ResetPasswordRequest
)
from middleware.auth import get_current_user
import uuid
import secrets

router = APIRouter()


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(
    payload: RegisterRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(User).where(
        (User.email == payload.email) | (User.username == payload.username)
    ))
    existing = result.scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=400, detail="Email or username already registered.")

    user = User(
        username=payload.username,
        email=payload.email,
        hashed_password=get_password_hash(payload.password),
        full_name=payload.full_name,
        role=UserRole.USER,
        referral_code=secrets.token_urlsafe(8),
    )
    db.add(user)
    await db.flush()

    wallet = Wallet(user_id=user.id, balance=0, currency="USD")
    db.add(wallet)
    await db.commit()
    await db.refresh(user)

    access_token = create_access_token({"sub": str(user.id), "role": user.role.value})
    refresh_token = create_refresh_token({"sub": str(user.id)})
    await redis_client.setex(f"refresh:{user.id}", 60 * 60 * 24 * 30, refresh_token)

    logger.info(f"New user registered: {user.email}")
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        user_id=str(user.id),
        username=user.username,
        email=user.email,
        role=user.role.value,
    )


@router.post("/login", response_model=TokenResponse)
async def login(
    payload: LoginRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(User).where(User.email == payload.email))
    user = result.scalar_one_or_none()

    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password.")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account is disabled.")

    user.last_login = datetime.now(timezone.utc)
    user.login_count = (user.login_count or 0) + 1
    await db.commit()

    access_token = create_access_token({"sub": str(user.id), "role": user.role.value})
    refresh_token = create_refresh_token({"sub": str(user.id)})
    await redis_client.setex(f"refresh:{user.id}", 60 * 60 * 24 * 30, refresh_token)

    logger.info(f"User logged in: {user.email} from {request.client.host}")
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        user_id=str(user.id),
        username=user.username,
        email=user.email,
        role=user.role.value,
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    payload: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db),
):
    try:
        data = decode_token(payload.refresh_token)
        if data.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="Invalid token type.")
        user_id = data.get("sub")
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token.")

    stored = await redis_client.get(f"refresh:{user_id}")
    if not stored or stored != payload.refresh_token:
        raise HTTPException(status_code=401, detail="Refresh token has been revoked.")

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="User not found or inactive.")

    new_access = create_access_token({"sub": str(user.id), "role": user.role.value})
    new_refresh = create_refresh_token({"sub": str(user.id)})
    await redis_client.setex(f"refresh:{user.id}", 60 * 60 * 24 * 30, new_refresh)

    return TokenResponse(
        access_token=new_access,
        refresh_token=new_refresh,
        token_type="bearer",
        user_id=str(user.id),
        username=user.username,
        email=user.email,
        role=user.role.value,
    )


@router.post("/logout")
async def logout(current_user: User = Depends(get_current_user)):
    await redis_client.delete(f"refresh:{current_user.id}")
    logger.info(f"User logged out: {current_user.email}")
    return {"message": "Logged out successfully."}


@router.post("/change-password")
async def change_password(
    payload: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if not verify_password(payload.current_password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="Current password is incorrect.")
    current_user.hashed_password = get_password_hash(payload.new_password)
    await db.commit()
    await redis_client.delete(f"refresh:{current_user.id}")
    return {"message": "Password changed successfully."}


@router.get("/me")
async def get_me(current_user: User = Depends(get_current_user)):
    return {
        "id": str(current_user.id),
        "username": current_user.username,
        "email": current_user.email,
        "full_name": current_user.full_name,
        "role": current_user.role.value,
        "subscription_plan": current_user.subscription_plan.value if current_user.subscription_plan else "free",
        "is_active": current_user.is_active,
        "is_verified": current_user.is_verified,
        "auto_trading_enabled": current_user.auto_trading_enabled,
        "risk_percent": current_user.risk_percent,
        "created_at": current_user.created_at,
        "last_login": current_user.last_login,
    }
