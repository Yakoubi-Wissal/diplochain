#!/bin/bash
# save as add_psycopg2_final.sh

echo "🔧 Ajout de psycopg2-binary à tous les services..."

cd backend/app/v2

# Liste de tous les services qui ont besoin de psycopg2
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
)

for service in "${services[@]}"; do
    req_file="${service}/requirements.txt"
    if [ -f "$req_file" ]; then
        echo "📝 Mise à jour de $service..."
        
        # Supprimer toute ligne asyncpg ou psycopg2 existante
        sed -i '/asyncpg/d' "$req_file"
        sed -i '/psycopg2/d' "$req_file"
        
        # Ajouter psycopg2-binary
        echo "psycopg2-binary>=2.9.9" >> "$req_file"
        
        # Vérifier le contenu
        echo "   ✅ psycopg2-binary ajouté"
    fi
done

cd ~/diplochain

echo "✅ Tous les requirements.txt ont été mis à jour !"
echo "🚀 Reconstruisez les services avec : docker compose build --no-cache"