#!/bin/bash
# save as fix_env.sh

cd ~/diplochain

# Sauvegarder docker-compose.yml
cp docker-compose.yml docker-compose.yml.backup

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
  "api-gateway"
)

for service in "${services[@]}"; do
  echo "🔧 Vérification de $service..."
  
  # Vérifier si DATABASE_URL est déjà présent
  if ! grep -A 5 "$service:" docker-compose.yml | grep -q "DATABASE_URL"; then
    echo "   ➕ Ajout de DATABASE_URL à $service"
    # Cette partie est complexe avec sed, mieux vaut le faire manuellement
  fi
done

echo "✅ Vérification terminée. Éditez docker-compose.yml manuellement pour ajouter les variables manquantes."