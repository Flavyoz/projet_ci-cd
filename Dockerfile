# Image du script de traitement (utilisée en production par docker-compose.prod.yml)
FROM python:3.11-slim

WORKDIR /app
# Les logs Python s'affichent tout de suite dans "docker compose logs"
ENV PYTHONUNBUFFERED=1

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY pipeline/ pipeline/

# Par défaut : traitement relancé à intervalle régulier
CMD ["python", "-m", "pipeline.main", "planifier"]
