from celery import shared_task
from loguru import logger
import asyncio


@shared_task(queue="trades", bind=True, max_retries=3)
def execute_auto_trades(self):
    try:
        asyncio.run(_execute_auto_trades())
    except Exception as exc:
        logger.error(f"Auto-trade task failed: {exc}")
        self.retry(exc=exc, countdown=15)


async def _execute_auto_trades():
    from core.database import AsyncSessionLocal
    from sqlalchemy import select, and_, func
    from database.models import (
        User, ApiKey, Signal, Trade, SignalStatus, TradeStatus,
        TradeType, OrderType, MarketType
    )
    from binance.client import BinanceClient
    from ai_engine.risk_management import RiskManager
    from datetime import datetime, timezone, date

    async with AsyncSessionLocal() as db:
        users_r = await db.execute(
            select(User).where(and_(User.auto_trading_enabled == True, User.is_active == True))
        )
        users = users_r.scalars().all()

        signals_r = await db.execute(
            select(Signal).where(Signal.status == SignalStatus.ACTIVE)
            .order_by(Signal.confidence_score.desc()).limit(5)
        )
        signals = signals_r.scalars().all()

        if not signals:
            return

        for user in users:
            try:
                key_r = await db.execute(
                    select(ApiKey).where(and_(
                        ApiKey.user_id == user.id,
                        ApiKey.is_active == True,
                        ApiKey.is_verified == True,
                    )).limit(1)
                )
                api_key = key_r.scalar_one_or_none()
                if not api_key:
                    continue

                today_count_r = await db.execute(
                    select(func.count()).select_from(Trade).where(and_(
                        Trade.user_id == user.id,
                        Trade.is_auto_trade == True,
                        Trade.created_at >= datetime.combine(date.today(), datetime.min.time()).replace(tzinfo=timezone.utc),
                    ))
                )
                today_count = today_count_r.scalar() or 0
                if today_count >= (user.max_trades_per_day or 10):
                    logger.info(f"User {user.id} reached max trades for today.")
                    continue

                client = BinanceClient(api_key.encrypted_api_key, api_key.encrypted_secret_key, api_key.network_type)
                risk_mgr = RiskManager(float(user.risk_percent or 1))

                for signal in signals:
                    try:
                        existing_r = await db.execute(
                            select(Trade).where(and_(
                                Trade.user_id == user.id,
                                Trade.signal_id == signal.id,
                                Trade.is_auto_trade == True,
                            ))
                        )
                        if existing_r.scalar_one_or_none():
                            continue

                        ticker = await client.get_ticker_price(signal.symbol)
                        current_price = float(ticker["price"])
                        price_diff = abs(current_price - float(signal.entry_price)) / float(signal.entry_price)
                        if price_diff > 0.005:
                            logger.info(f"Price moved too far for {signal.symbol}, skipping.")
                            continue

                        account_info = await client.get_account_info()
                        balances = account_info.get("balances", [])
                        usdt_balance = next(
                            (float(b["free"]) for b in balances if b["asset"] == "USDT"), 0
                        )
                        if usdt_balance < 10:
                            logger.warning(f"Insufficient USDT for user {user.id}: {usdt_balance}")
                            continue

                        pos_size = risk_mgr.calculate_position_size(
                            usdt_balance, current_price, float(signal.stop_loss)
                        )
                        quantity = pos_size["quantity"]
                        if quantity <= 0:
                            continue

                        order_result = await client.place_order(
                            symbol=signal.symbol,
                            side=signal.signal_type.value,
                            order_type="MARKET",
                            quantity=quantity,
                        )

                        trade = Trade(
                            user_id=user.id,
                            api_key_id=api_key.id,
                            signal_id=signal.id,
                            binance_order_id=str(order_result.get("orderId", "")),
                            symbol=signal.symbol,
                            trade_type=TradeType(signal.signal_type.value),
                            order_type=OrderType.MARKET,
                            market_type=MarketType.SPOT,
                            status=TradeStatus.OPEN,
                            quantity=quantity,
                            entry_price=current_price,
                            stop_loss=signal.stop_loss,
                            take_profit=signal.take_profit_1,
                            is_auto_trade=True,
                            is_testnet="testnet" in api_key.network_type.value,
                            opened_at=datetime.now(timezone.utc),
                        )
                        db.add(trade)
                        logger.info(f"Auto trade placed: {signal.symbol} {signal.signal_type.value} qty={quantity} for user {user.id}")
                    except Exception as e:
                        logger.error(f"Error placing auto trade for {signal.symbol}: {e}")

                await db.commit()
            except Exception as e:
                logger.error(f"Error processing auto trades for user {user.id}: {e}")
