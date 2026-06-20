from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc, and_
from typing import Optional
from core.database import get_db
from database.models import User, Trade, Signal, Payment, Subscription, Plan, AuditLog, SystemLog, Notification
from database.models import TradeStatus, SignalStatus, PaymentStatus, UserRole
from middleware.auth import get_current_admin, get_admin_only
import uuid

router = APIRouter()


@router.get("/dashboard")
async def admin_dashboard(
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    total_users = (await db.execute(select(func.count()).select_from(User))).scalar()
    active_users = (await db.execute(select(func.count()).select_from(User).where(User.is_active == True))).scalar()
    total_trades = (await db.execute(select(func.count()).select_from(Trade))).scalar()
    open_trades = (await db.execute(select(func.count()).select_from(Trade).where(Trade.status == TradeStatus.OPEN))).scalar()
    total_signals = (await db.execute(select(func.count()).select_from(Signal))).scalar()
    active_signals = (await db.execute(select(func.count()).select_from(Signal).where(Signal.status == SignalStatus.ACTIVE))).scalar()
    total_revenue = (await db.execute(select(func.sum(Payment.amount)).where(Payment.status == PaymentStatus.COMPLETED))).scalar()
    auto_trading_users = (await db.execute(select(func.count()).select_from(User).where(User.auto_trading_enabled == True))).scalar()

    return {
        "users": {"total": total_users, "active": active_users, "auto_trading": auto_trading_users},
        "trades": {"total": total_trades, "open": open_trades},
        "signals": {"total": total_signals, "active": active_signals},
        "revenue": {"total": round(float(total_revenue or 0), 2), "currency": "USD"},
    }


@router.get("/users")
async def admin_get_users(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    role: Optional[str] = None,
    is_active: Optional[bool] = None,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    query = select(User)
    if search:
        query = query.where((User.email.ilike(f"%{search}%")) | (User.username.ilike(f"%{search}%")))
    if role:
        query = query.where(User.role == role)
    if is_active is not None:
        query = query.where(User.is_active == is_active)

    total = (await db.execute(select(func.count()).select_from(query.subquery()))).scalar()
    query = query.order_by(desc(User.created_at)).offset((page - 1) * per_page).limit(per_page)
    result = await db.execute(query)
    users = result.scalars().all()

    return {
        "users": [
            {
                "id": str(u.id), "username": u.username, "email": u.email,
                "role": u.role.value, "subscription_plan": u.subscription_plan.value if u.subscription_plan else "free",
                "is_active": u.is_active, "is_verified": u.is_verified,
                "auto_trading_enabled": u.auto_trading_enabled,
                "login_count": u.login_count, "created_at": u.created_at, "last_login": u.last_login,
            }
            for u in users
        ],
        "total": total, "page": page, "per_page": per_page,
        "pages": max(1, (total + per_page - 1) // per_page),
    }


@router.put("/users/{user_id}/status")
async def toggle_user_status(
    user_id: str,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    user.is_active = not user.is_active
    await db.commit()
    return {"id": user_id, "is_active": user.is_active}


@router.put("/users/{user_id}/role")
async def change_user_role(
    user_id: str,
    role: str = Query(...),
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_admin_only),
):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    try:
        user.role = UserRole(role)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid role.")
    await db.commit()
    return {"id": user_id, "role": user.role.value}


@router.get("/trades")
async def admin_get_trades(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    user_id: Optional[str] = None,
    symbol: Optional[str] = None,
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    query = select(Trade)
    if user_id:
        query = query.where(Trade.user_id == user_id)
    if symbol:
        query = query.where(Trade.symbol == symbol.upper())
    if status:
        query = query.where(Trade.status == status)
    total = (await db.execute(select(func.count()).select_from(query.subquery()))).scalar()
    query = query.order_by(desc(Trade.created_at)).offset((page - 1) * per_page).limit(per_page)
    result = await db.execute(query)
    trades = result.scalars().all()
    return {
        "trades": [
            {
                "id": str(t.id), "user_id": str(t.user_id), "symbol": t.symbol,
                "trade_type": t.trade_type.value, "status": t.status.value,
                "quantity": float(t.quantity), "entry_price": float(t.entry_price or 0),
                "pnl": float(t.pnl or 0), "is_auto_trade": t.is_auto_trade, "created_at": t.created_at,
            }
            for t in trades
        ],
        "total": total, "page": page, "per_page": per_page,
        "pages": max(1, (total + per_page - 1) // per_page),
    }


@router.get("/signals")
async def admin_get_signals(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    query = select(Signal).order_by(desc(Signal.created_at))
    total = (await db.execute(select(func.count()).select_from(Signal))).scalar()
    result = await db.execute(query.offset((page - 1) * per_page).limit(per_page))
    signals = result.scalars().all()
    return {
        "signals": [
            {
                "id": str(s.id), "symbol": s.symbol, "signal_type": s.signal_type.value,
                "status": s.status.value, "confidence_score": float(s.confidence_score),
                "entry_price": float(s.entry_price), "timeframe": s.timeframe,
                "bos_detected": s.bos_detected, "choch_detected": s.choch_detected,
                "created_at": s.created_at,
            }
            for s in signals
        ],
        "total": total, "page": page, "per_page": per_page,
        "pages": max(1, (total + per_page - 1) // per_page),
    }


@router.get("/payments")
async def admin_get_payments(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    query = select(Payment).order_by(desc(Payment.created_at))
    total = (await db.execute(select(func.count()).select_from(Payment))).scalar()
    result = await db.execute(query.offset((page - 1) * per_page).limit(per_page))
    payments = result.scalars().all()
    return {
        "payments": [
            {
                "id": str(p.id), "user_id": str(p.user_id), "provider": p.provider.value,
                "amount": float(p.amount), "currency": p.currency,
                "status": p.status.value, "created_at": p.created_at,
            }
            for p in payments
        ],
        "total": total, "page": page, "per_page": per_page,
        "pages": max(1, (total + per_page - 1) // per_page),
    }


@router.get("/audit-logs")
async def admin_get_audit_logs(
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    query = select(AuditLog).order_by(desc(AuditLog.created_at))
    total = (await db.execute(select(func.count()).select_from(AuditLog))).scalar()
    result = await db.execute(query.offset((page - 1) * per_page).limit(per_page))
    logs = result.scalars().all()
    return {
        "logs": [
            {
                "id": str(l.id), "user_id": str(l.user_id) if l.user_id else None,
                "action": l.action, "resource": l.resource, "resource_id": l.resource_id,
                "ip_address": l.ip_address, "created_at": l.created_at,
            }
            for l in logs
        ],
        "total": total, "page": page, "per_page": per_page,
        "pages": max(1, (total + per_page - 1) // per_page),
    }


@router.get("/system-logs")
async def admin_get_system_logs(
    level: Optional[str] = None,
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    query = select(SystemLog)
    if level:
        query = query.where(SystemLog.level == level.upper())
    total = (await db.execute(select(func.count()).select_from(query.subquery()))).scalar()
    result = await db.execute(query.order_by(desc(SystemLog.created_at)).offset((page - 1) * per_page).limit(per_page))
    logs = result.scalars().all()
    return {
        "logs": [
            {"id": str(l.id), "level": l.level, "service": l.service, "message": l.message, "created_at": l.created_at}
            for l in logs
        ],
        "total": total, "page": page, "per_page": per_page,
        "pages": max(1, (total + per_page - 1) // per_page),
    }


@router.get("/revenue-analytics")
async def revenue_analytics(
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    from datetime import datetime, timezone, timedelta
    last_30 = datetime.now(timezone.utc) - timedelta(days=30)
    last_7 = datetime.now(timezone.utc) - timedelta(days=7)

    total_r = (await db.execute(select(func.sum(Payment.amount)).where(Payment.status == PaymentStatus.COMPLETED))).scalar()
    last30_r = (await db.execute(select(func.sum(Payment.amount)).where(and_(Payment.status == PaymentStatus.COMPLETED, Payment.created_at >= last_30)))).scalar()
    last7_r = (await db.execute(select(func.sum(Payment.amount)).where(and_(Payment.status == PaymentStatus.COMPLETED, Payment.created_at >= last_7)))).scalar()
    subs_r = (await db.execute(select(func.count()).select_from(Subscription).where(Subscription.status == "active"))).scalar()

    return {
        "total_revenue": round(float(total_r or 0), 2),
        "last_30_days": round(float(last30_r or 0), 2),
        "last_7_days": round(float(last7_r or 0), 2),
        "active_subscriptions": subs_r or 0,
    }
