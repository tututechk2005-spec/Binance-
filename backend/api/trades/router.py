from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, func, and_
from typing import Optional
from core.database import get_db
from database.models import Trade, Position, TradeStatus, MarketType, User, ApiKey
from middleware.auth import get_current_user
from .schemas import TradeResponse, TradeListResponse, CreateTradeRequest, PositionResponse
from binance.client import BinanceClient
from core.security import decrypt_api_key
import uuid

router = APIRouter()


@router.get("", response_model=TradeListResponse)
async def get_trades(
    symbol: Optional[str] = None,
    status: Optional[str] = None,
    market_type: Optional[str] = None,
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = select(Trade).where(Trade.user_id == current_user.id)
    if symbol:
        query = query.where(Trade.symbol == symbol.upper())
    if status:
        query = query.where(Trade.status == status)
    if market_type:
        query = query.where(Trade.market_type == market_type)

    count_q = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_q)).scalar()

    query = query.order_by(desc(Trade.created_at)).offset((page - 1) * per_page).limit(per_page)
    result = await db.execute(query)
    trades = result.scalars().all()

    return TradeListResponse(
        trades=[TradeResponse.model_validate(t) for t in trades],
        total=total, page=page, per_page=per_page,
        pages=max(1, (total + per_page - 1) // per_page),
    )


@router.get("/positions", response_model=list)
async def get_positions(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Position).where(and_(Position.user_id == current_user.id, Position.is_active == True))
    )
    positions = result.scalars().all()
    return [PositionResponse.model_validate(p) for p in positions]


@router.get("/stats")
async def get_trade_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    total_r = await db.execute(select(func.count()).select_from(Trade).where(Trade.user_id == current_user.id))
    open_r = await db.execute(select(func.count()).select_from(Trade).where(and_(Trade.user_id == current_user.id, Trade.status == TradeStatus.OPEN)))
    closed_r = await db.execute(select(func.count()).select_from(Trade).where(and_(Trade.user_id == current_user.id, Trade.status == TradeStatus.CLOSED)))
    pnl_r = await db.execute(select(func.sum(Trade.pnl)).where(and_(Trade.user_id == current_user.id, Trade.status == TradeStatus.CLOSED)))
    winning_r = await db.execute(select(func.count()).select_from(Trade).where(and_(Trade.user_id == current_user.id, Trade.pnl > 0)))

    total = total_r.scalar() or 0
    closed = closed_r.scalar() or 0
    winning = winning_r.scalar() or 0

    return {
        "total_trades": total,
        "open_trades": open_r.scalar() or 0,
        "closed_trades": closed,
        "winning_trades": winning,
        "losing_trades": closed - winning,
        "win_rate": round(winning / closed * 100, 2) if closed > 0 else 0,
        "total_pnl": round(float(pnl_r.scalar() or 0), 4),
    }


@router.post("/close/{trade_id}")
async def close_trade(
    trade_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Trade).where(and_(Trade.id == trade_id, Trade.user_id == current_user.id))
    )
    trade = result.scalar_one_or_none()
    if not trade:
        raise HTTPException(status_code=404, detail="Trade not found.")
    if trade.status != TradeStatus.OPEN:
        raise HTTPException(status_code=400, detail="Trade is not open.")

    if trade.api_key_id:
        key_r = await db.execute(select(ApiKey).where(ApiKey.id == trade.api_key_id))
        api_key = key_r.scalar_one_or_none()
        if api_key:
            try:
                client = BinanceClient(
                    api_key.encrypted_api_key, api_key.encrypted_secret_key, api_key.network_type
                )
                ticker = await client.get_ticker_price(trade.symbol)
                current_price = float(ticker["price"])
                trade.exit_price = current_price
                if trade.entry_price:
                    if trade.trade_type.value == "BUY":
                        trade.pnl = (current_price - float(trade.entry_price)) * float(trade.quantity)
                    else:
                        trade.pnl = (float(trade.entry_price) - current_price) * float(trade.quantity)
                    trade.pnl_percent = (trade.pnl / (float(trade.entry_price) * float(trade.quantity))) * 100
            except Exception:
                pass

    trade.status = TradeStatus.CLOSED
    from datetime import datetime, timezone
    trade.closed_at = datetime.now(timezone.utc)
    await db.commit()
    return {"message": "Trade closed.", "trade_id": str(trade.id)}


@router.get("/{trade_id}", response_model=TradeResponse)
async def get_trade(
    trade_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Trade).where(and_(Trade.id == trade_id, Trade.user_id == current_user.id))
    )
    trade = result.scalar_one_or_none()
    if not trade:
        raise HTTPException(status_code=404, detail="Trade not found.")
    return TradeResponse.model_validate(trade)
