#!/bin/bash

echo "🔄 Switching all services to SQLite for development..."

cd app/v2

for service in */ ; do
    service_name=${service%/}
    
    if [[ "$service_name" == *"__pycache__"* ]] || [[ ! -d "$service_name" ]]; then
        continue
    fi
    
    # Update .env to use SQLite
    cat > "$service_name/.env" << EOF
# SQLite for development
DATABASE_URL=sqlite+aiosqlite:///./${service_name}.db
DEBUG=True

# JWT Configuration
JWT_SECRET_KEY=dev-secret-key-change-in-production
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Service URLs (for local development)
USER_SERVICE_URL=http://localhost:8001
DIPLOMA_SERVICE_URL=http://localhost:8002
INSTITUTION_SERVICE_URL=http://localhost:8003
STUDENT_SERVICE_URL=http://localhost:8004
BLOCKCHAIN_SERVICE_URL=http://localhost:8005
STORAGE_SERVICE_URL=http://localhost:8006
EOF

    echo "  ✅ Updated $service_name to use SQLite"
done

cd ../..

echo ""
echo "✅ All services now configured to use SQLite!"
echo "Run ./setup_backend.sh to start them"