from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import Optional
from core.database import get_db
from database.models import User, ApiKey, NetworkType
from middleware.auth import get_current_user
from core.security import encrypt_api_key, decrypt_api_key
from .schemas import (
    UpdateProfileRequest, ApiKeyCreateRequest, ApiKeyResponse,
    UpdateTradingSettingsRequest
)
from binance.client import BinanceClient
import uuid

router = APIRouter()


@router.get("/profile")
async def get_profile(current_user: User = Depends(get_current_user)):
    return {
        "id": str(current_user.id),
        "username": current_user.username,
        "email": current_user.email,
        "full_name": current_user.full_name,
        "phone": current_user.phone,
        "role": current_user.role.value,
        "subscription_plan": current_user.subscription_plan.value if current_user.subscription_plan else "free",
        "auto_trading_enabled": current_user.auto_trading_enabled,
        "risk_percent": current_user.risk_percent,
        "max_trades_per_day": current_user.max_trades_per_day,
        "country": current_user.country,
        "timezone": current_user.timezone,
        "is_active": current_user.is_active,
        "is_verified": current_user.is_verified,
        "login_count": current_user.login_count,
        "created_at": current_user.created_at,
        "last_login": current_user.last_login,
    }


@router.put("/profile")
async def update_profile(
    payload: UpdateProfileRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if payload.full_name is not None:
        current_user.full_name = payload.full_name
    if payload.phone is not None:
        current_user.phone = payload.phone
    if payload.country is not None:
        current_user.country = payload.country
    if payload.timezone is not None:
        current_user.timezone = payload.timezone
    await db.commit()
    return {"message": "Profile updated successfully."}


@router.put("/trading-settings")
async def update_trading_settings(
    payload: UpdateTradingSettingsRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if payload.auto_trading_enabled is not None:
        current_user.auto_trading_enabled = payload.auto_trading_enabled
    if payload.risk_percent is not None:
        if payload.risk_percent < 0.1 or payload.risk_percent > 5.0:
            raise HTTPException(status_code=400, detail="Risk percent must be between 0.1 and 5.0.")
        current_user.risk_percent = payload.risk_percent
    if payload.max_trades_per_day is not None:
        current_user.max_trades_per_day = payload.max_trades_per_day
    await db.commit()
    return {"message": "Trading settings updated.", "auto_trading_enabled": current_user.auto_trading_enabled}


@router.get("/api-keys", response_model=list)
async def get_api_keys(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(ApiKey).where(ApiKey.user_id == current_user.id))
    keys = result.scalars().all()
    return [
        {
            "id": str(k.id),
            "label": k.label,
            "network_type": k.network_type.value,
            "is_active": k.is_active,
            "is_verified": k.is_verified,
            "permissions": k.permissions,
            "last_used": k.last_used,
            "created_at": k.created_at,
        }
        for k in keys
    ]


@router.post("/api-keys", status_code=201)
async def create_api_key(
    payload: ApiKeyCreateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    network_type = NetworkType(payload.network_type)
    client = BinanceClient(
        encrypt_api_key(payload.api_key),
        encrypt_api_key(payload.secret_key),
        network_type,
    )
    is_valid = False
    try:
        is_valid = await client.validate_credentials()
    except Exception:
        pass

    api_key_obj = ApiKey(
        user_id=current_user.id,
        label=payload.label,
        encrypted_api_key=encrypt_api_key(payload.api_key),
        encrypted_secret_key=encrypt_api_key(payload.secret_key),
        network_type=network_type,
        is_verified=is_valid,
        permissions=payload.permissions or "READ,TRADE",
    )
    db.add(api_key_obj)
    await db.commit()
    await db.refresh(api_key_obj)
    return {
        "id": str(api_key_obj.id),
        "label": api_key_obj.label,
        "network_type": api_key_obj.network_type.value,
        "is_verified": api_key_obj.is_verified,
        "created_at": api_key_obj.created_at,
        "message": "API key saved and validated." if is_valid else "API key saved but validation failed.",
    }


@router.delete("/api-keys/{key_id}")
async def delete_api_key(
    key_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(ApiKey).where(and_(ApiKey.id == key_id, ApiKey.user_id == current_user.id))
    )
    key = result.scalar_one_or_none()
    if not key:
        raise HTTPException(status_code=404, detail="API key not found.")
    await db.delete(key)
    await db.commit()
    return {"message": "API key deleted."}


@router.post("/api-keys/{key_id}/verify")
async def verify_api_key(
    key_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(ApiKey).where(and_(ApiKey.id == key_id, ApiKey.user_id == current_user.id))
    )
    key = result.scalar_one_or_none()
    if not key:
        raise HTTPException(status_code=404, detail="API key not found.")
    client = BinanceClient(key.encrypted_api_key, key.encrypted_secret_key, key.network_type)
    is_valid = await client.validate_credentials()
    key.is_verified = is_valid
    await db.commit()
    return {"is_verified": is_valid, "message": "Valid credentials." if is_valid else "Invalid credentials."}
