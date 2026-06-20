from celery import shared_task
from loguru import logger
import asyncio
from datetime import datetime, timezone, timedelta


@shared_task(queue="signals", bind=True, max_retries=3)
def generate_signals_for_all_pairs(self):
    try:
        asyncio.run(_generate_all_signals())
    except Exception as exc:
        logger.error(f"Signal generation task failed: {exc}")
        self.retry(exc=exc, countdown=30)


async def _generate_all_signals():
    from core.database import AsyncSessionLocal
    from sqlalchemy import select, and_
    from database.models import ApiKey, Signal, SignalStatus, SignalType
    from binance.client import BinanceClient
    from ai_engine.signal_generator import SignalGenerator, WATCHED_PAIRS
    from database.models import NetworkType

    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(ApiKey).where(and_(ApiKey.is_active == True, ApiKey.is_verified == True)).limit(1)
        )
        api_key = result.scalar_one_or_none()

        if not api_key:
            logger.warning("No verified API key found for signal generation. Using public endpoints.")
            return

        client = BinanceClient(api_key.encrypted_api_key, api_key.encrypted_secret_key, NetworkType.SPOT_MAINNET)
        generator = SignalGenerator()
        signals_created = 0

        for symbol in WATCHED_PAIRS:
            try:
                klines = await client.get_klines(symbol, "1h", limit=200)
                signal_data = generator.generate_signal(symbol, klines, "1h")
                if signal_data:
                    expires_at = datetime.now(timezone.utc) + timedelta(hours=4)
                    signal = Signal(
                        symbol=signal_data["symbol"],
                        signal_type=signal_data["signal_type"],
                        status=SignalStatus.ACTIVE,
                        confidence_score=signal_data["confidence_score"],
                        entry_price=signal_data["entry_price"],
                        stop_loss=signal_data["stop_loss"],
                        take_profit_1=signal_data.get("take_profit_1"),
                        take_profit_2=signal_data.get("take_profit_2"),
                        take_profit_3=signal_data.get("take_profit_3"),
                        timeframe=signal_data["timeframe"],
                        risk_reward_ratio=signal_data.get("risk_reward_ratio"),
                        indicators=signal_data.get("indicators"),
                        analysis_data=signal_data.get("analysis_data"),
                        market_structure=signal_data.get("market_structure"),
                        trend=signal_data.get("trend"),
                        bos_detected=signal_data.get("bos_detected", False),
                        choch_detected=signal_data.get("choch_detected", False),
                        liquidity_zones=signal_data.get("liquidity_zones"),
                        order_blocks=signal_data.get("order_blocks"),
                        fair_value_gaps=signal_data.get("fair_value_gaps"),
                        smart_money_concepts=signal_data.get("smart_money_concepts"),
                        expires_at=expires_at,
                    )
                    db.add(signal)
                    signals_created += 1
                    logger.info(f"Signal created: {symbol} {signal_data['signal_type']} conf={signal_data['confidence_score']}")
            except Exception as e:
                logger.error(f"Error generating signal for {symbol}: {e}")

        await db.commit()
        logger.info(f"Signal generation complete: {signals_created} signals created.")
