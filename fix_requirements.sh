#!/bin/bash
# save as fix_requirements.sh

cd backend/app/v2

for service in */; do
    req_file="${service}requirements.txt"
    if [ -f "$req_file" ]; then
        echo "📝 Vérification de $req_file..."
        if ! grep -q "pydantic-settings" "$req_file"; then
            echo "   ➕ Ajout de pydantic-settings"
            echo "pydantic-settings>=2.0.0" >> "$req_file"
        fi
        if ! grep -q "asyncpg" "$req_file"; then
            echo "   ➕ Ajout de asyncpg (si manquant)"
            echo "asyncpg>=0.29.0" >> "$req_file"
        fi
    fi
done

echo "✅ Requirements mis à jour"