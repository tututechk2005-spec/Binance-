from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, func
from typing import Optional, List
from core.database import get_db
from database.models import Signal, SignalType, SignalStatus
from middleware.auth import get_current_user, get_current_admin
from database.models import User
from .schemas import SignalResponse, SignalListResponse
import uuid

router = APIRouter()


@router.get("", response_model=SignalListResponse)
async def get_signals(
    symbol: Optional[str] = None,
    signal_type: Optional[str] = None,
    status: Optional[str] = None,
    timeframe: Optional[str] = None,
    min_confidence: Optional[float] = Query(None, ge=0, le=100),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = select(Signal)
    if symbol:
        query = query.where(Signal.symbol == symbol.upper())
    if signal_type:
        query = query.where(Signal.signal_type == signal_type.upper())
    if status:
        query = query.where(Signal.status == status)
    if timeframe:
        query = query.where(Signal.timeframe == timeframe)
    if min_confidence is not None:
        query = query.where(Signal.confidence_score >= min_confidence)

    count_q = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_q)).scalar()

    query = query.order_by(desc(Signal.created_at)).offset((page - 1) * per_page).limit(per_page)
    result = await db.execute(query)
    signals = result.scalars().all()

    return SignalListResponse(
        signals=[SignalResponse.model_validate(s) for s in signals],
        total=total,
        page=page,
        per_page=per_page,
        pages=max(1, (total + per_page - 1) // per_page),
    )


@router.get("/{signal_id}", response_model=SignalResponse)
async def get_signal(
    signal_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(Signal).where(Signal.id == signal_id))
    signal = result.scalar_one_or_none()
    if not signal:
        raise HTTPException(status_code=404, detail="Signal not found.")
    return SignalResponse.model_validate(signal)


@router.get("/latest/active")
async def get_latest_active_signals(
    limit: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Signal)
        .where(Signal.status == SignalStatus.ACTIVE)
        .order_by(desc(Signal.confidence_score), desc(Signal.created_at))
        .limit(limit)
    )
    signals = result.scalars().all()
    return [SignalResponse.model_validate(s) for s in signals]


@router.get("/stats/summary")
async def get_signal_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    total_r = await db.execute(select(func.count()).select_from(Signal))
    active_r = await db.execute(select(func.count()).select_from(Signal).where(Signal.status == SignalStatus.ACTIVE))
    triggered_r = await db.execute(select(func.count()).select_from(Signal).where(Signal.status == SignalStatus.TRIGGERED))
    buy_r = await db.execute(select(func.count()).select_from(Signal).where(Signal.signal_type == SignalType.BUY))
    sell_r = await db.execute(select(func.count()).select_from(Signal).where(Signal.signal_type == SignalType.SELL))
    avg_conf_r = await db.execute(select(func.avg(Signal.confidence_score)).select_from(Signal))

    return {
        "total_signals": total_r.scalar(),
        "active_signals": active_r.scalar(),
        "triggered_signals": triggered_r.scalar(),
        "buy_signals": buy_r.scalar(),
        "sell_signals": sell_r.scalar(),
        "average_confidence": round(float(avg_conf_r.scalar() or 0), 2),
    }
