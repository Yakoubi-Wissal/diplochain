#!/bin/bash
# save as fix_async_drivers.sh

echo "🔧 Remplacement de psycopg2 par asyncpg dans tous les services..."

cd backend/app/v2

# Liste de tous les services qui utilisent async engine
services=(
  "admin-dashboard-service"
  "analytics-service"
  "blockchain-service"
  "diploma-service"
  "document-service"
  "entreprise-service"
  "institution-service"
  "notification-service"
  "retry-worker-service"
  "storage-service"
  "student-service"
  "user-service"
  "verification-service"
  "backend"
)

for service in "${services[@]}"; do
    # Gérer le cas spécial du backend qui est à la racine
    if [ "$service" = "backend" ]; then
        req_file="../../requirements.txt"
    else
        req_file="${service}/requirements.txt"
    fi
    
    if [ -f "$req_file" ]; then
        echo "📝 Mise à jour de $service..."
        
        # Sauvegarder
        cp "$req_file" "${req_file}.backup"
        
        # Supprimer toute ligne avec psycopg2
        sed -i '/psycopg2/d' "$req_file"
        
        # Ajouter asyncpg s'il n'existe pas déjà
        if ! grep -q "asyncpg" "$req_file"; then
            echo "asyncpg>=0.29.0" >> "$req_file"
        fi
        
        echo "   ✅ asyncpg ajouté à $service"
    fi
done

cd ~/diplochain

echo "✅ Tous les requirements.txt ont été mis à jour !"
echo "🚀 Reconstruisez maintenant avec : docker compose build --no-cache"