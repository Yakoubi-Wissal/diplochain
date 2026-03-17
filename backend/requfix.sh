#!/bin/bash
# save as fix_requirements.sh

cd backend/app/v2

for service in */; do
    req_file="${service}requirements.txt"
    if [ -f "$req_file" ]; then
        if ! grep -q "pydantic-settings" "$req_file"; then
            echo "Ajout de pydantic-settings à $req_file"
            echo "pydantic-settings>=2.0.0" >> "$req_file"
        fi
    fi
done

echo "✅ Requirements mis à jour"