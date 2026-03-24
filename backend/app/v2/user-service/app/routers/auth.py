from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from core.database import AsyncSessionLocal
from core.models import User, UserRole, Role
from core.schemas import TokenResponse, UserRead
from core.security import verify_password, create_access_token
from core.dependencies import get_current_user

router = APIRouter(prefix="", tags=["Authentification"])

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

@router.post("/login", response_model=TokenResponse)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(User)
        .options(selectinload(User.roles).selectinload(UserRole.role))
        .where(User.email == form_data.username)
    )
    user = result.scalar_one_or_none()

    pass_match = verify_password(form_data.password, user.password) if user else False
    if not user or not pass_match:
        debug_info = f"User found: {bool(user)}"
        if user:
            debug_info += f", Pass match: {pass_match}"
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Email ou mot de passe incorrect ({debug_info})",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = create_access_token(data={"sub": str(user.id_user)})
    return TokenResponse(access_token=token)

@router.get("/me", response_model=UserRead)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user
