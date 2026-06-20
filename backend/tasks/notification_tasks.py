from celery import shared_task
from loguru import logger
import asyncio


@shared_task(queue="notifications")
def send_daily_reports():
    asyncio.run(_send_daily_reports())


@shared_task(queue="notifications")
def cleanup_old_logs():
    asyncio.run(_cleanup_old_logs())


@shared_task(queue="notifications")
def send_signal_notification(user_id: str, signal_data: dict):
    asyncio.run(_create_notification(
        user_id=user_id,
        title=f"New {signal_data['signal_type']} Signal: {signal_data['symbol']}",
        message=f"Confidence: {signal_data['confidence_score']}% | Entry: {signal_data['entry_price']} | SL: {signal_data['stop_loss']}",
        notification_type="signal",
        data=signal_data,
    ))


@shared_task(queue="notifications")
def send_trade_notification(user_id: str, trade_data: dict):
    asyncio.run(_create_notification(
        user_id=user_id,
        title=f"Trade {trade_data['status'].title()}: {trade_data['symbol']}",
        message=f"PNL: {trade_data.get('pnl', 0)} USDT",
        notification_type="trade",
        data=trade_data,
    ))


async def _create_notification(user_id: str, title: str, message: str, notification_type: str, data: dict = None):
    from core.database import AsyncSessionLocal
    from database.models import Notification, NotificationType
    async with AsyncSessionLocal() as db:
        notif = Notification(
            user_id=user_id,
            notification_type=NotificationType(notification_type),
            title=title,
            message=message,
            data=data,
        )
        db.add(notif)
        await db.commit()
        logger.info(f"Notification created for user {user_id}: {title}")


async def _send_daily_reports():
    from core.database import AsyncSessionLocal
    from sqlalchemy import select, and_, func
    from database.models import User, Trade, TradeStatus
    from datetime import datetime, timezone, timedelta
    async with AsyncSessionLocal() as db:
        yesterday = datetime.now(timezone.utc) - timedelta(days=1)
        users_r = await db.execute(select(User).where(User.is_active == True))
        users = users_r.scalars().all()
        for user in users:
            trades_r = await db.execute(
                select(Trade).where(and_(
                    Trade.user_id == user.id,
                    Trade.status == TradeStatus.CLOSED,
                    Trade.closed_at >= yesterday,
                ))
            )
            trades = trades_r.scalars().all()
            if trades:
                total_pnl = sum(float(t.pnl or 0) for t in trades)
                await _create_notification(
                    user_id=str(user.id),
                    title="Daily Trading Report",
                    message=f"Yesterday: {len(trades)} trades, Total PNL: {round(total_pnl, 4)} USDT",
                    notification_type="system",
                    data={"trades_count": len(trades), "total_pnl": total_pnl},
                )


async def _cleanup_old_logs():
    from core.database import AsyncSessionLocal
    from sqlalchemy import delete
    from database.models import SystemLog, AuditLog
    from datetime import datetime, timezone, timedelta
    cutoff = datetime.now(timezone.utc) - timedelta(days=90)
    async with AsyncSessionLocal() as db:
        await db.execute(delete(SystemLog).where(SystemLog.created_at < cutoff))
        await db.execute(delete(AuditLog).where(AuditLog.created_at < cutoff))
        await db.commit()
    logger.info("Old logs cleaned up.")
