from typing import Callable
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from core.database import AsyncSessionLocal
from core.models import User, UserRole, Role
from core.security import decode_access_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/users/auth/login")

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
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

    try:
        uid = int(user_id)
    except ValueError:
        raise credentials_exception

    result = await db.execute(
        select(User)
        .options(selectinload(User.roles).selectinload(UserRole.role))
        .where(User.id_user == uid)
    )
    user = result.scalar_one_or_none()

    if not user:
        raise credentials_exception

    return user

def require_role(*roles: str) -> Callable:
    async def _check(current_user: User = Depends(get_current_user)) -> User:
        user_role_codes = [ur.role.code for ur in current_user.roles if ur.role]
        if not any(rc in roles for rc in user_role_codes):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Accès refusé. Rôle(s) requis : {list(roles)}",
            )
        return current_user
    return _check

require_super_admin = require_role("SUPER_ADMIN")
