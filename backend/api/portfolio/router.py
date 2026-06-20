from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from typing import Optional
from core.database import get_db
from database.models import User, ApiKey, Trade, Position, TradeStatus
from middleware.auth import get_current_user
from binance.client import BinanceClient

router = APIRouter()


@router.get("/overview")
async def get_portfolio_overview(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    open_r = await db.execute(
        select(func.count()).select_from(Trade).where(
            and_(Trade.user_id == current_user.id, Trade.status == TradeStatus.OPEN)
        )
    )
    closed_r = await db.execute(
        select(func.count()).select_from(Trade).where(
            and_(Trade.user_id == current_user.id, Trade.status == TradeStatus.CLOSED)
        )
    )
    total_pnl_r = await db.execute(
        select(func.sum(Trade.pnl)).where(
            and_(Trade.user_id == current_user.id, Trade.status == TradeStatus.CLOSED)
        )
    )
    winning_r = await db.execute(
        select(func.count()).select_from(Trade).where(
            and_(Trade.user_id == current_user.id, Trade.pnl > 0, Trade.status == TradeStatus.CLOSED)
        )
    )

    open_count = open_r.scalar() or 0
    closed_count = closed_r.scalar() or 0
    total_pnl = float(total_pnl_r.scalar() or 0)
    winning = winning_r.scalar() or 0
    win_rate = round(winning / closed_count * 100, 2) if closed_count > 0 else 0

    binance_balances = []
    key_r = await db.execute(
        select(ApiKey).where(and_(ApiKey.user_id == current_user.id, ApiKey.is_active == True, ApiKey.is_verified == True))
    )
    api_keys = key_r.scalars().all()

    for key in api_keys[:1]:
        try:
            client = BinanceClient(key.encrypted_api_key, key.encrypted_secret_key, key.network_type)
            balances = await client.get_balance()
            if isinstance(balances, list):
                binance_balances = [
                    b for b in balances
                    if float(b.get("free", 0)) > 0 or float(b.get("locked", 0)) > 0
                ]
        except Exception:
            pass

    return {
        "open_trades": open_count,
        "closed_trades": closed_count,
        "total_pnl": round(total_pnl, 4),
        "win_rate": win_rate,
        "winning_trades": winning,
        "losing_trades": closed_count - winning,
        "binance_balances": binance_balances,
        "auto_trading_enabled": current_user.auto_trading_enabled,
        "risk_percent": current_user.risk_percent,
    }


@router.get("/balances")
async def get_binance_balances(
    key_id: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = select(ApiKey).where(and_(ApiKey.user_id == current_user.id, ApiKey.is_active == True))
    if key_id:
        query = query.where(ApiKey.id == key_id)
    result = await db.execute(query)
    keys = result.scalars().all()

    all_balances = []
    for key in keys:
        try:
            client = BinanceClient(key.encrypted_api_key, key.encrypted_secret_key, key.network_type)
            balances = await client.get_balance()
            if isinstance(balances, list):
                non_zero = [b for b in balances if float(b.get("free", 0)) > 0 or float(b.get("locked", 0)) > 0]
                all_balances.append({"key_label": key.label, "network": key.network_type.value, "balances": non_zero})
        except Exception as e:
            all_balances.append({"key_label": key.label, "network": key.network_type.value, "error": str(e)})

    return all_balances


@router.get("/pnl-history")
async def get_pnl_history(
    days: int = Query(30, ge=1, le=365),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    from datetime import datetime, timezone, timedelta
    from sqlalchemy import cast, Date

    since = datetime.now(timezone.utc) - timedelta(days=days)
    result = await db.execute(
        select(Trade).where(
            and_(
                Trade.user_id == current_user.id,
                Trade.status == TradeStatus.CLOSED,
                Trade.closed_at >= since,
            )
        ).order_by(Trade.closed_at)
    )
    trades = result.scalars().all()

    daily_pnl: dict = {}
    for t in trades:
        if t.closed_at:
            day = t.closed_at.strftime("%Y-%m-%d")
            daily_pnl[day] = daily_pnl.get(day, 0) + float(t.pnl or 0)

    return [{"date": k, "pnl": round(v, 4)} for k, v in sorted(daily_pnl.items())]


@router.get("/performance")
async def get_performance_metrics(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Trade).where(and_(Trade.user_id == current_user.id, Trade.status == TradeStatus.CLOSED))
        .order_by(Trade.closed_at)
    )
    trades = result.scalars().all()

    if not trades:
        return {
            "total_return": 0, "win_rate": 0, "avg_win": 0, "avg_loss": 0,
            "profit_factor": 0, "max_drawdown": 0, "sharpe_ratio": 0,
            "total_trades": 0, "best_trade": 0, "worst_trade": 0,
        }

    pnls = [float(t.pnl or 0) for t in trades]
    wins = [p for p in pnls if p > 0]
    losses = [p for p in pnls if p < 0]

    import numpy as np
    cumulative = np.cumsum(pnls)
    peak = np.maximum.accumulate(cumulative)
    drawdown = (peak - cumulative) / (peak + 1e-10)
    max_dd = float(drawdown.max() * 100) if len(drawdown) > 0 else 0

    return {
        "total_return": round(sum(pnls), 4),
        "total_trades": len(trades),
        "win_rate": round(len(wins) / len(pnls) * 100, 2) if pnls else 0,
        "avg_win": round(sum(wins) / len(wins), 4) if wins else 0,
        "avg_loss": round(sum(losses) / len(losses), 4) if losses else 0,
        "profit_factor": round(sum(wins) / abs(sum(losses)), 2) if losses else 0,
        "max_drawdown": round(max_dd, 2),
        "best_trade": round(max(pnls), 4) if pnls else 0,
        "worst_trade": round(min(pnls), 4) if pnls else 0,
        "sharpe_ratio": round(float(np.mean(pnls) / (np.std(pnls) + 1e-10)), 4),
    }
