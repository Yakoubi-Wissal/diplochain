#!/bin/bash
# save as add_deps.sh

cd backend/app/v2

# Liste des services qui ont besoin de dépendances DB
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
  "pdf-generator-service"
  "qr-validation-service"
)

for service in "${services[@]}"; do
    req_file="${service}/requirements.txt"
    if [ -f "$req_file" ]; then
        echo "📝 Mise à jour de $req_file..."
        
        # Ajouter psycopg2-binary
        if ! grep -q "psycopg2-binary" "$req_file"; then
            echo "psycopg2-binary>=2.9.9" >> "$req_file"
            echo "   ✅ psycopg2-binary ajouté"
        fi
        
        # Ajouter pydantic-settings si manquant
        if ! grep -q "pydantic-settings" "$req_file"; then
            echo "pydantic-settings>=2.0.0" >> "$req_file"
            echo "   ✅ pydantic-settings ajouté"
        fi
    fi
done

echo "✅ Tous les requirements.txt ont été mis à jour !"