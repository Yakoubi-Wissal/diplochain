#!/bin/bash
set -e
ROOT=$(pwd)
SERVICES=$(find backend/app/v2 -maxdepth 2 -name "tests" -type d | cut -d'/' -f1-4 | sort -u)
for service in $SERVICES; do
    echo "---------------------------------------------------"
    echo "Testing $service..."
    echo "---------------------------------------------------"
    cd "$ROOT/$service"
    # Set PYTHONPATH to include service root and its app folder
    export PYTHONPATH=".:$(pwd):$(pwd)/app"
    export DATABASE_URL="sqlite+aiosqlite:///:memory:"
    pytest || echo "Tests failed for $service"
done
