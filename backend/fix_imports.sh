#!/bin/bash

echo "🔧 Fixing import paths and structure..."

cd app/v2

# Fix 1: Create proper __init__.py files in all directories
echo "📁 Creating __init__.py files..."
find . -type d -exec touch {}/__init__.py \;

# Fix 2: Create .env files for each service
echo "🔧 Creating .env files..."
for service in */ ; do
    service_name=${service%/}
    
    # Create service-specific .env
    cat > "$service_name/.env" << EOF
# Database configuration
DATABASE_URL=postgresql://diplochain_user:diplochain_pass@postgres:5432/diplochain_db
POSTGRES_SERVER=postgres
POSTGRES_USER=diplochain_user
POSTGRES_PASSWORD=diplochain_pass
POSTGRES_DB=diplochain_db

# JWT Configuration (for user-service)
JWT_SECRET_KEY=your-secret-key-change-in-production
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Service URLs
USER_SERVICE_URL=http://user-service:8001
DIPLOMA_SERVICE_URL=http://diploma-service:8002
INSTITUTION_SERVICE_URL=http://institution-service:8003
STUDENT_SERVICE_URL=http://student-service:8004
BLOCKCHAIN_SERVICE_URL=http://blockchain-service:8005
STORAGE_SERVICE_URL=http://storage-service:8006

# Hyperledger Fabric (for blockchain-service)
FABRIC_ORG_NAME=org1
FABRIC_CHANNEL_NAME=diplomchannel
FABRIC_CONTRACT_NAME=diplomcontract
FABRIC_MSP_ID=Org1MSP
FABRIC_WALLET_PATH=/app/wallet
FABRIC_CONNECTION_PROFILE=/app/connection-profile.yaml

# Redis (for retry-worker)
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_DB=0

# Debug mode
DEBUG=True
EOF

    echo "  ✅ Created .env for $service_name"
done

# Fix 3: Create config.py for services that need it
echo "🔧 Creating config.py files..."
for service in */ ; do
    service_name=${service%/}
    
    # Create config.py in core directory
    mkdir -p "$service_name/app/core"
    
    cat > "$service_name/app/core/config.py" << 'EOF'
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql://user:pass@localhost:5432/diplochain"
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "user"
    POSTGRES_PASSWORD: str = "pass"
    POSTGRES_DB: str = "diplochain"
    
    # JWT
    JWT_SECRET_KEY: str = "your-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Service URLs
    USER_SERVICE_URL: str = "http://user-service:8001"
    DIPLOMA_SERVICE_URL: str = "http://diploma-service:8002"
    INSTITUTION_SERVICE_URL: str = "http://institution-service:8003"
    STUDENT_SERVICE_URL: str = "http://student-service:8004"
    BLOCKCHAIN_SERVICE_URL: str = "http://blockchain-service:8005"
    STORAGE_SERVICE_URL: str = "http://storage-service:8006"
    
    # Hyperledger Fabric
    FABRIC_ORG_NAME: str = "org1"
    FABRIC_CHANNEL_NAME: str = "diplomchannel"
    FABRIC_CONTRACT_NAME: str = "diplomcontract"
    FABRIC_MSP_ID: str = "Org1MSP"
    FABRIC_WALLET_PATH: str = "/app/wallet"
    FABRIC_CONNECTION_PROFILE: str = "/app/connection-profile.yaml"
    
    # Redis
    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    
    # Debug
    DEBUG: bool = True
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

@lru_cache
def get_settings():
    return Settings()

settings = get_settings()
EOF

    echo "  ✅ Created config.py for $service_name"
done

# Fix 4: Create database.py for services that need it
echo "🔧 Creating database.py files..."
for service in */ ; do
    service_name=${service%/}
    
    cat > "$service_name/app/core/database.py" << 'EOF'
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from .config import settings

# Handle postgresql:// vs postgresql+asyncpg://
database_url = settings.DATABASE_URL
if database_url.startswith("postgresql://"):
    database_url = database_url.replace("postgresql://", "postgresql+asyncpg://", 1)

engine = create_async_engine(
    database_url,
    echo=settings.DEBUG,
    future=True
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

Base = declarative_base()

async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
EOF

    echo "  ✅ Created database.py for $service_name"
done

# Fix 5: Update main.py to use correct imports
echo "🔧 Updating main.py files..."
for service in */ ; do
    service_name=${service%/}
    main_file="$service_name/app/main.py"
    
    if [ -f "$main_file" ]; then
        # Backup original
        cp "$main_file" "$main_file.bak"
        
        # Create new main.py with proper imports
        cat > "$main_file" << EOF
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import engine, Base

# Try to import routers if they exist
try:
    from app.routers import users, auth, roles
except ImportError:
    pass

try:
    from app.routers import diplomas
except ImportError:
    pass

try:
    from app.routers import institutions
except ImportError:
    pass

try:
    from app.routers import students
except ImportError:
    pass

try:
    from app.routers import blockchain
except ImportError:
    pass

try:
    from app.routers import storage
except ImportError:
    pass

try:
    from app.routers import documents
except ImportError:
    pass

try:
    from app.routers import entreprises
except ImportError:
    pass

try:
    from app.routers import notifications
except ImportError:
    pass

try:
    from app.routers import analytics
except ImportError:
    pass

try:
    from app.routers import dashboard
except ImportError:
    pass

try:
    from app.routers import verify
except ImportError:
    pass

app = FastAPI(
    title="${service_name}",
    description="${service_name} for DiploChain",
    version="1.0.0",
    debug=settings.DEBUG
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup():
    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@app.get("/")
async def root():
    return {
        "service": "${service_name}",
        "status": "running",
        "debug": settings.DEBUG
    }

@app.get("/health")
async def health():
    return {"status": "healthy"}

# Include routers if they exist
try:
    app.include_router(users.router, prefix="/users", tags=["users"])
except NameError:
    pass

try:
    app.include_router(auth.router, prefix="/auth", tags=["auth"])
except NameError:
    pass

try:
    app.include_router(roles.router, prefix="/roles", tags=["roles"])
except NameError:
    pass

try:
    app.include_router(diplomas.router, prefix="/diplomas", tags=["diplomas"])
except NameError:
    pass

try:
    app.include_router(institutions.router, prefix="/institutions", tags=["institutions"])
except NameError:
    pass

try:
    app.include_router(students.router, prefix="/students", tags=["students"])
except NameError:
    pass

try:
    app.include_router(blockchain.router, prefix="/blockchain", tags=["blockchain"])
except NameError:
    pass

try:
    app.include_router(storage.router, prefix="/storage", tags=["storage"])
except NameError:
    pass

try:
    app.include_router(documents.router, prefix="/documents", tags=["documents"])
except NameError:
    pass

try:
    app.include_router(entreprises.router, prefix="/entreprises", tags=["entreprises"])
except NameError:
    pass

try:
    app.include_router(notifications.router, prefix="/notifications", tags=["notifications"])
except NameError:
    pass

try:
    app.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
except NameError:
    pass

try:
    app.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])
except NameError:
    pass

try:
    app.include_router(verify.router, prefix="/verify", tags=["verify"])
except NameError:
    pass
EOF

        echo "  ✅ Updated main.py for $service_name"
    fi
done

# Fix 6: Create basic router files where needed
echo "🔧 Creating basic router files..."

# Function to create router
create_router() {
    local service=$1
    local router_name=$2
    local router_file="$service/app/routers/$router_name.py"
    
    if [ ! -f "$router_file" ]; then
        cat > "$router_file" << EOF
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.config import settings

router = APIRouter()

@router.get("/")
async def get_all(db: AsyncSession = Depends(get_db)):
    return {"message": "List of ${router_name}"}

@router.get("/{id}")
async def get_one(id: int, db: AsyncSession = Depends(get_db)):
    return {"message": f"${router_name} {id}"}

@router.post("/")
async def create(db: AsyncSession = Depends(get_db)):
    return {"message": "Create ${router_name}"}

@router.put("/{id}")
async def update(id: int, db: AsyncSession = Depends(get_db)):
    return {"message": f"Update ${router_name} {id}"}

@router.delete("/{id}")
async def delete(id: int, db: AsyncSession = Depends(get_db)):
    return {"message": f"Delete ${router_name} {id}"}
EOF
        echo "  ✅ Created router $router_name for $service"
    fi
}

# Create routers for each service
create_router "user-service" "users"
create_router "user-service" "auth"
create_router "user-service" "roles"
create_router "diploma-service" "diplomas"
create_router "institution-service" "institutions"
create_router "student-service" "students"
create_router "blockchain-service" "blockchain"
create_router "storage-service" "storage"
create_router "document-service" "documents"
create_router "entreprise-service" "entreprises"
create_router "notification-service" "notifications"
create_router "analytics-service" "analytics"
create_router "admin-dashboard-service" "dashboard"
create_router "verification-service" "verify"
create_router "qr-validation-service" "validation"

cd ../..

echo ""
echo "✅ All fixes applied!"
echo ""
echo "Next steps:"
echo "1. Make sure PostgreSQL is running (or use SQLite for testing)"
echo "2. Run: ./setup_backend.sh"
echo "3. Check each service at http://localhost:8001-8015"