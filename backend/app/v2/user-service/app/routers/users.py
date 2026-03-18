from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from core.database import AsyncSessionLocal
from core.models import User, Role, UserRole
from core.schemas import UserCreate, UserRead, UserUpdate

router = APIRouter(prefix="", tags=["Users"])

@router.get("/health", tags=["Health"])
async def health():
    return {"status": "ok"}

# dependency
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

from core.security import hash_password

@router.post("/", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate, db: AsyncSession = Depends(get_db)):
    user_data = user.model_dump()
    user_data["password"] = hash_password(user_data["password"])
    db_user = User(**user_data)
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user

@router.get("/{user_id}", response_model=UserRead)
async def read_user(user_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.get(User, user_id)
    if not result:
        raise HTTPException(status_code=404, detail="User not found")
    return result

@router.get("/all", response_model=List[UserRead])
async def list_users(status: Optional[str] = None, db: AsyncSession = Depends(get_db)):
    query_str = "SELECT * FROM \"User\""
    params = {}
    if status:
        query_str += " WHERE status = :s"
        params["s"] = status
    result = await db.execute(text(query_str), params)
    return result.mappings().all()

@router.put("/{user_id}", response_model=UserRead)
async def update_user(user_id: int, user: UserUpdate, db: AsyncSession = Depends(get_db)):
    db_user = await db.get(User, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    for var, value in user.model_dump(exclude_unset=True).items():
        setattr(db_user, var, value)
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user

