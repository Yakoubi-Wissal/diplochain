from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from models import User, UserExt, UserRole, Role
from .base import BaseRepository

class UserRepository(BaseRepository[User]):
    def __init__(self, db: AsyncSession):
        super().__init__(User, db)

    async def get_with_ext(self, user_id: int) -> Optional[User]:
        query = select(User).options(
            selectinload(User.ext),
            selectinload(User.user_roles).selectinload(UserRole.role)
        ).where(User.id_user == user_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> Optional[User]:
        query = select(User).options(
            selectinload(User.ext),
            selectinload(User.user_roles).selectinload(UserRole.role)
        ).where(User.email == email)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def list_by_institution(self, institution_id: int) -> List[User]:
        query = select(User).join(User.ext).options(
            selectinload(User.ext),
            selectinload(User.user_roles).selectinload(UserRole.role)
        ).where(UserExt.institution_id == institution_id)
        result = await self.db.execute(query)
        return result.scalars().all()
