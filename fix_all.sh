#!/bin/bash
# save as fix_all.sh

echo "🔧 Correction de tous les problèmes..."

# 1. Correction du fichier init.sql
echo "📁 Vérification de database/init.sql..."
if [ -d "./database/init.sql" ]; then
    echo "   ⚠️  C'est un dossier, correction..."
    mv ./database/init.sql ./database/init.sql.bak.$(date +%s)
    # Recréer avec votre contenu (vous devrez copier-coller le contenu)
fi

# 2. Ajout de pydantic-settings aux requirements
echo "📝 Mise à jour des requirements.txt..."
cd backend/app/v2
for service in */; do
    req_file="${service}requirements.txt"
    if [ -f "$req_file" ]; then
        if ! grep -q "pydantic-settings" "$req_file"; then
            echo "pydantic-settings>=2.0.0" >> "$req_file"
            echo "   ✅ pydantic-settings ajouté à $service"
        fi
    fi
done
cd ../../..

# 3. Vérification des Dockerfiles
echo "🐳 Vérification des Dockerfiles..."
cd backend/app/v2
for service in */; do
    dockerfile="${service}Dockerfile"
    if [ -f "$dockerfile" ]; then
        # Vérifier que le CMD est correct
        if grep -q "uvicorn main:app" "$dockerfile"; then
            echo "   ✅ $service Dockerfile OK"
        else
            echo "   ⚠️  $service Dockerfile pourrait nécessiter une vérification"
        fi
    fi
done
cd ../../..

echo "✅ Corrections terminées!"
echo "🚀 Lancez: docker compose down && docker compose build --no-cache && docker compose up -d"