from typing import Generic, List, Type, TypeVar, Optional, Any
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

T = TypeVar("T")

class BaseRepository(Generic[T]):
    def __init__(self, model: Type[T], db: AsyncSession):
        self.model = model
        self.db = db

    async def get(self, id: Any) -> Optional[T]:
        query = select(self.model).where(getattr(self.model, self._get_pk_name()) == id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def list(self, filters: Optional[dict] = None) -> List[T]:
        query = select(self.model)
        if filters:
            for key, value in filters.items():
                query = query.where(getattr(self.model, key) == value)
        result = await self.db.execute(query)
        return result.scalars().all()

    async def create(self, **kwargs) -> T:
        obj = self.model(**kwargs)
        self.db.add(obj)
        await self.db.flush()
        return obj

    async def update(self, id: Any, **kwargs) -> Optional[T]:
        pk_name = self._get_pk_name()
        query = update(self.model).where(getattr(self.model, pk_name) == id).values(**kwargs).returning(self.model)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    def _get_pk_name(self) -> str:
        # Simple heuristic, usually id_... or ..._id
        from sqlalchemy import inspect
        return inspect(self.model).primary_key[0].name
