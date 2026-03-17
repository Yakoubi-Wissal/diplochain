FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir uvicorn[standard]
RUN pip install --no-cache-dir -r requirements.txt

# Copier tout le contenu du dossier app à la racine
COPY app/ ./

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
