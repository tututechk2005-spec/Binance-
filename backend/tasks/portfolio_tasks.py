from celery import shared_task
from loguru import logger
import asyncio


@shared_task(queue="signals")
def update_all_portfolio_values():
    asyncio.run(_update_all_portfolio_values())


async def _update_all_portfolio_values():
    from core.database import AsyncSessionLocal
    from sqlalchemy import select, and_
    from database.models import Trade, Position, ApiKey, TradeStatus, User
    from binance.client import BinanceClient
    from datetime import datetime, timezone

    async with AsyncSessionLocal() as db:
        users_r = await db.execute(select(User).where(User.is_active == True))
        users = users_r.scalars().all()

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

                client = BinanceClient(api_key.encrypted_api_key, api_key.encrypted_secret_key, api_key.network_type)

                open_r = await db.execute(
                    select(Trade).where(and_(
                        Trade.user_id == user.id,
                        Trade.status == TradeStatus.OPEN,
                    ))
                )
                open_trades = open_r.scalars().all()

                for trade in open_trades:
                    try:
                        ticker = await client.get_ticker_price(trade.symbol)
                        current_price = float(ticker["price"])
                        entry_price = float(trade.entry_price or 0)
                        quantity = float(trade.quantity)

                        if trade.trade_type.value == "BUY":
                            pnl = (current_price - entry_price) * quantity
                        else:
                            pnl = (entry_price - current_price) * quantity

                        trade.pnl = pnl
                        if entry_price > 0:
                            trade.pnl_percent = (pnl / (entry_price * quantity)) * 100

                        if trade.stop_loss:
                            sl = float(trade.stop_loss)
                            if trade.trade_type.value == "BUY" and current_price <= sl:
                                trade.status = TradeStatus.CLOSED
                                trade.exit_price = current_price
                                trade.closed_at = datetime.now(timezone.utc)
                                logger.info(f"Stop loss triggered: {trade.symbol} at {current_price}")

                            elif trade.trade_type.value == "SELL" and current_price >= sl:
                                trade.status = TradeStatus.CLOSED
                                trade.exit_price = current_price
                                trade.closed_at = datetime.now(timezone.utc)
                                logger.info(f"Stop loss triggered: {trade.symbol} at {current_price}")

                        if trade.take_profit and trade.status == TradeStatus.OPEN:
                            tp = float(trade.take_profit)
                            if trade.trade_type.value == "BUY" and current_price >= tp:
                                trade.status = TradeStatus.CLOSED
                                trade.exit_price = current_price
                                trade.closed_at = datetime.now(timezone.utc)
                                logger.info(f"Take profit hit: {trade.symbol} at {current_price}")

                            elif trade.trade_type.value == "SELL" and current_price <= tp:
                                trade.status = TradeStatus.CLOSED
                                trade.exit_price = current_price
                                trade.closed_at = datetime.now(timezone.utc)
                                logger.info(f"Take profit hit: {trade.symbol} at {current_price}")

                    except Exception as e:
                        logger.error(f"Error updating trade {trade.id}: {e}")

                await db.commit()
            except Exception as e:
                logger.error(f"Error updating portfolio for user {user.id}: {e}")
