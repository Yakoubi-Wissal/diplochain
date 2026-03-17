from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class RoleBase(BaseModel):
    code: str
    label_role: Optional[str] = None
    id_cursus: Optional[int]

class RoleCreate(RoleBase):
    pass

class RoleRead(RoleBase):
    id_role: int
    model_config = {"from_attributes": True}

class UserBase(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    status: Optional[str] = None
    revoked: Optional[bool] = False
    expired: Optional[bool] = False

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    status: Optional[str] = None
    revoked: Optional[bool] = None
    expired: Optional[bool] = None

class UserRead(UserBase):
    id_user: int
    token: Optional[str]
    tokentype: Optional[str]
    reset_code: Optional[str]
    verificationtoken_expiration: Optional[datetime]
    reset_code_expiration: Optional[datetime]
    verification_token: Optional[str]
    model_config = {"from_attributes": True}
class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    user_id: Optional[int] = None
