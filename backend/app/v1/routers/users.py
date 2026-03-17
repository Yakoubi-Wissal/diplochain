"""
routers/users.py — DiploChain v6.0
Refactored for Core/Extension architecture.
"""

from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from core.dependencies import get_current_user, require_role
from core.security import hash_password
from database import get_db
from models import Role, User, UserExt, UserRole, StatutUserDiploChain
from schemas import UserCreate, UserRead, UserUpdate # Assuming UserRead handles the combined view
from repositories.user_repository import UserRepository

router = APIRouter(prefix="/users", tags=["Utilisateurs"])


# ── Liste ─────────────────────────────────────────────────────────────────────

@router.get("/", response_model=List[UserRead])
async def list_users(
    role_code: Optional[str] = None,
    statut: Optional[StatutUserDiploChain] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("SUPER_ADMIN", "ADMIN_INSTITUTION")),
):
    """Liste des utilisateurs. ADMIN_INSTITUTION ne voit que son institution."""
    query = select(User).options(
        selectinload(User.ext),
        selectinload(User.user_roles).selectinload(UserRole.role)
    ).outerjoin(User.ext)

    # Filtre par institution pour ADMIN_INSTITUTION
    if current_user.ext.institution_id:
        query = query.where(UserExt.institution_id == current_user.ext.institution_id)

    # Filtres optionnels
    if statut:
        query = query.where(UserExt.statut_diplochain == statut)

    if role_code:
        query = query.join(User.user_roles).join(UserRole.role).where(Role.code == role_code)

    result = await db.execute(query.order_by(UserExt.created_at.desc()))
    return [_to_user_read(u) for u in result.scalars().all()]


# ── Création ──────────────────────────────────────────────────────────────────
# UserCreate and logic would need to handle Core/Ext split.
# For now, keeping it minimal to avoid breakages.

# ── Détail ────────────────────────────────────────────────────────────────────

@router.get("/{id_user}", response_model=UserRead)
async def get_user(
    id_user: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("SUPER_ADMIN", "ADMIN_INSTITUTION")),
):
    """Récupère un utilisateur par son ID (Core + Ext)"""
    repo = UserRepository(db)
    user = await repo.get_with_ext(id_user)
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur introuvable.")
    return _to_user_read(user)


# ── Mise à jour ───────────────────────────────────────────────────────────────

@router.patch("/{id_user}", response_model=UserRead)
async def update_user(
    id_user: int,
    data: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("SUPER_ADMIN")),
):
    """Met à jour un utilisateur (champs Core et/ou Ext)"""
    repo = UserRepository(db)
    user = await repo.get_with_ext(id_user)
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur introuvable.")
    
    # apply any provided fields to the core or extension object
    changes = data.model_dump(exclude_none=True)
    if changes:
        for field, value in changes.items():
            # core attributes live on the User model itself
            if hasattr(user, field):
                setattr(user, field, value)
            else:
                # otherwise assume it's an ext field; create ext row if missing
                if user.ext is None:
                    from models import UserExt
                    user.ext = UserExt(user_id=user.id_user)
                setattr(user.ext, field, value)
    
    # persist modifications if any were applied
    await db.commit()
    await db.refresh(user)
    return _to_user_read(user)


# Helper conversion
def _to_user_read(u: User) -> UserRead:
    # This should match your UserRead schema fields
    role_id = u.user_roles[0].role_id if u.user_roles else 0
    
    # Defaults if extension is missing (should not happen for DiploChain users)
    ext = u.ext
    
    return UserRead(
        user_id=u.id_user,
        email=u.email,
        nom=ext.nom if ext else None,
        prenom=ext.prenom if ext else None,
        statut_diplochain=ext.statut_diplochain if ext else StatutUserDiploChain.EN_ATTENTE,
        niveau_acces=ext.niveau_acces if ext else "GLOBAL",
        blockchain_address=ext.blockchain_address if ext else None,
        numero_etudiant=ext.numero_etudiant if ext else None,
        date_naissance=ext.date_naissance if ext else None,
        promotion=ext.promotion if ext else None,
        role_id=role_id,
        institution_id=ext.institution_id if ext else None,
        entreprise_id=ext.entreprise_id if ext else None,
    )
