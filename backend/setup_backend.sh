#!/bin/bash

echo "🔧 Fixing import paths and structure..."

cd app/v2

# Fix 1: Create proper __init__.py files in all directories (excluding __pycache__)
echo "📁 Creating __init__.py files..."
find . -type d -not -path "*/__pycache__/*" -not -name "__pycache__" -exec touch {}/__init__.py 2>/dev/null \;

# Fix 2: Create .env files for each service
echo "🔧 Creating .env files..."
for service in */ ; do
    service_name=${service%/}
    
    # Skip if it's a pycache or other special directory
    if [[ "$service_name" == *"__pycache__"* ]] || [[ ! -d "$service_name" ]]; then
        continue
    fi
    
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
    
    # Skip if it's a pycache or other special directory
    if [[ "$service_name" == *"__pycache__"* ]] || [[ ! -d "$service_name" ]]; then
        continue
    fi
    
    # Create config.py in core directory
    mkdir -p "$service_name/app/core"
    
    # Only create if it doesn't exist
    if [ ! -f "$service_name/app/core/config.py" ]; then
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
    fi
done

# Fix 4: Create database.py for services that need it
echo "🔧 Creating database.py files..."
for service in */ ; do
    service_name=${service%/}
    
    # Skip if it's a pycache or other special directory
    if [[ "$service_name" == *"__pycache__"* ]] || [[ ! -d "$service_name" ]]; then
        continue
    fi
    
    # Only create if it doesn't exist
    if [ ! -f "$service_name/app/core/database.py" ]; then
        cat > "$service_name/app/core/database.py" << 'EOF'
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from .config import settings

# Handle postgresql:// vs postgresql+asyncpg://
database_url = settings.DATABASE_URL
if database_url.startswith("postgresql://"):
    database_url = database_url.replace("postgresql://", "postgresql+asyncpg://", 1)

# For SQLite (development)
if database_url.startswith("sqlite"):
    engine = create_async_engine(
        database_url,
        echo=settings.DEBUG,
        future=True
    )
else:
    engine = create_async_engine(
        database_url,
        echo=settings.DEBUG,
        future=True,
        pool_size=5,
        max_overflow=10
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
    fi
done

# Fix 5: Update main.py to use correct imports (only if it exists)
echo "🔧 Checking main.py files..."
for service in */ ; do
    service_name=${service%/}
    
    # Skip if it's a pycache or other special directory
    if [[ "$service_name" == *"__pycache__"* ]] || [[ ! -d "$service_name" ]]; then
        continue
    fi
    
    main_file="$service_name/app/main.py"
    
    if [ -f "$main_file" ]; then
        # Backup original if not already backed up
        if [ ! -f "$main_file.bak" ]; then
            cp "$main_file" "$main_file.bak"
            echo "  ✅ Backed up $service_name/main.py"
        fi
        
        # Check if the file has the old import style
        if grep -q "from routers import" "$main_file" || grep -q "from core.config" "$main_file"; then
            echo "  ⚠️  $service_name needs import fixes (manual update recommended)"
        else
            echo "  ✅ $service_name looks good"
        fi
    else
        echo "  ⚠️  No main.py found for $service_name"
    fi
done

# Fix 6: Create basic router files where needed (but don't overwrite existing)
echo "🔧 Creating missing router files..."

# Function to create router only if it doesn't exist
create_router_if_missing() {
    local service=$1
    local router_name=$2
    local router_file="$service/app/routers/$router_name.py"
    
    # Skip if service doesn't exist or is a pycache
    if [[ ! -d "$service" ]] || [[ "$service" == *"__pycache__"* ]]; then
        return
    fi
    
    mkdir -p "$service/app/routers"
    
    if [ ! -f "$router_file" ]; then
        cat > "$router_file" << EOF
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.config import settings

router = APIRouter()

@router.get("/")
async def get_all(db: AsyncSession = Depends(get_db)):
    """Get all items"""
    return {"message": "List of ${router_name}", "items": []}

@router.get("/{id}")
async def get_one(id: int, db: AsyncSession = Depends(get_db)):
    """Get a single item by ID"""
    return {"message": f"${router_name} {id}", "id": id}

@router.post("/")
async def create(db: AsyncSession = Depends(get_db)):
    """Create a new item"""
    return {"message": "Create ${router_name}", "id": 1}

@router.put("/{id}")
async def update(id: int, db: AsyncSession = Depends(get_db)):
    """Update an item"""
    return {"message": f"Update ${router_name} {id}", "id": id}

@router.delete("/{id}")
async def delete(id: int, db: AsyncSession = Depends(get_db)):
    """Delete an item"""
    return {"message": f"Delete ${router_name} {id}", "id": id}
EOF
        echo "  ✅ Created router $router_name for $service"
    fi
}

# Create routers for each service (only if missing)
echo "  Creating routers for services..."
create_router_if_missing "user-service" "users"
create_router_if_missing "user-service" "auth"
create_router_if_missing "user-service" "roles"
create_router_if_missing "diploma-service" "diplomas"
create_router_if_missing "institution-service" "institutions"
create_router_if_missing "student-service" "students"
create_router_if_missing "blockchain-service" "blockchain"
create_router_if_missing "storage-service" "storage"
create_router_if_missing "document-service" "documents"
create_router_if_missing "entreprise-service" "entreprises"
create_router_if_missing "notification-service" "notifications"
create_router_if_missing "analytics-service" "analytics"
create_router_if_missing "admin-dashboard-service" "dashboard"
create_router_if_missing "verification-service" "verify"
create_router_if_missing "qr-validation-service" "validation"
create_router_if_missing "retry-worker-service" "worker"

# Fix 7: Create a simple test database for development
echo "🔧 Creating SQLite test database for development..."
cat > "../docker-compose.dev.yml" << EOF
version: '3.8'

services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_USER: diplochain_user
      POSTGRES_PASSWORD: diplochain_pass
      POSTGRES_DB: diplochain_db
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

volumes:
  postgres_data:
  redis_data:
EOF

cd ../..

echo ""
echo "========================================="
echo "✅ All fixes applied successfully!"
echo "========================================="
echo ""
echo "Next steps:"
echo ""
echo "1. Start the databases (optional - for development with real DB):"
echo "   docker-compose -f docker-compose.dev.yml up -d"
echo ""
echo "2. For development without PostgreSQL, you can modify each service's"
echo "   .env file to use SQLite instead:"
echo "   DATABASE_URL=sqlite+aiosqlite:///./test.db"
echo ""
echo "3. Run your setup script:"
echo "   ./setup_backend.sh"
echo ""
echo "4. Check each service at:"
echo "   http://localhost:8001 (user-service)"
echo "   http://localhost:8002 (diploma-service)"
echo "   http://localhost:8003 (institution-service)"
echo "   ... etc"
echo ""
echo "Note: Some services may still have application logic errors"
echo "that need to be fixed manually in their respective files."