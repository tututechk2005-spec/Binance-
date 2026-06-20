from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, update
from core.database import get_db
from database.models import User, Notification
from middleware.auth import get_current_user

router = APIRouter()


@router.get("")
async def get_notifications(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    unread_only: bool = False,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = select(Notification).where(Notification.user_id == current_user.id)
    if unread_only:
        query = query.where(Notification.is_read == False)
    total = (await db.execute(select(func.count()).select_from(query.subquery()))).scalar()
    result = await db.execute(
        query.order_by(Notification.created_at.desc())
        .offset((page - 1) * per_page).limit(per_page)
    )
    notifs = result.scalars().all()
    return {
        "notifications": [
            {
                "id": str(n.id), "type": n.notification_type.value,
                "title": n.title, "message": n.message,
                "is_read": n.is_read, "data": n.data, "created_at": n.created_at,
            }
            for n in notifs
        ],
        "total": total, "unread": sum(1 for n in notifs if not n.is_read),
    }


@router.put("/{notification_id}/read")
async def mark_read(
    notification_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    from datetime import datetime, timezone
    await db.execute(
        update(Notification)
        .where(and_(Notification.id == notification_id, Notification.user_id == current_user.id))
        .values(is_read=True, read_at=datetime.now(timezone.utc))
    )
    await db.commit()
    return {"message": "Marked as read."}


@router.put("/read-all")
async def mark_all_read(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    from datetime import datetime, timezone
    await db.execute(
        update(Notification)
        .where(and_(Notification.user_id == current_user.id, Notification.is_read == False))
        .values(is_read=True, read_at=datetime.now(timezone.utc))
    )
    await db.commit()
    return {"message": "All notifications marked as read."}


@router.get("/unread-count")
async def unread_count(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    count = (await db.execute(
        select(func.count()).select_from(Notification)
        .where(and_(Notification.user_id == current_user.id, Notification.is_read == False))
    )).scalar()
    return {"count": count}
