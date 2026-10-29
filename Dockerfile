# Una sola imagen para head, workers y gateway.
# Todos los nodos deben usar EXACTAMENTE la misma version de Python y de Ray.
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY src/ ./src/
ENV PYTHONPATH=/app/src
ENV PYTHONUNBUFFERED=1
