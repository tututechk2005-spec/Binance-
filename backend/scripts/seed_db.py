#!/usr/bin/env python3
"""
Seed script: creates admin user, default plans, and sample data.
Run: docker compose exec api python scripts/seed_db.py
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from core.database import SessionLocal, engine
from core.security import get_password_hash
from database.models import user as user_models
from database.models import payment as payment_models
from database import models as all_models
import uuid
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def seed_admin(db: Session):
    existing = db.query(user_models.User).filter(user_models.User.email == "admin@batpro.app").first()
    if existing:
        logger.info("Admin user already exists.")
        return existing

    admin = user_models.User(
        id=str(uuid.uuid4()),
        username="admin",
        email="admin@batpro.app",
        full_name="Admin User",
        hashed_password=get_password_hash("Admin@123456"),
        role="admin",
        subscription_plan="enterprise",
        is_active=True,
        is_verified=True,
        auto_trading_enabled=False,
        risk_percent=1.0,
        max_trades_per_day=50,
    )
    db.add(admin)
    db.commit()
    logger.info("Admin user created: admin@batpro.app / Admin@123456")
    return admin


def seed_plans(db: Session):
    existing = db.query(payment_models.SubscriptionPlan).count()
    if existing > 0:
        logger.info("Plans already seeded.")
        return

    plans = [
        payment_models.SubscriptionPlan(
            id=str(uuid.uuid4()), name="Free", slug="free", description="Get started with basic features",
            price_monthly=0, max_api_keys=1, max_auto_trades_per_day=0, max_signals_per_day=5
        ),
        payment_models.SubscriptionPlan(
            id=str(uuid.uuid4()), name="Basic", slug="basic", description="Perfect for beginner traders",
            price_monthly=29.99, price_quarterly=79.99, price_yearly=299.99,
            max_api_keys=3, max_auto_trades_per_day=5, max_signals_per_day=50
        ),
        payment_models.SubscriptionPlan(
            id=str(uuid.uuid4()), name="Pro", slug="pro", description="For serious traders",
            price_monthly=79.99, price_quarterly=219.99, price_yearly=799.99,
            max_api_keys=10, max_auto_trades_per_day=25, max_signals_per_day=200
        ),
        payment_models.SubscriptionPlan(
            id=str(uuid.uuid4()), name="Enterprise", slug="enterprise", description="Unlimited everything",
            price_monthly=199.99, price_quarterly=549.99, price_yearly=1999.99,
            max_api_keys=100, max_auto_trades_per_day=1000, max_signals_per_day=10000
        ),
    ]
    db.add_all(plans)
    db.commit()
    logger.info(f"Seeded {len(plans)} subscription plans.")


def main():
    logger.info("Starting database seed...")
    db = SessionLocal()
    try:
        seed_admin(db)
        seed_plans(db)
        logger.info("✅ Seed completed successfully!")
    except Exception as e:
        logger.error(f"Seed failed: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
