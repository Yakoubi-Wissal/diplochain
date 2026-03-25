FROM python:3.12-slim

WORKDIR /app

RUN pip install --no-cache-dir httpx asyncio

COPY app/ ./

CMD ["python", "main.py"]
