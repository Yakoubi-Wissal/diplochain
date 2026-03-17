#!/bin/bash
# save as add_database_url.sh

cd ~/diplochain

# Sauvegarder docker-compose.yml
cp docker-compose.yml docker-compose.yml.backup.$(date +%s)

# Liste des services qui ont besoin de DATABASE_URL
services=(
  "admin-dashboard-service"
  "entreprise-service"
  "notification-service"
  "retry-worker-service"
  "user-service"
  "institution-service"
  "student-service"
  "diploma-service"
  "document-service"
  "blockchain-service"
  "storage-service"
  "verification-service"
  "analytics-service"
  "backend"
)

echo "🔧 Ajout de DATABASE_URL aux services..."

for service in "${services[@]}"; do
  echo "   📝 Traitement de $service..."
  
  # Utiliser sed pour ajouter DATABASE_URL après PYTHONPATH
  sed -i "/$service:/,/environment:/ {
    /- PYTHONPATH=/a\\
      - DATABASE_URL=postgresql://diplochain_user:diplochain_pass@postgres:5432/diplochain_db
  }" docker-compose.yml
done

echo "✅ Mise à jour terminée !"