#!/bin/bash

# 1️⃣ Navigate to backend
cd "$(dirname "$0")"

# 2️⃣ Create venv si pas exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# 3️⃣ Activate venv
source venv/bin/activate

# 4️⃣ Upgrade pip
pip install --upgrade pip

# 5️⃣ Installer requirements
if [ -f "requirements.txt" ]; then
    echo "Installing requirements..."
    pip install -r requirements.txt
fi

# 6️⃣ Check et create __init__.py dans folders importants
for folder in schemas models routers; do
    if [ -d "$folder" ]; then
        if [ ! -f "$folder/__init__.py" ]; then
            echo "Creating __init__.py in $folder"
            touch "$folder/__init__.py"
        fi
    fi
done

# 7️⃣ Lancer FastAPI
echo "Starting FastAPI..."
uvicorn main:app --host 0.0.0.0 --port 8000 --reload