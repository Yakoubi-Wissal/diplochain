#!/bin/bash

# Clean setup for DiploChain microservices

set -e

echo "🟢 Activation de l'environnement virtuel..."
source venv/bin/activate

# Liste des vrais microservices (exclure les dossiers non-services)
services=(
    "api-gateway"
    "user-service"
    "diploma-service"
    "institution-service"
    "student-service"
    "blockchain-service"
    "storage-service"
    "document-service"
    "entreprise-service"
    "notification-service"
    "analytics-service"
    "admin-dashboard-service"
    "verification-service"
    "pdf-generator-service"
    "qr-validation-service"
    "retry-worker-service"
)

# Ports correspondants
declare -A ports=(
    ["api-gateway"]=8000
    ["user-service"]=8001
    ["diploma-service"]=8002
    ["institution-service"]=8003
    ["student-service"]=8004
    ["blockchain-service"]=8005
    ["storage-service"]=8006
    ["document-service"]=8007
    ["entreprise-service"]=8008
    ["notification-service"]=8009
    ["analytics-service"]=8010
    ["admin-dashboard-service"]=8011
    ["verification-service"]=8012
    ["pdf-generator-service"]=8013
    ["qr-validation-service"]=8014
    ["retry-worker-service"]=8015
)

echo "🟢 Installation des dépendances communes..."
pip install fastapi uvicorn[standard] sqlalchemy aiosqlite pydantic-settings python-dotenv

# Installer les requirements de chaque service
for service in "${services[@]}"; do
    req_file="app/v2/$service/requirements.txt"
    if [ -f "$req_file" ]; then
        echo "🟢 Installation des dépendances pour $service..."
        pip install -r "$req_file"
    else
        echo "⚠️  Pas de requirements.txt pour $service"
    fi
done

echo "🟢 Création des fichiers __init__.py..."
find app/v2 -type d -not -path "*/__pycache__*" -not -path "*/venv*" -exec touch {}/__init__.py 2>/dev/null \;

echo "🟢 Démarrage des microservices..."

# Tuer les processus existants sur les ports
for port in "${ports[@]}"; do
    fuser -k "$port"/tcp 2>/dev/null || true
done

# Démarrer chaque service
for service in "${services[@]}"; do
    port="${ports[$service]}"
    service_dir="app/v2/$service"
    
    if [ -d "$service_dir" ] && [ -f "$service_dir/app/main.py" ]; then
        echo "🟢 Démarrage de $service sur le port $port"
        
        # Utiliser cd pour se placer dans le répertoire du service
        # et uvicorn avec le chemin d'import correct (avec des points)
        (cd "$service_dir" && PYTHONPATH=../.. uvicorn app.main:app --reload --port "$port" --host 0.0.0.0) &
        
        # Petit délai entre les démarrages
        sleep 2
    else
        echo "⚠️  Service $service non trouvé ou main.py manquant"
    fi
done

echo ""
echo "✅ Tous les services sont démarrés !"
echo ""
echo "📡 Services disponibles :"
for service in "${services[@]}"; do
    echo "   http://localhost:${ports[$service]}  →  $service"
done
echo ""
echo "📝 Appuyez sur Ctrl+C pour arrêter tous les services"

# Attendre que tous les processus se terminent
wait