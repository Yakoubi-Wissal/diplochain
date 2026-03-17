#!/bin/bash
# save as fix_all_issues.sh

echo "🔧 Correction de tous les problèmes..."

# 1. Remplacer psycopg2-binary par asyncpg dans tous les requirements.txt
echo "📝 Mise à jour des requirements.txt (psycopg2 -> asyncpg)..."
cd backend/app/v2

for service in */; do
    service=${service%/}
    req_file="${service}/requirements.txt"
    
    if [ -f "$req_file" ]; then
        echo "   Traitement de $service..."
        
        # Sauvegarder
        cp "$req_file" "${req_file}.backup"
        
        # Remplacer psycopg2 par asyncpg
        sed -i 's/psycopg2-binary.*/asyncpg>=0.29.0/' "$req_file"
        
        # S'assurer que asyncpg est présent
        if ! grep -q "asyncpg" "$req_file"; then
            echo "asyncpg>=0.29.0" >> "$req_file"
        fi
        
        # Ajouter pydantic-settings si manquant
        if ! grep -q "pydantic-settings" "$req_file"; then
            echo "pydantic-settings>=2.0.0" >> "$req_file"
        fi
    fi
done

cd ../..

# 2. Corriger l'erreur de syntaxe dans documents.py
echo "📝 Correction de documents.py..."
DOCS_FILE="backend/app/v2/document-service/app/routers/documents.py"
if [ -f "$DOCS_FILE" ]; then
    cp "$DOCS_FILE" "${DOCS_FILE}.backup"
    sed -i '/from core.schemas import None/d' "$DOCS_FILE"
    echo "   ✅ documents.py corrigé"
fi

# 3. Créer core/config.py manquant pour institution-service
echo "📝 Création de core/config.py pour institution-service..."
mkdir -p backend/app/v2/institution-service/app/core
cat > backend/app/v2/institution-service/app/core/config.py << 'EOF'
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str

    class Config:
        env_file = ".env"

settings = Settings()
EOF
echo "   ✅ core/config.py créé"

echo "✅ Toutes les corrections sont terminées !"
echo "🚀 N'oubliez pas d'ajouter DATABASE_URL et FABRIC_GATEWAY_* dans docker-compose.yml"