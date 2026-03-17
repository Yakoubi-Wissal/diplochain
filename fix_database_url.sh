#!/bin/bash
echo "🔧 Correction DATABASE_URL : postgresql:// → postgresql+asyncpg://"

for service in admin-dashboard-service analytics-service blockchain-service diploma-service \
               document-service entreprise-service institution-service notification-service \
               retry-worker-service storage-service student-service user-service \
               verification-service backend; do
  
  # Chercher dans .env, core/database.py, config.py, settings.py
  for file in "$service/.env" "$service/app/core/database.py" "$service/app/core/config.py" \
              "$service/app/core/settings.py" "$service/app/config.py"; do
    if [ -f "$file" ]; then
      if grep -q "postgresql://" "$file"; then
        sed -i 's|postgresql://|postgresql+asyncpg://|g' "$file"
        echo "   ✅ $file corrigé"
      fi
    fi
  done

  # Chercher aussi dans docker-compose.yml / .env à la racine
done

# Corriger aussi docker-compose.yml si la DATABASE_URL y est définie
if grep -q "postgresql://" docker-compose.yml 2>/dev/null; then
  sed -i 's|postgresql://|postgresql+asyncpg://|g' docker-compose.yml
  echo "   ✅ docker-compose.yml corrigé"
fi

if grep -q "postgresql://" .env 2>/dev/null; then
  sed -i 's|postgresql://|postgresql+asyncpg://|g' .env
  echo "   ✅ .env racine corrigé"
fi

echo "✅ Done ! Relance : docker compose up -d --force-recreate"
