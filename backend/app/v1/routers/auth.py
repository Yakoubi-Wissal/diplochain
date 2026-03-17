"""
routers/auth.py — DiploChain
Authentification alignée sur le schéma réel :
  - Recherche uniquement par email (pas de colonne `username`)
  - Vérification password_hash (pas `password`)
  - PK = UUID (pas id_user int)
  - Statut via colonne `statut` de type statut_user
"""

from datetime import datetime
from zoneinfo import ZoneInfo

# timezone for Tunis
TZ_TUNIS = ZoneInfo("Africa/Tunis")

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from core.dependencies import get_current_user
import core.security as security
from database import get_db
from models import User, UserExt, Role, UserRole
from schemas import TokenResponse, UserRead
from routers.users import _to_user_read

router = APIRouter(prefix="/auth", tags=["Authentification"])


@router.post("/login", response_model=TokenResponse,
             summary="Connexion — retourne un JWT Bearer")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
):
    """
    form_data.username = email de l'utilisateur.
    (La table users n'a pas de colonne username.)
    """
    result = await db.execute(
        select(User)
        .options(
            selectinload(User.ext),
            selectinload(User.user_roles).selectinload(UserRole.role)
        )
        .where(User.email == form_data.username)
    )
    user: User | None = result.scalar_one_or_none()

    if not user or not security.verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou mot de passe incorrect",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Extension check
    if not user.ext:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Profil DiploChain manquant pour cet utilisateur.",
        )

    # Vérification du statut via user_ext
    if user.ext.statut_diplochain == "EN_ATTENTE":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Compte en attente de validation. Contactez votre administrateur.",
        )
    if user.ext.statut_diplochain == "SUSPENDU":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Compte suspendu. Contactez votre administrateur.",
        )

    # Mise à jour last_login dans user_ext
    # record in local Tunis time
    # strip tzinfo because column is TIMESTAMP WITHOUT TIME ZONE
    user.ext.last_login = datetime.now(TZ_TUNIS).replace(tzinfo=None)
    await db.commit()
    await db.refresh(user.ext)

    # JWT : sub = id_user (str), role = code du premier rôle trouvé
    primary_role = user.user_roles[0].role if user.user_roles else None
    
    token = security.create_access_token(data={
        "sub": str(user.id_user),
        "role": primary_role.code if primary_role else None,
    })

    return TokenResponse(access_token=token)


@router.get("/me", response_model=UserRead,
            summary="Profil de l'utilisateur connecté")
async def get_me(current_user: User = Depends(get_current_user)):
    return _to_user_read(current_user)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT,
             summary="Déconnexion")
async def logout(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Met à jour derniere_action_audit. Pour une révocation complète, utiliser une blacklist Redis."""
    if current_user.ext:
        current_user.ext.derniere_action_audit = datetime.utcnow()
        await db.commit()
