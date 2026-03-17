#!/bin/bash
# save as fix_all_remaining.sh

echo "🔧 Correction de tous les problèmes restants..."

# 1. Ajouter psycopg2-binary à TOUS les services qui en manquent
echo "📦 Ajout de psycopg2-binary aux requirements.txt..."
cd backend/app/v2

for service in */; do
    service=${service%/}
    req_file="${service}/requirements.txt"
    
    if [ -f "$req_file" ]; then
        if ! grep -q "psycopg2" "$req_file"; then
            echo "psycopg2-binary>=2.9.9" >> "$req_file"
            echo "   ✅ psycopg2 ajouté à $service"
        fi
    fi
done

# 2. Créer core/config.py pour institution-service
echo "📝 Création de core/config.py pour institution-service..."
mkdir -p institution-service/app/core
cat > institution-service/app/core/config.py << 'EOF'
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str

    class Config:
        env_file = ".env"

settings = Settings()
EOF
echo "   ✅ core/config.py créé"

# 3. Corriger l'erreur de syntaxe dans documents.py
echo "📝 Correction de documents.py..."
DOCS_FILE="document-service/app/routers/documents.py"
if [ -f "$DOCS_FILE" ]; then
    # Sauvegarder
    cp "$DOCS_FILE" "${DOCS_FILE}.backup"
    # Supprimer la ligne problématique
    sed -i '/from core.schemas import None/d' "$DOCS_FILE"
    echo "   ✅ documents.py corrigé"
fi

cd ../..

echo "✅ Toutes les corrections de code sont terminées !"
echo ""
echo "🚀 ÉTAPE SUIVANTE : Modifier docker-compose.yml"
echo "================================================"
echo ""
echo "Ajoutez ces variables d'environnement dans docker-compose.yml :"
echo ""
echo "1. Pour admin-dashboard-service, entreprise-service, notification-service :"
echo "   environment:"
echo "     - PYTHONPATH=/app"
echo "     - DATABASE_URL=postgresql://diplochain_user:diplochain_pass@postgres:5432/diplochain_db"
echo ""
echo "2. Pour blockchain-service :"
echo "   environment:"
echo "     - PYTHONPATH=/app"
echo "     - DATABASE_URL=postgresql://diplochain_user:diplochain_pass@postgres:5432/diplochain_db"
echo "     - FABRIC_GATEWAY_HOST=fabric-gateway"
echo "     - FABRIC_GATEWAY_PORT=7051"