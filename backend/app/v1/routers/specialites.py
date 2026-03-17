from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from core.dependencies import get_current_user, require_role
from database import get_db
from models import User
from repositories.specialite_repository import SpecialiteRepository
from schemas import SpecialiteRead

router = APIRouter(prefix="/specialites", tags=["Spécialités"])

@router.get("/", response_model=List[SpecialiteRead])
async def list_specialites(
    institution_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    repo = SpecialiteRepository(db)
    
    # Logic for filtering
    target_inst = institution_id
    if current_user.ext and current_user.ext.institution_id:
        target_inst = current_user.ext.institution_id
        
    if target_inst:
        specs = await repo.list_by_institution(target_inst)
    else:
        specs = await repo.list()
        
    return [_to_specialite_read(s) for s in specs]

@router.get("/{specialite_id}", response_model=SpecialiteRead)
async def get_specialite(
    specialite_id: str,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    repo = SpecialiteRepository(db)
    s = await repo.get_with_ext(specialite_id)
    if not s:
        raise HTTPException(status_code=404, detail="Spécialité introuvable.")
    return _to_specialite_read(s)

def _to_specialite_read(s) -> SpecialiteRead:
    return SpecialiteRead(
        code_specialite=s.code_specialite,
        designation_specialite=s.designation_specialite,
        nom=s.ext.nom if s.ext else None,
        code_ext=s.ext.code if s.ext else None,
        institution_id=s.ext.institution_id if s.ext else None,
        is_active=s.ext.is_active if s.ext else True,
    )
