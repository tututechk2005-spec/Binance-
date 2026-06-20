import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from core.database import AsyncSessionLocal, engine, Base
from core.security import get_password_hash
from database.models import User, UserRole, SubscriptionPlan, Plan, Wallet
import uuid


async def seed():
    async with AsyncSessionLocal() as db:
        # Seed plans
        plans = [
            Plan(
                id=uuid.uuid4(),
                name="Free",
                slug="free",
                description="Basic access with limited signals",
                price_monthly=0,
                max_api_keys=1,
                max_auto_trades_per_day=0,
                max_signals_per_day=3,
                features="3 signals/day,Manual trading only,Basic analytics",
            ),
            Plan(
                id=uuid.uuid4(),
                name="Basic",
                slug="basic",
                description="Essential trading tools",
                price_monthly=29.99,
                price_quarterly=79.99,
                price_yearly=299.99,
                max_api_keys=2,
                max_auto_trades_per_day=5,
                max_signals_per_day=20,
                features="20 signals/day,5 auto trades/day,Portfolio tracking,Email alerts",
            ),
            Plan(
                id=uuid.uuid4(),
                name="Pro",
                slug="pro",
                description="Full AI trading power",
                price_monthly=79.99,
                price_quarterly=219.99,
                price_yearly=799.99,
                max_api_keys=5,
                max_auto_trades_per_day=50,
                max_signals_per_day=100,
                features="Unlimited signals,50 auto trades/day,Advanced analytics,Priority support,All indicators,Smart Money Concepts",
            ),
            Plan(
                id=uuid.uuid4(),
                name="Enterprise",
                slug="enterprise",
                description="For professional traders",
                price_monthly=199.99,
                price_quarterly=549.99,
                price_yearly=1999.99,
                max_api_keys=20,
                max_auto_trades_per_day=500,
                max_signals_per_day=1000,
                features="Everything in Pro,Dedicated support,Custom indicators,API access,White-label option",
            ),
        ]
        for plan in plans:
            db.add(plan)

        # Seed admin user
        import os
        admin_email = os.environ.get("ADMIN_EMAIL", "admin@batpro.app")
        admin_password = os.environ.get("ADMIN_PASSWORD", "Admin@123456")
        admin_username = os.environ.get("ADMIN_USERNAME", "admin")

        admin = User(
            id=uuid.uuid4(),
            username=admin_username,
            email=admin_email,
            hashed_password=get_password_hash(admin_password),
            full_name="System Administrator",
            role=UserRole.ADMIN,
            subscription_plan=SubscriptionPlan.ENTERPRISE,
            is_active=True,
            is_verified=True,
            referral_code="ADMIN001",
        )
        db.add(admin)
        await db.flush()

        admin_wallet = Wallet(user_id=admin.id, balance=0, currency="USD")
        db.add(admin_wallet)

        await db.commit()
        print("Database seeded successfully.")
        print(f"Admin: {admin_email} / {admin_password}")


if __name__ == "__main__":
    asyncio.run(seed())
