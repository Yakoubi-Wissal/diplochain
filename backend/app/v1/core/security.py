from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from core.config import settings

# use Africa/Tunis timezone for all generated datetimes
TZ_TUNIS = ZoneInfo("Africa/Tunis")

# ── Hachage des mots de passe ─────────────────────────────────────────────────
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    # passlib's verify will trigger a dummy hash when the stored hash is None or
    # otherwise invalid.  In that case the dummy secret is very long (>72 bytes)
    # which can blow up with a `ValueError: password cannot be longer than 72
    # bytes` during tests when a user record has an empty/NULL password.  Guard
    # against it so callers can simply use the helper without worrying about
    # database corruption or missing values.
    if not hashed_password:
        return False
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except ValueError:
        # invalid hash (or bcrypt wrapping bug) could trigger the same error
        # during the internal dummy verification; treat as failed login instead
        return False


# ── JWT ───────────────────────────────────────────────────────────────────────
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    # use localized current time
    expire = datetime.now(TZ_TUNIS) + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

def decode_access_token(token: str) -> Optional[dict]:
    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except JWTError:
        return None
