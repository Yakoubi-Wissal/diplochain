from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class NotificationBase(BaseModel):
    user_id: int
    type_notification: str
    message: str
    status: Optional[str] = "PENDING"

class NotificationCreate(NotificationBase):
    pass

class NotificationRead(NotificationBase):
    id: int
    created_at: datetime
    model_config = {"from_attributes": True}
