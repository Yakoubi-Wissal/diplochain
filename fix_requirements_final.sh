#!/bin/bash
# save as fix_requirements_final.sh

cd backend/app/v2

for service in */; do
    service=${service%/}
    req_file="${service}/requirements.txt"
    
    if [ -f "$req_file" ]; then
        echo "🔧 Correction de $req_file..."
        
        # Sauvegarder une copie
        cp "$req_file" "${req_file}.backup"
        
        # Supprimer les lignes mal formatées et ajouter les bonnes dépendances
        grep -v "pydantic-settings" "$req_file" | grep -v "asyncpg" > "${req_file}.tmp"
        
        # Ajouter les dépendances correctement formatées
        echo "" >> "${req_file}.tmp"
        echo "# Database" >> "${req_file}.tmp"
        echo "asyncpg>=0.29.0" >> "${req_file}.tmp"
        echo "pydantic-settings>=2.0.0" >> "${req_file}.tmp"
        
        # Remplacer le fichier original
        mv "${req_file}.tmp" "$req_file"
        
        echo "✅ $req_file corrigé"
    fi
done

echo "🎉 Tous les requirements.txt ont été corrigés !"