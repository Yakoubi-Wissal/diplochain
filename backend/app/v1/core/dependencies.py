"""
core/dependencies.py — DiploChain
Dépendances FastAPI alignées sur le schéma réel (UUID PKs, statut statut_user).
"""

from typing import Callable

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from database import get_db
from models import Institution, User, UserExt, UserRole, Role, InstitutionBlockchainExt
from core.security import decode_access_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    Décode le JWT, charge l'utilisateur avec son rôle (eager load),
    vérifie le statut (colonne `statut` de type statut_user).
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token invalide ou expiré",
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload = decode_access_token(token)
    if not payload:
        raise credentials_exception

    user_id: str = payload.get("sub")
    if not user_id:
        raise credentials_exception

    # PK = id_user (Integer)
    try:
        uid = int(user_id)
    except ValueError:
        raise credentials_exception

    result = await db.execute(
        select(User)
        .options(
            selectinload(User.ext),
            selectinload(User.user_roles).selectinload(UserRole.role)
        )
        .where(User.id_user == uid)
    )
    user = result.scalar_one_or_none()

    if not user:
        raise credentials_exception

    if not user.ext:
         raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Profil DiploChain manquant.",
        )

    if user.ext.statut_diplochain == "SUSPENDU":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Compte suspendu. Contactez votre administrateur.",
        )

    if user.ext.statut_diplochain != "ACTIF":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Compte {user.ext.statut_diplochain.lower()}. Contactez votre administrateur.",
        )

    return user


def require_role(*roles: str) -> Callable:
    """
    Restreint l'accès aux rôles indiqués (valeur du champ `code`).

    Usage:
        Depends(require_role("SUPER_ADMIN"))
        Depends(require_role("SUPER_ADMIN", "ADMIN_INSTITUTION"))
    """
    async def _check(current_user: User = Depends(get_current_user)) -> User:
        user_role_codes = [ur.role.code for ur in current_user.user_roles if ur.role]
        
        if not user_role_codes:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Aucun rôle assigné à ce compte.",
            )
            
        if not any(rc in roles for rc in user_role_codes):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Accès refusé. Rôle(s) requis : {list(roles)}",
            )
        return current_user

    return _check


async def require_active_institution(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Institution:
    """Vérifie que l'utilisateur est rattaché à une institution ACTIVE."""
    if not current_user.ext or current_user.ext.institution_id is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Aucune institution associée à ce compte.",
        )

    result = await db.execute(
        select(Institution)
        .options(selectinload(Institution.blockchain_ext))
        .where(Institution.institution_id == current_user.ext.institution_id)
    )
    institution = result.scalar_one_or_none()

    if not institution or not institution.blockchain_ext or institution.blockchain_ext.status != "ACTIVE":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Institution inactive ou suspendue.",
        )

    return institution


# Shortcuts
require_super_admin = require_role("SUPER_ADMIN")
require_admin_institution = require_role("SUPER_ADMIN", "ADMIN_INSTITUTION")
