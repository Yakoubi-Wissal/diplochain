#!/bin/bash
# save as fix_dockerfiles_uvicorn.sh

cd backend/app/v2

for service in */; do
    service=${service%/}
    dockerfile="${service}/Dockerfile"
    
    if [ -f "$dockerfile" ]; then
        echo "🔧 Correction de $dockerfile..."
        
        # Sauvegarder
        cp "$dockerfile" "${dockerfile}.backup"
        
        # Ajouter une vérification explicite de uvicorn
        sed -i '/pip install/i RUN pip install --no-cache-dir uvicorn[standard]' "$dockerfile"
        
        echo "✅ $dockerfile corrigé"
    fi
done

echo "🎉 Tous les Dockerfiles ont été mis à jour !"