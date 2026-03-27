from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from typing import Optional

from core.database import AsyncSessionLocal
from core.models import Notification
from core.schemas import NotificationCreate, NotificationRead

router = APIRouter(prefix="", tags=["Notifications"])

async def get_db():
    async with AsyncSessionLocal() as s:
        yield s

@router.get("/health", tags=["Health"])
async def health():
    return {"status": "healthy"}

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=NotificationRead)
async def create_notification(notification: NotificationCreate, db: AsyncSession = Depends(get_db)):
    db_notification = Notification(**notification.model_dump())
    db.add(db_notification)
    await db.commit()
    await db.refresh(db_notification)
    return db_notification

@router.get("/{notification_id}", response_model=NotificationRead)
async def read_notification(notification_id: int, db: AsyncSession = Depends(get_db)):
    notification = await db.get(Notification, notification_id)
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    return notification

@router.get("/user/{user_id}", response_model=list[NotificationRead])
async def get_user_notifications(user_id: int, db: AsyncSession = Depends(get_db)):
    from sqlalchemy import select
    result = await db.execute(
        select(Notification).where(Notification.user_id == user_id)
    )
    return result.scalars().all()
