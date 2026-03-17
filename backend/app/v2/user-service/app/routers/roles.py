from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from core.database import AsyncSessionLocal
from core.models import Role
from core.schemas import RoleRead, RoleCreate

router = APIRouter(prefix="/users/roles", tags=["Roles"])

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

@router.get("/", response_model=List[RoleRead])
async def list_roles(code: Optional[str] = None, db: AsyncSession = Depends(get_db)):
    query_str = "SELECT * FROM \"ROLE\""
    params = {}
    if code:
        query_str += " WHERE code = :code"
        params["code"] = code
    result = await db.execute(text(query_str), params)
    return result.mappings().all()

@router.post("/", response_model=RoleRead)
async def create_role(role: RoleCreate, db: AsyncSession = Depends(get_db)):
    db_role = Role(code=role.code, label_role=role.label_role, id_cursus=role.id_cursus)
    db.add(db_role)
    await db.commit()
    await db.refresh(db_role)
    return db_role

@router.get("/{id_role}", response_model=RoleRead)
async def get_role(id_role: int, db: AsyncSession = Depends(get_db)):
    r = await db.get(Role, id_role)
    if not r:
        raise HTTPException(status_code=404, detail="Role not found")
    return r

@router.put("/{id_role}", response_model=RoleRead)
async def update_role(id_role: int, role: RoleCreate, db: AsyncSession = Depends(get_db)):
    r = await db.get(Role, id_role)
    if not r:
        raise HTTPException(status_code=404, detail="Role not found")
    for k, v in role.model_dump(exclude_unset=True).items():
        setattr(r, k, v)
    db.add(r)
    await db.commit()
    await db.refresh(r)
    return r
