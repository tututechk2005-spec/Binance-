from celery import Celery
from celery.schedules import crontab
from core.config import settings

celery_app = Celery(
    "batpro",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=[
        "tasks.signal_tasks",
        "tasks.trade_tasks",
        "tasks.notification_tasks",
        "tasks.portfolio_tasks",
    ],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    beat_schedule={
        "generate-ai-signals": {
            "task": "tasks.signal_tasks.generate_signals_for_all_pairs",
            "schedule": settings.AI_SIGNAL_INTERVAL_SECONDS,
        },
        "execute-auto-trades": {
            "task": "tasks.trade_tasks.execute_auto_trades",
            "schedule": 30,
        },
        "update-portfolio-values": {
            "task": "tasks.portfolio_tasks.update_all_portfolio_values",
            "schedule": 60,
        },
        "send-daily-reports": {
            "task": "tasks.notification_tasks.send_daily_reports",
            "schedule": crontab(hour=8, minute=0),
        },
        "cleanup-old-logs": {
            "task": "tasks.notification_tasks.cleanup_old_logs",
            "schedule": crontab(hour=0, minute=0),
        },
    },
)
