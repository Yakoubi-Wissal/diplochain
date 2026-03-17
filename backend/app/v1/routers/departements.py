from typing import List, Optional
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, ConfigDict
from sqlalchemy.ext.asyncio import AsyncSession

from core.dependencies import get_current_user, require_role
from database import get_db
from models import User, TemplateDepartement
from repositories.template_repository import TemplateRepository

router = APIRouter(prefix="/departements", tags=["Templates Département"])

# ── Schémas ───────────────────────────────────────────────────────────────────

class TemplateCreate(BaseModel):
    nom: str
    departement_id: Optional[int] = None
    institution_id: int
    fichier_jrxml_path: str
    fichier_jasper_path: str
    version: int = 1

class TemplateUpdate(BaseModel):
    nom: Optional[str] = None
    fichier_jrxml_path: Optional[str] = None
    fichier_jasper_path: Optional[str] = None
    version: Optional[int] = None
    is_active: Optional[bool] = None

class TemplateResponse(BaseModel):
    id: int
    nom: str
    departement_id: Optional[int]
    institution_id: int
    fichier_jrxml_path: str
    fichier_jasper_path: str
    version: int
    is_active: bool
    created_by: Optional[int]
    created_at: datetime
    updated_at: Optional[datetime]

    model_config = ConfigDict(from_attributes=True)

# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.get("/", response_model=List[TemplateResponse])
async def list_templates(
    institution_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    repo = TemplateRepository(db)
    
    # Auth-based filtering
    target_inst = institution_id
    if current_user.ext and current_user.ext.institution_id:
         target_inst = current_user.ext.institution_id
    
    return await repo.list_by_institution(target_inst)

@router.post("/", response_model=TemplateResponse, status_code=status.HTTP_201_CREATED)
async def create_template(
    data: TemplateCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("SUPER_ADMIN", "ADMIN_INSTITUTION")),
):
    repo = TemplateRepository(db)
    template = TemplateDepartement(
        nom=data.nom,
        departement_id=data.departement_id,
        institution_id=data.institution_id,
        fichier_jrxml_path=data.fichier_jrxml_path,
        fichier_jasper_path=data.fichier_jasper_path,
        version=data.version,
        created_by=current_user.id_user,
    )
    return await repo.create(template)

@router.get("/{template_id}", response_model=TemplateResponse)
async def get_template(
    template_id: int,
    db: AsyncSession = Depends(get_db)
):
    repo = TemplateRepository(db)
    t = await repo.get_by_id(template_id)
    if not t:
        raise HTTPException(status_code=404, detail="Template introuvable.")
    return t

@router.patch("/{template_id}", response_model=TemplateResponse)
async def update_template(
    template_id: int,
    data: TemplateUpdate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_role("SUPER_ADMIN", "ADMIN_INSTITUTION")),
):
    repo = TemplateRepository(db)
    t = await repo.get_by_id(template_id)
    if not t:
        raise HTTPException(status_code=404, detail="Template introuvable.")

    if data.nom is not None: t.nom = data.nom
    if data.fichier_jrxml_path is not None: t.fichier_jrxml_path = data.fichier_jrxml_path
    if data.fichier_jasper_path is not None: t.fichier_jasper_path = data.fichier_jasper_path
    if data.version is not None: t.version = data.version
    if data.is_active is not None: t.is_active = data.is_active

    await db.commit()
    await db.refresh(t)
    return t
